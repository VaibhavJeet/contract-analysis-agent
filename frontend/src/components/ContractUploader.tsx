'use client';

import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, Loader2, FileText } from 'lucide-react';

interface ContractUploaderProps {
  onUpload: (file: File) => void;
  onClose: () => void;
  uploading?: boolean;
}

export function ContractUploader({ onUpload, onClose, uploading = false }: ContractUploaderProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles[0]);
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Upload Contract</h3>
        <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded" disabled={uploading}>
          <X className="w-5 h-5" />
        </button>
      </div>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'
        } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <>
            <Loader2 className="w-12 h-12 text-primary-500 mx-auto mb-4 animate-spin" />
            <p className="text-gray-600">Uploading and analyzing...</p>
          </>
        ) : acceptedFiles.length > 0 ? (
          <>
            <FileText className="w-12 h-12 text-primary-500 mx-auto mb-4" />
            <p className="text-gray-900 font-medium">{acceptedFiles[0].name}</p>
            <p className="text-sm text-gray-500 mt-1">Click upload to process</p>
          </>
        ) : (
          <>
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">
              {isDragActive ? 'Drop the contract here...' : 'Drag & drop a contract, or click to select'}
            </p>
            <p className="text-sm text-gray-400 mt-2">Supports PDF, DOCX, DOC, TXT</p>
          </>
        )}
      </div>
    </div>
  );
}
