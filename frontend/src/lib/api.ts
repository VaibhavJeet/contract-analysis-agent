import axios from 'axios';
import type { Contract, Clause, Amendment, DashboardStats, Analytics } from './types';

const client = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

export const api = {
  async getStats(): Promise<DashboardStats> {
    const { data } = await client.get('/api/analytics/stats');
    return data;
  },

  async getContracts(): Promise<Contract[]> {
    const { data } = await client.get('/api/contracts');
    return data;
  },

  async getContract(id: string): Promise<Contract> {
    const { data } = await client.get(`/api/contracts/${id}`);
    return data;
  },

  async uploadContract(file: File): Promise<Contract> {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await client.post('/api/contracts', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async analyzeContract(id: string): Promise<Contract> {
    const { data } = await client.post(`/api/contracts/${id}/analyze`);
    return data;
  },

  async getClauses(contractId: string): Promise<Clause[]> {
    const { data } = await client.get(`/api/clauses/contract/${contractId}`);
    return data;
  },

  async assessClauseRisk(clauseId: string): Promise<Clause> {
    const { data } = await client.post(`/api/clauses/${clauseId}/assess-risk`);
    return data;
  },

  async getAmendments(): Promise<Amendment[]> {
    const { data } = await client.get('/api/amendments');
    return data;
  },

  async generateAmendments(contractId: string): Promise<Amendment[]> {
    const { data } = await client.post(`/api/amendments/contract/${contractId}/generate`);
    return data.amendments;
  },

  async getAnalytics(): Promise<Analytics> {
    const { data } = await client.get('/api/analytics');
    return data;
  },
};
