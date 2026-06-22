// Mirrors the backend Pydantic schemas (app/schemas.py).

export type TaskStatus =
  | "PENDING"
  | "SCRAPING"
  | "EXTRACTING"
  | "GENERATING_3D"
  | "COMPLETED"
  | "FAILED";

export interface EstimatedDimensionsCm {
  chest_width_cm: number | null;
  garment_length_cm: number | null;
  sleeve_length_cm: number | null;
  shoulder_width_cm: number | null;
  waist_cm: number | null;
  hip_cm: number | null;
  inseam_cm: number | null;
}

export interface ExtractedProductData {
  title: string;
  brand: string | null;
  category: string;
  garment_type: string | null;
  price: number | null;
  currency: string | null;
  primary_color: string | null;
  colors: string[];
  material: string | null;
  pattern: string | null;
  description: string | null;
  size_options: string[];
  estimated_dimensions_cm: EstimatedDimensionsCm;
  fit: string | null;
  confidence: number;
}

export interface ProductDetail {
  id: string;
  status: TaskStatus;
  source_url: string;
  affiliate_url: string | null;
  status_detail: string | null;
  progress: number;
  product_image_url: string | null;
  extracted_data: ExtractedProductData | null;
  tripo_task_id: string | null;
  model_url: string | null;
  thumbnail_url: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserDimensions {
  height_cm?: number | null;
  weight_kg?: number | null;
  chest_cm?: number | null;
  waist_cm?: number | null;
  hips_cm?: number | null;
  inseam_cm?: number | null;
  shoulder_cm?: number | null;
  arm_length_cm?: number | null;
  neck_cm?: number | null;
  gender?: string | null;
  fit_preference?: string | null;
  raw_landmarks?: Record<string, unknown> | null;
}

export interface UserProfile extends UserDimensions {
  id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}
