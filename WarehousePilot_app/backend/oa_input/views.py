from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import pandas as pd
from django.core.files.storage import default_storage
from django.conf import settings
from .models import OAReport 
from  orders.models import Orders, OrderPart
from parts.models import Part
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

class OAInputView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        logger.info(" Received a POST request for file upload.")
        start_time = pd.Timestamp.now()
        logger.info(f" Started processing at: {start_time}")

        if "file" not in request.FILES:
            logger.error(" No file uploaded!")
            return Response({"error": "No file uploaded"}, status=400)

        file = request.FILES["file"]
        file_extension = os.path.splitext(file.name)[1].lower()
        file_path = default_storage.save(f"uploads/{file.name}", file)
        logger.info(f" File saved at: {file_path}")

        try:
            logger.info(f" Detecting file type: {file_extension}")

            if file_extension in [".xlsm", ".xlsx"]:
                df = pd.read_excel(file_path, engine="openpyxl")
            elif file_extension == ".csv":
                df = pd.read_csv(file_path)
            else:
                logger.error(f" Unsupported file format: {file_extension}")
                return Response({"error": f"Unsupported file format: {file_extension}"}, status=400)

            logger.info(f" Successfully loaded file. Shape: {df.shape}")

            # Define required columns and rename them
            COLUMN_MAPPING = {
                "275": "material_type",
                "NoCommande": "order_id",
                "QteAProd": "qty",
                "NoProd": "sku_color",
                "Departement": "department",
                "LineUpNo": "lineup_nb",
                "LineupName": "lineup_name",
                "MaxDate": "due_date",
                "NomClientLiv": "client_name",
                "ProjectType": "project_type",
                "LOC": "location",
                "AREA": "area",
                "MODEL FINAL": "final_model",
                "StatutOA": "importance"
            }

            # Check if required columns exist
            missing_columns = [col for col in COLUMN_MAPPING.keys() if col not in df.columns]
            if missing_columns:
                logger.warning(f" Missing columns in uploaded file (proceeding anyway): {missing_columns}")
                # Add missing columns with default values
                for col in missing_columns:
                    if col == '275':
                        # Try to derive material type from Departement
                        if 'Departement' in df.columns:
                            df[col] = df['Departement'].apply(lambda x: str(x).split()[0] if isinstance(x, str) and ' ' in str(x) else '')
                        else:
                            df[col] = ''
                    elif col == 'LOC':
                        df[col] = ''  # Default empty location
                    elif col == 'AREA':
                        df[col] = ''  # Default empty area
                    elif col == 'MODEL FINAL':
                        df[col] = 'standard'  # Default model
                    elif col == 'LineupName':
                        # Try to derive from LineUpNo if it exists
                        if 'LineUpNo' in df.columns:
                            df[col] = df['LineUpNo'].apply(lambda x: f"Lineup {x}" if x else "")
                        else:
                            df[col] = ''
                    else:
                        df[col] = ''

            available_columns = [col for col in COLUMN_MAPPING.keys() if col in df.columns]
            df = df[available_columns].rename(columns=COLUMN_MAPPING)
            logger.info(f" Columns after renaming: {list(df.columns)}")

            # Clean and validate all columns before anything else - Optimized
            # Only process essential columns for validation
            essential_columns = ['order_id', 'sku_color', 'qty', 'due_date']
            
            # Convert data types efficiently by only operating on required columns
            if 'order_id' in df.columns:
                df["order_id"] = pd.to_numeric(df["order_id"], errors="coerce")
            if 'due_date' in df.columns:
                df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce")
            if 'qty' in df.columns:
                df["qty"] = pd.to_numeric(df["qty"], errors="coerce")
                
            # Only drop rows where essential data is missing, keep other rows even if they have some missing fields
            original_count = df.shape[0]
            df = df.dropna(subset=[col for col in essential_columns if col in df.columns])
            removed_count = original_count - df.shape[0]
            logger.info(f" Removed {removed_count} invalid/missing rows. Remaining: {df.shape[0]}")

            # Insert Orders into `Orders` Table - Optimized batch processing
            unique_orders = df[['order_id', 'due_date', 'client_name', 'project_type']].drop_duplicates()
            
            # Get all existing order IDs in a single query to avoid repeated database lookups
            existing_order_ids = set(Orders.objects.filter(
                order_id__in=unique_orders['order_id'].tolist()
            ).values_list('order_id', flat=True))
            
            # Create new orders that don't exist in the database
            new_orders = [
                Orders(
                    order_id=order['order_id'],
                    due_date=order['due_date'],
                    customer_name=order['client_name'],
                    project_type=order['project_type'],
                    status="Not Started"  # Default status
                )
                for _, order in unique_orders.iterrows()
                if order['order_id'] not in existing_order_ids
            ]

            if new_orders:
                Orders.objects.bulk_create(new_orders)
                logger.info(f" Inserted {len(new_orders)} new orders.")

            # Insert Parts into `OrderPart` Table
            new_parts = []
            
            # Prepare data for bulk processing
            unique_order_ids = df['order_id'].unique()
            orders_dict = {order.order_id: order for order in Orders.objects.filter(order_id__in=unique_order_ids)}
            
            # Extract all unique SKUs from the dataframe for batch lookup
            unique_skus = df['sku_color'].apply(lambda x: str(x).strip().upper()).unique()
            parts_dict = {part.sku_color.upper(): part for part in Part.objects.filter(sku_color__in=unique_skus)}
            
            # Get existing order parts to avoid duplicates (batch query)
            existing_order_parts = set()
            for op in OrderPart.objects.filter(order_id__in=orders_dict.values()):
                key = (op.order_id.order_id, op.sku_color.sku_color.upper(), op.final_model)
                existing_order_parts.add(key)
            
            # Process in batches of 1000 rows for large files
            batch_size = 1000
            total_rows = len(df)
            skipped_skus = 0
            skipped_duplicates = 0
            
            for i in range(0, total_rows, batch_size):
                batch_df = df.iloc[i:min(i+batch_size, total_rows)]
                
                for _, row in batch_df.iterrows():
                    order_id = row['order_id']
                    if order_id not in orders_dict:
                        continue
                        
                    order = orders_dict[order_id]
                    normalized_sku = str(row["sku_color"]).strip().upper()
                    
                    if normalized_sku not in parts_dict:
                        # If the part doesn't exist in our dictionary, we can try a direct query
                        # This handles potential cases where new parts were added since we loaded our dictionary
                        try:
                            part = Part.objects.get(sku_color__iexact=normalized_sku)
                            # Update the dictionary for future lookups
                            parts_dict[normalized_sku] = part
                        except Part.DoesNotExist:
                            skipped_skus += 1
                            if skipped_skus <= 10:  # Limit logging to avoid overwhelming logs
                                logger.error(f" Part with SKU '{normalized_sku}' does not exist. Skipping entry.")
                            continue
                        
                    part = parts_dict[normalized_sku]
                    
                    # Check if this combination already exists using our pre-populated set
                    key = (order_id, normalized_sku, row["final_model"])
                    if key in existing_order_parts:
                        skipped_duplicates += 1
                        continue
                        
                    new_parts.append(OrderPart(
                        order_id=order,
                        sku_color=part,  
                        qty=row["qty"],
                        location=row["location"],
                        area=row["area"],
                        final_model=row["final_model"],
                        material_type=row["material_type"],
                        department=row["department"],
                        lineup_nb=row["lineup_nb"],
                        lineup_name=row["lineup_name"],
                        status=False,  # Default status
                        importance=row["importance"]
                    ))
                    
                # Create parts in batches to avoid memory issues
                if len(new_parts) >= 5000:
                    # Use ignore_conflicts to handle duplicate keys gracefully
                    OrderPart.objects.bulk_create(new_parts, ignore_conflicts=True)
                    logger.info(f" Inserted batch of {len(new_parts)} order parts.")
                    new_parts = []
                    
            # Log summary of skipped items
            if skipped_skus > 0:
                logger.warning(f" Skipped {skipped_skus} entries due to missing SKUs in the parts database.")
            if skipped_duplicates > 0:
                logger.info(f" Skipped {skipped_duplicates} duplicate entries that already exist in the database.")

            # Process remaining parts in the last batch
            total_parts_created = 0
            if new_parts:
                # Use ignore_conflicts to handle duplicate keys gracefully
                OrderPart.objects.bulk_create(new_parts, ignore_conflicts=True)
                total_parts_created = len(new_parts)
                logger.info(f" Inserted final batch of {len(new_parts)} order parts.")

            # Performance metrics
            end_time = pd.Timestamp.now()
            processing_time = (end_time - start_time).total_seconds()
            
            #  Delete the uploaded file after processing
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f" Deleted uploaded file: {file_path}")

            return Response({
                "message": f"File processed in {processing_time:.2f} seconds. {len(new_orders)} new orders and {total_parts_created} parts inserted.",
                "note": f"Missing columns skipped: {missing_columns}" if missing_columns else "All columns were present."
            }, status=201)
        
        except Exception as e:
            logger.error(f" Error processing file: {e}")
            import traceback
            logger.error(f" Traceback: {traceback.format_exc()}")
            
            # Calculate processing time even for errors
            end_time = pd.Timestamp.now()
            try:
                # Safer way to calculate processing time
                processing_time = (end_time - start_time).total_seconds()
                logger.info(f" Failed after {processing_time:.2f} seconds")
            except:
                logger.info(f" Processing failed at {end_time}")

            # Delete file if an error occurs
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f" Deleted uploaded file due to error: {file_path}")

            return Response({"error": str(e)}, status=400)
