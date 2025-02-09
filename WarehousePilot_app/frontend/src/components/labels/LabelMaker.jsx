import React, { useState, useEffect } from "react";
import axios from "axios";
import { useParams } from "react-router-dom"; 

const LabelMaker = () => {
  const { picklist_item_id } = useParams(); 
  const [labelData, setLabelData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  useEffect(() => {
    async function fetchLabelData() {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          setError("No authorization token found");
          setLoading(false);
          return;
        }
        const response = await axios.get(
          `${API_BASE_URL}/label_maker/${picklist_item_id}/`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        setLabelData(response.data);
      } catch (err) {
        console.error("Error fetching label data:", err);
        setError("Failed to load label data");
      } finally {
        setLoading(false);
      }
    }

    fetchLabelData();
  }, [picklist_item_id]); 

  if (loading) {
    return <div>Loading Label Data...</div>;
  }

  if (error) {
    return <div style={{ color: "red" }}>{error}</div>;
  }

  if (!labelData) {
    return <div>No label data found.</div>;
  }

  const decodedImageUrl = labelData.SKU_COLOR_IMAGE
    ? decodeURIComponent(labelData.SKU_COLOR_IMAGE).replace(/^\/+/, "")
    : null;
    
  return (
    <div style={{ border: "1px solid #ccc", padding: "16px", maxWidth: "400px" }}>
      <h2 style={{ marginBottom: "1rem" }}>Label Maker</h2>
      <p><strong>SKU COLOR:</strong> {labelData.SKU_COLOR}</p>
      <p><strong>QTY:</strong> {labelData.QTY || "QTY"}</p>
      <p><strong>ORDER NUMBER:</strong> {labelData.ORDER_NUMBER || "ORDER NB"}</p>
      <p><strong>QTY PER BOX:</strong> {labelData.QTY_PER_BOX || "QTY PER BOX"}</p>
      <p><strong>CRATE SIZE:</strong> {labelData.CRATE_SIZE || "CRATE SIZE"}</p>
      <p><strong>PART IMAGE:</strong> {decodedImageUrl ?(
        <img src={decodedImageUrl} alt={decodedImageUrl} style={{ maxWidth: "100%" }} />
      ): ("PART IMAGE")} </p>
      <p><strong>BARCODE:</strong> BARCODE HERE </p>
    </div>
  );
}

export default LabelMaker;
