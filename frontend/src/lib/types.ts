export interface Contract {
  id: string;
  filename: string;
  title?: string;
  contract_type: string;
  status: string;
  parties: string[];
  effective_date?: string;
  expiration_date?: string;
  summary?: string;
  risk_score?: string;
  overall_assessment?: string;
  created_at: string;
  updated_at: string;
}

export interface Clause {
  id: string;
  contract_id: string;
  clause_type: string;
  title?: string;
  text: string;
  section_number?: string;
  page_number?: string;
  risk_level?: string;
  risk_score?: number;
  risk_factors: string[];
  key_terms: string[];
  analysis?: string;
  created_at: string;
}

export interface Amendment {
  id: string;
  contract_id: string;
  clause_id?: string;
  amendment_type: string;
  status: string;
  original_text?: string;
  proposed_text: string;
  rationale?: string;
  risk_mitigation?: string;
  negotiation_points: string[];
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  total_contracts: number;
  analyzed_contracts: number;
  total_clauses: number;
  high_risk_clauses: number;
  pending_amendments: number;
  analysis_rate: number;
}

export interface Analytics {
  contracts_by_type: { type: string; count: number }[];
  clauses_by_type: { type: string; count: number }[];
  risk_distribution: { level: string; count: number }[];
  amendments_by_status: { status: string; count: number }[];
  most_risky_clause_types: { type: string; count: number }[];
}
