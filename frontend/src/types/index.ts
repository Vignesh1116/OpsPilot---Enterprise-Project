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
  address?: string;
  postal_code?: string;
}

export interface Department {
  id: string;
  name: string;
  code: string;
  description?: string;
}

export interface Employee {
  id: string;
  company_id: string;
  location_id?: string;
  location_name?: string;
  department_id?: string;
  department_name?: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone?: string;
  designation?: string;
  is_active: boolean;
  roles: string[];
  permissions: string[];
  created_at: string;
}

export interface AssetCategory {
  id: string;
  company_id: string;
  name: string;
  code: string;
  description?: string;
  depreciation_method: string;
  expected_lifetime_months: number;
  created_at: string;
}

export interface Asset {
  id: string;
  company_id: string;
  location_id: string;
  location_name?: string;
  location_code?: string;
  department_id?: string;
  department_name?: string;
  category_id: string;
  category_name?: string;
  category_code?: string;
  asset_tag: string;
  name: string;
  model_number?: string;
  serial_number?: string;
  status: 'operational' | 'in_maintenance' | 'out_of_service' | 'decommissioned';
  critical_level: 'low' | 'medium' | 'high' | 'critical';
  purchase_date: string;
  purchase_cost: number;
  warranty_expiry_date?: string;
  expected_lifetime_months: number;
  qr_code_url?: string;
  qr_code_data_uri?: string;
  created_at: string;
  updated_at: string;
}

export interface AuditLog {
  id: string;
  company_id: string;
  user_id?: string;
  user_name?: string;
  action: string;
  entity_name: string;
  entity_id: string;
  old_values?: Record<string, unknown>;
  new_values?: Record<string, unknown>;
  ip_address?: string;
  created_at: string;
}
