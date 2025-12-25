'use client';

import { FileText, Calendar, Users, AlertTriangle, ChevronRight } from 'lucide-react';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import type { Contract } from '@/lib/types';

interface ContractCardProps {
  contract: Contract;
}

export function ContractCard({ contract }: ContractCardProps) {
  const getRiskBadge = (risk?: string) => {
    switch (risk) {
      case 'high': return 'badge-danger';
      case 'medium': return 'badge-warning';
      case 'low': return 'badge-success';
      default: return 'badge-primary';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'analyzed': return 'badge-success';
      case 'parsing': case 'analyzing': return 'badge-warning';
      case 'error': return 'badge-danger';
      default: return 'badge-primary';
    }
  };

  return (
    <Link href={`/contracts/${contract.id}`} className="card hover:shadow-md transition-shadow block">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <FileText className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">{contract.title || contract.filename}</h3>
            <span className={`badge ${getStatusBadge(contract.status)}`}>{contract.status}</span>
            {contract.risk_score && (
              <span className={`badge ${getRiskBadge(contract.risk_score)}`}>
                <AlertTriangle className="w-3 h-3 mr-1" />
                {contract.risk_score} risk
              </span>
            )}
          </div>

          {contract.summary && (
            <p className="text-gray-600 line-clamp-2 mb-3">{contract.summary}</p>
          )}

          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
            <span className="badge badge-primary">{contract.contract_type}</span>
            {contract.parties && contract.parties.length > 0 && (
              <span className="flex items-center gap-1">
                <Users className="w-4 h-4" />
                {contract.parties.slice(0, 2).join(', ')}
              </span>
            )}
            <span className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              {formatDistanceToNow(new Date(contract.created_at), { addSuffix: true })}
            </span>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400" />
      </div>
    </Link>
  );
}
