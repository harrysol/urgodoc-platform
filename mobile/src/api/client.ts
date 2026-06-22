import { API_BASE_URL } from "../config";
import type { ProductDetail, UserDimensions, UserProfile } from "./types";

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // non-JSON error body; keep statusText
    }
    throw new ApiError(detail, res.status);
  }

  // 204 No Content guard
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  /** Submit a retail link; returns the created job (status = PENDING). */
  submitProduct: (url: string) =>
    request<ProductDetail>("/products/submit", {
      method: "POST",
      body: JSON.stringify({ url }),
    }),

  /** Poll a single job's status / result. */
  getProduct: (id: string) => request<ProductDetail>(`/products/${id}`),

  /** List recent jobs. */
  listProducts: () => request<ProductDetail[]>("/products"),

  /** Upsert a user's calibrated body dimensions. */
  saveDimensions: (userId: string, dims: UserDimensions) =>
    request<UserProfile>(`/users/${encodeURIComponent(userId)}/dimensions`, {
      method: "PUT",
      body: JSON.stringify(dims),
    }),

  /** Fetch a user's saved dimensions (throws ApiError 404 if none). */
  getDimensions: (userId: string) =>
    request<UserProfile>(`/users/${encodeURIComponent(userId)}/dimensions`),
};

export { ApiError };
