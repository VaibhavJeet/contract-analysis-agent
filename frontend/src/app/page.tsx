'use client';

import { useQuery } from '@tanstack/react-query';
import { FileText, AlertTriangle, FileCheck, Edit, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { MetricCard } from '@/components/MetricCard';

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => api.getStats(),
  });

  const navigationCards = [
    {
      title: 'Contracts',
      description: 'Upload and analyze contracts',
      icon: FileText,
      href: '/contracts',
      color: 'bg-blue-500',
    },
    {
      title: 'Clauses',
      description: 'Review extracted clauses',
      icon: FileCheck,
      href: '/clauses',
      color: 'bg-purple-500',
    },
    {
      title: 'Risk Analysis',
      description: 'View risk assessments',
      icon: AlertTriangle,
      href: '/risks',
      color: 'bg-orange-500',
    },
    {
      title: 'Amendments',
      description: 'Generate and manage amendments',
      icon: Edit,
      href: '/amendments',
      color: 'bg-green-500',
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">AI-powered contract analysis and review</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard title="Total Contracts" value={stats?.total_contracts ?? 0} loading={isLoading} />
        <MetricCard title="Analyzed" value={stats?.analyzed_contracts ?? 0} loading={isLoading} />
        <MetricCard title="High Risk Clauses" value={stats?.high_risk_clauses ?? 0} loading={isLoading} />
        <MetricCard title="Pending Amendments" value={stats?.pending_amendments ?? 0} loading={isLoading} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {navigationCards.map((card) => (
          <Link key={card.href} href={card.href} className="card group hover:shadow-md transition-shadow">
            <div className={`${card.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
              <card.icon className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600">{card.title}</h3>
            <p className="mt-1 text-sm text-gray-500">{card.description}</p>
            <div className="mt-4 flex items-center text-primary-600 text-sm font-medium">
              View <ArrowRight className="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
