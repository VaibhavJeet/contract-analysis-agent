'use client';

interface MetricCardProps {
  title: string;
  value: number | string;
  loading?: boolean;
}

export function MetricCard({ title, value, loading = false }: MetricCardProps) {
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-4" />
        <div className="h-8 bg-gray-200 rounded w-1/3" />
      </div>
    );
  }

  return (
    <div className="card">
      <p className="text-sm font-medium text-gray-500">{title}</p>
      <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
    </div>
  );
}
