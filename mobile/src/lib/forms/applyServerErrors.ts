import type { FieldValues, Path, UseFormSetError } from 'react-hook-form';

import { ApiError } from '@/lib/api/client';

/**
 * Every API view built server-side returns Django-form-style errors on 400:
 * `{field_name: ["message", ...], ...}` (see e.g. apps/accounts/api_views.py
 * ::student_create). This maps that shape onto react-hook-form's setError so
 * server-side validation (the real source of truth) shows up under the
 * right field, exactly like the Django template forms do on the web.
 *
 * Returns a generic top-level message for anything that isn't a per-field
 * error (network failure, a `{detail: "..."}` permission error, or a
 * non-ApiError), so the caller can show it in a toast/banner instead.
 */
export function applyServerErrors<T extends FieldValues>(
  error: unknown,
  setError: UseFormSetError<T>,
  knownFields: readonly string[],
): string | null {
  if (!(error instanceof ApiError) || typeof error.data !== 'object' || error.data === null) {
    return error instanceof Error ? error.message : 'Something went wrong.';
  }

  const data = error.data as Record<string, unknown>;
  let matchedAny = false;
  let firstGenericMessage: string | null = null;

  for (const [key, value] of Object.entries(data)) {
    const messages = Array.isArray(value) ? value.filter((m): m is string => typeof m === 'string') : [];
    if (messages.length === 0) continue;

    if (key === 'detail') {
      firstGenericMessage ??= messages[0];
      continue;
    }

    if (knownFields.includes(key)) {
      setError(key as Path<T>, { type: 'server', message: messages.join(' ') });
      matchedAny = true;
    } else {
      // A __all__/non_field_errors-style error, or a field the form doesn't render.
      firstGenericMessage ??= messages[0];
    }
  }

  if (typeof data.detail === 'string') firstGenericMessage ??= data.detail;

  return matchedAny ? firstGenericMessage : (firstGenericMessage ?? 'Please check the form and try again.');
}
