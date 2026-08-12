/**
 * Shared fetch wrapper for every page's API calls: reads the CSRF cookie
 * Django already sets, attaches it to unsafe requests (mirrors what
 * {% csrf_token %} does for classic form POSTs), and normalizes JSON
 * in/out plus error handling so every page doesn't repeat this.
 *
 * Plain script, no build step / bundler - matches the rest of this
 * project's frontend (no JS framework, static files served as-is).
 */
(function (global) {
    'use strict';

    function getCookie(name) {
        const prefix = name + '=';
        const parts = document.cookie ? document.cookie.split('; ') : [];
        for (const part of parts) {
            if (part.startsWith(prefix)) {
                return decodeURIComponent(part.slice(prefix.length));
            }
        }
        return null;
    }

    const UNSAFE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

    class ApiError extends Error {
        constructor(status, data) {
            super(typeof data === 'object' && data && data.detail ? data.detail : `Request failed (${status})`);
            this.status = status;
            this.data = data;
        }
    }

    /**
     * apiFetch(url, {method, body, params})
     * - body: a plain object (JSON-encoded) or a FormData instance (sent as-is, for file uploads).
     * - params: a plain object of query-string params appended to `url`.
     * - Resolves to the parsed JSON body (or null for 204 No Content).
     * - Rejects with an ApiError(status, data) for any non-2xx response.
     */
    async function apiFetch(url, options = {}) {
        const { method = 'GET', body, params } = options;

        if (params) {
            const qs = new URLSearchParams();
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined && value !== null && value !== '') {
                    qs.set(key, value);
                }
            });
            const qsString = qs.toString();
            if (qsString) {
                url += (url.includes('?') ? '&' : '?') + qsString;
            }
        }

        const headers = { Accept: 'application/json' };
        const isFormData = body instanceof FormData;
        if (body !== undefined && !isFormData) {
            headers['Content-Type'] = 'application/json';
        }
        if (UNSAFE_METHODS.has(method.toUpperCase())) {
            const csrftoken = getCookie('csrftoken');
            if (csrftoken) {
                headers['X-CSRFToken'] = csrftoken;
            }
        }

        const response = await fetch(url, {
            method,
            headers,
            credentials: 'same-origin',
            body: body === undefined ? undefined : isFormData ? body : JSON.stringify(body),
        });

        if (response.status === 204) {
            return null;
        }

        const contentType = response.headers.get('Content-Type') || '';
        const data = contentType.includes('application/json') ? await response.json() : await response.text();

        if (!response.ok) {
            throw new ApiError(response.status, data);
        }
        return data;
    }

    global.KipsAPI = { apiFetch, ApiError, getCookie };
})(window);
