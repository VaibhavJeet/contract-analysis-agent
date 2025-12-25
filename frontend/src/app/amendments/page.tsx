'use client';

import { useQuery } from '@tanstack/react-query';
import { Edit, Check, X, Clock } from 'lucide-react';
import { api } from '@/lib/api';
import type { Amendment } from '@/lib/types';

export default function AmendmentsPage() {
  const { data: amendments, isLoading } = useQuery({
    queryKey: ['amendments'],
    queryFn: () => api.getAmendments(),
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved': return <Check className="w-4 h-4 text-green-600" />;
      case 'rejected': return <X className="w-4 h-4 text-red-600" />;
      default: return <Clock className="w-4 h-4 text-yellow-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved': return 'badge-success';
      case 'rejected': return 'badge-danger';
      case 'applied': return 'badge-primary';
      default: return 'badge-warning';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Amendments</h1>
        <p className="mt-1 text-gray-600">AI-generated contract amendments</p>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
              <div className="h-4 bg-gray-200 rounded w-2/3" />
            </div>
          ))}
        </div>
      ) : amendments && amendments.length > 0 ? (
        <div className="space-y-4">
          {amendments.map((amendment: Amendment) => (
            <div key={amendment.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Edit className="w-5 h-5 text-primary-600" />
                  <span className={`badge ${getStatusBadge(amendment.status)}`}>
                    {amendment.status.replace('_', ' ')}
                  </span>
                  <span className="badge badge-primary">{amendment.amendment_type}</span>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div className="p-3 bg-red-50 rounded-lg">
                  <p className="text-xs font-medium text-red-700 mb-1">Original</p>
                  <p className="text-sm text-red-900 line-clamp-3">{amendment.original_text}</p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <p className="text-xs font-medium text-green-700 mb-1">Proposed</p>
                  <p className="text-sm text-green-900 line-clamp-3">{amendment.proposed_text}</p>
                </div>
              </div>

              {amendment.rationale && (
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs font-medium text-gray-700 mb-1">Rationale</p>
                  <p className="text-sm text-gray-600">{amendment.rationale}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <Edit className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No amendments generated yet</p>
        </div>
      )}
    </div>
  );
}
