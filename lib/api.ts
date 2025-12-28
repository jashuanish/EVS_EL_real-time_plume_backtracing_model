/**
 * API Client for Environmental Safety Platform Backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface LocationResponse {
  location: {
    lat: number;
    lng: number;
    name: string;
  };
  timestamp: string;
  data_timestamp: {
    air_quality?: string;
    water_quality?: string;
    land?: string;
    meteorology?: string;
  };
  verdict: {
    level: 'SAFE' | 'MODERATE' | 'UNSAFE';
    confidence: number;
    risk_score: number;
  };
  metrics: {
    air: Record<string, {
      value: number;
      unit: string;
      threshold?: number;
      source: string;
    }>;
    water: {
      quality_score?: number;
      turbidity?: number;
      status?: string;
      source?: string;
    };
    land: {
      deforestation_risk?: number;
      trend?: string;
      source?: string;
    };
  };
  plumes: Array<{
    detected: boolean;
    pollutant?: string;
    intensity?: number;
    source_estimate?: any;
  }>;
  sources: {
    satellite?: string;
    ground_sensors?: string[];
    weather?: string;
  };
}

export interface AnalysisResponse {
  human_readable: {
    summary: string;
    reasons: string[];
    recommendations: string[];
  };
  technical: {
    air_quality?: Record<string, any>;
    risk_model?: {
      exposure_score: number;
      duration_score: number;
      uncertainty_penalty: number;
      final_risk_score: number;
      model_version: string;
      feature_importance: Record<string, number>;
    };
  };
  model_info: {
    risk_model_version: string;
    timestamp: string;
  };
}

export interface ForecastResponse {
  location: [number, number];
  forecast_type: string;
  horizon_hours: number;
  generated_at: string;
  predictions: Array<{
    timestamp: string;
    [key: string]: any;
  }>;
  model_info: {
    type: string;
    training_data_range?: string;
    rmse?: number;
    mae?: number;
    note?: string;
  };
}

export interface SearchResult {
  results: Array<{
    name: string;
    lat: number;
    lng: number;
    type: string;
    importance: number;
  }>;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async fetchLocation(lat: number, lng: number): Promise<LocationResponse> {
    const response = await fetch(`${this.baseUrl}/location/${lat}/${lng}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    return response.json();
  }

  async fetchAnalysis(lat: number, lng: number): Promise<AnalysisResponse> {
    const response = await fetch(`${this.baseUrl}/analysis/${lat}/${lng}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    return response.json();
  }

  async fetchForecast(lat: number, lng: number, horizonHours: number = 48): Promise<ForecastResponse> {
    const response = await fetch(`${this.baseUrl}/forecast/${lat}/${lng}?horizon_hours=${horizonHours}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    return response.json();
  }

  async searchLocation(query: string): Promise<SearchResult> {
    const response = await fetch(`${this.baseUrl}/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    return response.json();
  }
}

export const apiClient = new ApiClient();

