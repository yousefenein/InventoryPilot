import React, { useState } from "react";
import axios from "axios";
import { Card, CardHeader, CardBody, CardFooter } from "@heroui/card";
import { Tooltip } from "@heroui/tooltip";
import { Divider } from "@heroui/divider";
import SideBar from "../dashboard_sidebar1/App";

const OAInput = () => {
  const [file, setFile] = useState(null);
  const [uploadResponse, setUploadResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploadStartTime, setUploadStartTime] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file before uploading.");
      console.error("❌ No file selected.");
      return;
    }
  
    const formData = new FormData();
    formData.append("file", file);
  
    setLoading(true);
    setError(null);
    setUploadResponse(null);
    setUploadStartTime(Date.now());
    
    // Start a timer to update the elapsed time every second
    const timer = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - uploadStartTime) / 1000));
    }, 1000);
  
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authorization token found");
        console.error("❌ No authorization token found.");
        setLoading(false);
        return;
      }
  
      console.log("📤 Sending file to backend...");
      console.log("🔍 API URL:", `${API_BASE_URL}/oa_input/oa_in/`);
      console.log("🔍 Headers:", {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data",
      });
  
      const response = await axios.post(
        `${API_BASE_URL}/oa_input/oa_in/`, 
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "multipart/form-data",
          },
        }
      );
  
      console.log("✅ Upload successful:", response.data);
      setUploadResponse(response.data);
    } catch (err) {
      console.error("❌ Error uploading file:", err);
      console.error("🔍 Error response:", err.response?.data);
      setError(`Failed to upload file: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
      clearInterval(timer); // Clear the timer when upload completes or fails
    }
  };

  return (
    <div>
    <SideBar/>
    <div className="flex flex-col items-center justify-center h-screen dark:bg-gray-900">
    <Card className="max-w-[1000px] w-full h-[500px] flex flex-col justify-between dark:bg-gray-700">
      <CardHeader className="flex justify-center items-center">
        <p className="text-2xl font-bold text-center">Upload OA Report File</p>
      </CardHeader>
      <Divider />
      <CardBody className="flex flex-col items-center justify-center space-y-4">
        <div className="flex items-center gap-2">
          <input
            type="file"
            accept=".xlsx, .xlsm, .csv"
            onChange={handleFileChange}
            className="border p-2 rounded"
          />
          <Tooltip
            content={
              <div className="text-sm max-w-xs">
                <p><strong>Accepted formats:</strong> .xlsx, .xlsm, .csv</p>
                <p><strong>Required columns with exact names and capitalization:</strong></p>
                <ul className="list-disc list-inside">
                  <li>NoCommande</li>
                  <li>QteAProd</li>
                  <li>NoProd</li>
                  <li>Departement</li>
                  <li>LineUpNo</li>
                  <li>LineupName</li>
                  <li>MaxDate</li>
                  <li>NomClientLiv</li>
                  <li>ProjectType</li>
                  <li>StatutOA</li>
                </ul>
                <p><strong>Note:</strong> Column '275' (material type), 'LOC' (location), 'AREA', and 'MODEL FINAL' are also expected but may be derived from other columns.</p>
                <p>Rows with missing or invalid values may be skipped.</p>
              </div>
            }
            placement="right"
          >
            <span className="text-blue-600 cursor-pointer text-lg">ℹ️</span>
          </Tooltip>
        </div>

        <button
          onClick={handleUpload}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          disabled={loading}
        >
          {loading ? `Uploading... (${elapsedTime}s)` : "Upload"}
        </button>
      </CardBody>
      <Divider />
      <CardFooter className="text-center">
        {error && <p className="text-red-500">{error}</p>}
        {uploadResponse && (
          <div>
            <p className="text-green-500">Upload Successful!</p>
            {uploadResponse.message && <p className="text-sm mt-1">{uploadResponse.message}</p>}
            {uploadResponse.note && <p className="text-xs text-gray-600 mt-1">{uploadResponse.note}</p>}
          </div>
        )}
      </CardFooter>
    </Card>
    </div>
    </div>
  );
};

export default OAInput;
