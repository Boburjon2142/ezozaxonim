export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type ApiError = {
  detail?: { code: string; message: string };
};

export async function api<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  if (!res.ok) {
    const err = (await res.json().catch(() => ({}))) as ApiError;
    throw new Error(err.detail?.message || "API request failed");
  }
  return res.json() as Promise<T>;
}
