'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, FileText, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { ContractUploader } from '@/components/ContractUploader';
import { ContractCard } from '@/components/ContractCard';

export default function ContractsPage() {
  const [showUploader, setShowUploader] = useState(false);
  const queryClient = useQueryClient();

  const { data: contracts, isLoading } = useQuery({
    queryKey: ['contracts'],
    queryFn: () => api.getContracts(),
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => api.uploadContract(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
      setShowUploader(false);
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Contracts</h1>
          <p className="mt-1 text-gray-600">Upload and analyze legal contracts</p>
        </div>
        <button onClick={() => setShowUploader(true)} className="btn btn-primary">
          <Plus className="w-4 h-4 mr-2" /> Upload Contract
        </button>
      </div>

      {showUploader && (
        <ContractUploader
          onUpload={(file) => uploadMutation.mutate(file)}
          onClose={() => setShowUploader(false)}
          uploading={uploadMutation.isPending}
        />
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      ) : contracts && contracts.length > 0 ? (
        <div className="grid gap-4">
          {contracts.map((contract) => (
            <ContractCard key={contract.id} contract={contract} />
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No contracts uploaded yet</p>
          <button onClick={() => setShowUploader(true)} className="btn btn-primary mt-4">
            Upload Your First Contract
          </button>
        </div>
      )}
    </div>
  );
}
