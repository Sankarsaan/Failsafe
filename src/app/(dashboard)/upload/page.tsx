"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { UploadCloud, File, AlertCircle, CheckCircle2 } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { uploadCSVAction } from "@/actions/upload";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === "text/csv" || droppedFile.name.endsWith(".csv")) {
        setFile(droppedFile);
        setUploadStatus("idle");
        setErrorMessage("");
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setUploadStatus("idle");
      setErrorMessage("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploadStatus("uploading");
    setErrorMessage("");

    try {
      // Basic Frontend Validation
      const text = await file.text();
      const lines = text.split('\n').filter(line => line.trim() !== "");
      if (lines.length > 0) {
        const headers = lines[0].toLowerCase().split(',');
        const courseIdIndex = headers.findIndex(h => h.trim() === 'course_id');
        
        if (courseIdIndex === -1) {
          throw new Error("Missing 'course_id' column in the CSV headers.");
        }
        
        if (lines.length > 1) {
          const firstRow = lines[1].split(',');
          if (firstRow.length > courseIdIndex) {
            const firstCourseId = firstRow[courseIdIndex].trim();
            const pattern = /^(cs|ma|ee|da|me|ce|cl)\d{3}$/i;
            if (!pattern.test(firstCourseId)) {
               throw new Error(`Invalid course format detected ('${firstCourseId}'). Must match department prefix (e.g. CS, MA, EE) followed by 3 digits (case-insensitive).`);
            }
          }
        }
      }

      const formData = new FormData();
      formData.append("file", file);

      const result = await uploadCSVAction(formData);
      
      if (result.error) {
        throw new Error(result.error);
      }

      setUploadStatus("success");
      setFile(null); // Clear after success
    } catch (error: any) {
      console.error(error);
      setErrorMessage(error.message || "There was a problem processing your file.");
      setUploadStatus("error");
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Upload Data</h1>
        <p className="text-muted-foreground mt-1">Upload student performance data (CSV) to update the ML model.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>CSV Data Upload</CardTitle>
          <CardDescription>
            Your CSV must contain a course_id column followed by student data. The Course ID must match your department prefix followed by 3 digits (e.g., CS201, cs201 — case-insensitive).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-10 flex flex-col items-center justify-center transition-colors ${
              isDragging ? "border-primary bg-primary/5" : "border-slate-300 bg-slate-50"
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <UploadCloud className={`w-12 h-12 mb-4 ${isDragging ? "text-primary" : "text-slate-400"}`} />
            <p className="text-sm font-medium text-slate-700 mb-1">
              Drag & drop a file here, or click to select
            </p>
            <p className="text-xs text-slate-500 mb-4">Supported formats: CSV (Max 10MB)</p>
            <div>
              <Button 
                type="button" 
                variant="outline"
                onClick={() => document.getElementById('csv-upload-input')?.click()}
              >
                Browse Files
              </Button>
              <input
                id="csv-upload-input"
                type="file"
                className="hidden"
                accept=".csv"
                onChange={handleFileChange}
              />
            </div>
          </div>

          {file && (
            <div className="mt-4 p-3 border rounded-md flex items-center gap-3 bg-white">
              <File className="w-5 h-5 text-blue-500" />
              <div className="flex-1 text-sm overflow-hidden">
                <p className="font-medium truncate">{file.name}</p>
                <p className="text-slate-500 text-xs">{(file.size / 1024).toFixed(1)} KB</p>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setFile(null)}>Remove</Button>
            </div>
          )}

          {uploadStatus === "success" && (
            <Alert className="mt-4 bg-emerald-50 border-emerald-200">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              <AlertTitle className="text-emerald-800">Upload Successful</AlertTitle>
              <AlertDescription className="text-emerald-700">
                The data has been processed and the ML pipeline has been updated.
              </AlertDescription>
            </Alert>
          )}

          {uploadStatus === "error" && (
            <Alert variant="destructive" className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Upload Failed</AlertTitle>
              <AlertDescription>
                {errorMessage}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
        <CardFooter className="flex justify-end border-t pt-4">
          <Button 
            onClick={handleUpload} 
            disabled={!file || uploadStatus === "uploading"}
            className="w-full sm:w-auto"
          >
            {uploadStatus === "uploading" ? "Uploading..." : "Upload and Process"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
