import { API_BASE_URL } from './config';

/** Shape of every `RoleScopedModelViewSet` list response (DRF PageNumberPagination, page_size=50). */
export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

/**
 * Thrown for any non-2xx response. `data` is the parsed JSON body when the
 * server sent one - every API view built server-side returns either
 * `{detail: string}` or a Django-form-style `{field: [messages, ...]}` shape
 * on error, so callers can pattern-match on `data` to show field-level
 * errors in a form, or fall back to `message` for a generic toast.
 */
export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, data: unknown) {
    super(extractMessage(data) ?? `Request failed (${status}).`);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

/** The request never reached the server - no connectivity, wrong LAN IP, server not running, etc. */
export class NetworkError extends Error {
  constructor(cause: unknown) {
    super('Could not reach the server. Check your Wi-Fi connection and that the server is running.');
    this.name = 'NetworkError';
    this.cause = cause;
  }
}

function extractMessage(data: unknown): string | null {
  if (data && typeof data === 'object') {
    const obj = data as Record<string, unknown>;
    if (typeof obj.detail === 'string') return obj.detail;
    // Django form-style {field: ["message"]} - surface the first one generically;
    // screens that render a form should read `error.data` directly instead.
    const firstKey = Object.keys(obj)[0];
    const firstValue = firstKey ? obj[firstKey] : undefined;
    if (Array.isArray(firstValue) && typeof firstValue[0] === 'string') {
      return firstValue[0];
    }
  }
  return null;
}

/**
 * Wired up by AuthContext (Phase 2) so this module never imports React/auth
 * state directly - keeps the API layer usable from anywhere (including
 * outside components) and avoids a circular import between the client and
 * the context that depends on it.
 */
type AuthHooks = {
  getAccessToken: () => string | null;
  /** Attempts a silent token refresh; returns the new access token, or null if the refresh itself failed. */
  refreshAccessToken: () => Promise<string | null>;
  /** Called when a request still 401s after a refresh attempt - the caller should force logout. */
  onAuthenticationFailed: () => void;
};

let authHooks: AuthHooks | null = null;

export function registerAuthHooks(hooks: AuthHooks) {
  authHooks = hooks;
}

type RequestOptions = {
  method?: 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';
  body?: unknown;
  /** Pass a FormData instance directly (photo uploads) - skips JSON.stringify and Content-Type. */
  form?: FormData;
  query?: Record<string, string | number | boolean | undefined | null>;
  /** Most endpoints require a valid JWT; a handful (token obtain) don't. Defaults to true. */
  auth?: boolean;
  /** Internal - set on the retried request after a token refresh, to prevent infinite retry loops. */
  _isRetry?: boolean;
};

function buildUrl(path: string, query?: RequestOptions['query']) {
  const url = new URL(API_BASE_URL + path);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

async function parseBody(response: Response): Promise<unknown> {
  if (response.status === 204) return null;
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, form, query, auth = true, _isRetry = false } = options;

  const headers: Record<string, string> = { Accept: 'application/json' };
  if (!form) headers['Content-Type'] = 'application/json';
  if (auth) {
    const token = authHooks?.getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(buildUrl(path, query), {
      method,
      headers,
      body: form ?? (body !== undefined ? JSON.stringify(body) : undefined),
    });
  } catch (cause) {
    throw new NetworkError(cause);
  }

  if (response.status === 401 && auth && !_isRetry && authHooks) {
    const newToken = await authHooks.refreshAccessToken();
    if (newToken) {
      return request<T>(path, { ...options, _isRetry: true });
    }
    authHooks.onAuthenticationFailed();
  }

  const data = await parseBody(response);
  if (!response.ok) {
    throw new ApiError(response.status, data);
  }
  return data as T;
}

export const apiFetch = {
  get: <T>(path: string, query?: RequestOptions['query'], options?: Pick<RequestOptions, 'auth'>) =>
    request<T>(path, { method: 'GET', query, ...options }),
  post: <T>(path: string, body?: unknown, options?: Pick<RequestOptions, 'auth'>) =>
    request<T>(path, { method: 'POST', body, ...options }),
  patch: <T>(path: string, body?: unknown, options?: Pick<RequestOptions, 'auth'>) =>
    request<T>(path, { method: 'PATCH', body, ...options }),
  put: <T>(path: string, body?: unknown, options?: Pick<RequestOptions, 'auth'>) =>
    request<T>(path, { method: 'PUT', body, ...options }),
  delete: <T>(path: string, options?: Pick<RequestOptions, 'auth'>) =>
    request<T>(path, { method: 'DELETE', ...options }),
  postForm: <T>(path: string, form: FormData) => request<T>(path, { method: 'POST', form }),
  patchForm: <T>(path: string, form: FormData) => request<T>(path, { method: 'PATCH', form }),
};
