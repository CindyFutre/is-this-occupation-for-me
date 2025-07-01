// API client for the backend job analysis service

export interface JobSearchRequest {
  query: string;
  location?: string;
}

export interface JobSuggestion {
  title: string;
  soc_code: string;
  similarity_score: number;
}

export interface AnalyzedTerm {
  term: string;
  count: number;
  context_sentences: string[];
}

export interface JobInsightsReport {
  success: boolean;
  soc_code: string;
  job_title: string;
  location: string;
  total_postings_analyzed: number;
  responsibilities: AnalyzedTerm[];
  skills: AnalyzedTerm[];
  qualifications: AnalyzedTerm[];
  unique_aspects: AnalyzedTerm[];
}

export interface JobAnalysisResponse {
  success: boolean;
  data?: JobInsightsReport;
  suggestions?: JobSuggestion[];
  error?: {
    code: string;
    message: string;
  };
}

export class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8001';
  }

  async analyzeJob(request: JobSearchRequest): Promise<JobAnalysisResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/jobs/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API call failed:', error);
      return {
        success: false,
        error: {
          code: 'NETWORK_ERROR',
          message: error instanceof Error ? error.message : 'Unknown error occurred',
        },
      };
    }
  }

  async checkHealth(): Promise<{ status: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/health`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
}

// Export a singleton instance
export const apiClient = new ApiClient();