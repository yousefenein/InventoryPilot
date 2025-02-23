from django.db import models

class InventoryPicklistItem(models.Model):
    # Define the fields for your model
    status = models.BooleanField(default=False)  # True for accurate picks, False for inaccurate picks
    # Add other fields as needed, for example:
    # item_name = models.CharField(max_length=255)
    # picker_name = models.CharField(max_length=255)
    # timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pick List Item {self.id} - {'Accurate' if self.status else 'Inaccurate'}"