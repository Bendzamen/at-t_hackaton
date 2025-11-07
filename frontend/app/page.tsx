'use client';

import type React from 'react';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Upload, CheckCircle, Loader2 } from 'lucide-react';

export default function FileUploadPage() {
  const [fileName, setFileName] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const acceptedExtensions = ['pdf', 'docx', 'png', 'jpg', 'jpeg'];

  const validateFile = (file: File): boolean => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    return extension ? acceptedExtensions.includes(extension) : false;
  };

  const convertToPdf = async (file: File): Promise<File> => {
    const extension = file.name.split('.').pop()?.toLowerCase();

    if (extension === 'pdf' || extension === 'docx') {
      return file;
    }

    if (['png', 'jpg', 'jpeg'].includes(extension || '')) {
      const { jsPDF } = await import('jspdf');

      return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = async (e) => {
          try {
            const imgData = e.target?.result as string;

            const img = new Image();
            img.onload = () => {
              const pdf = new jsPDF({
                orientation: img.width > img.height ? 'landscape' : 'portrait',
                unit: 'px',
                format: [img.width, img.height],
              });

              pdf.addImage(imgData, 'PNG', 0, 0, img.width, img.height);
              const pdfBlob = pdf.output('blob');
              const pdfFile = new File([pdfBlob], file.name.replace(/\.[^/.]+$/, '.pdf'), {
                type: 'application/pdf',
              });
              resolve(pdfFile);
            };
            img.onerror = () => {
              reject(new Error('Failed to load image'));
            };
            img.src = imgData;
          } catch (err) {
            reject(err);
          }
        };
        reader.onerror = () => reject(new Error('Failed to read file'));
        reader.readAsDataURL(file);
      });
    }

    return file;
  };

  const handleFileSelect = async (file: File) => {
    if (!validateFile(file)) {
      setError('Invalid file type. Please upload: PDF, DOCX, PNG, JPG, or JPEG');
      return;
    }

    setError(null);
    setFileName(file.name);
    setUploadSuccess(false);
    setIsUploading(true);

    try {
      const fileToUpload = await convertToPdf(file);
      console.log(' File converted, uploading:', fileToUpload.name, fileToUpload.type);

      const formData = new FormData();
      formData.append('file', fileToUpload);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      console.log(' Upload response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Upload failed');
      }

      const data = await response.json();
      console.log(' Upload successful:', data);

      setIsUploading(false);
      setUploadSuccess(true);

      setTimeout(() => {
        router.push(`/chat?file=${encodeURIComponent(data.fileName)}`);
      }, 1500);
    } catch (err) {
      console.error(' Upload error:', err);
      setIsUploading(false);
      setFileName(null);
      setError(err instanceof Error ? err.message : 'Upload failed');
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const resetUpload = () => {
    setFileName(null);
    setUploadSuccess(false);
    setIsUploading(false);
    setError(null);
  };

  return (
    <main className="flex items-center justify-center min-h-screen bg-linear-to-br from-background via-background to-background/95 p-4">
      <Card className="w-full max-w-md transition-all duration-300 hover:shadow-lg hover:scale-105">
        <div className="p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">Upload File</h1>
            <p className="text-muted-foreground">PDF, DOCX, PNG, JPG, or JPEG</p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded text-red-600 text-sm">{error}</div>
          )}

          {!uploadSuccess ? (
            <>
              {!isUploading && !fileName ? (
                <>
                  <div
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onClick={handleClick}
                    className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
                      isDragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-foreground font-medium mb-1">Drag & drop your file here</p>
                    <p className="text-muted-foreground text-sm">or click to upload</p>
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    onChange={handleInputChange}
                    accept=".pdf,.docx,.png,.jpg,.jpeg"
                    className="hidden"
                  />
                </>
              ) : null}

              {fileName && isUploading && (
                <div className="text-center">
                  <Loader2 className="w-12 h-12 mx-auto mb-4 text-primary animate-spin" />
                  <p className="text-foreground font-medium mb-1">Uploading & Converting…</p>
                  <p className="text-muted-foreground text-sm truncate">{fileName}</p>
                </div>
              )}
            </>
          ) : (
            <div className="text-center">
              <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
              <p className="text-foreground font-medium mb-1">✅ File uploaded successfully!</p>
              <p className="text-muted-foreground text-sm mb-4">Redirecting to chat...</p>
              <p className="text-muted-foreground text-xs truncate mb-6">{fileName}</p>
            </div>
          )}
        </div>
      </Card>
    </main>
  );
}
