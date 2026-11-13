export interface SystemHealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  service: string;
  environment: string;
  timestamp: string;
  total_latency_ms: number;
  components: {
    database: {
      status: string;
      latency_ms: number | null;
    };
    redis: {
      status: string;
      latency_ms: number | null;
    };
  };
  enterprise_context: {
    organization: string;
    headquarters: string;
  };
}

export interface OperatingLocation {
  id: string;
  name: string;
  code: string;
  type: 'factory' | 'warehouse' | 'corporate_office' | 'service_center' | 'spare_parts_store';
  city: string;
  state: string;
}

export interface UserSession {
  id: string;
  email: string;
  fullName: string;
  role: string;
  locationName: string;
}
