import { z } from 'zod';

// Client-side validation is UX sugar only (catch empty/malformed fields
// before a round trip) - Django's own validators (password strength, old
// password correctness, etc.) remain the real source of truth and their
// errors are surfaced from the server response regardless of what passes
// here. See src/lib/api/client.ts's ApiError.

export const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});
export type LoginInput = z.infer<typeof loginSchema>;

export const changePasswordSchema = z
  .object({
    old_password: z.string().min(1, 'Current password is required'),
    new_password1: z.string().min(8, 'New password must be at least 8 characters'),
    new_password2: z.string().min(1, 'Please confirm your new password'),
  })
  .refine((data) => data.new_password1 === data.new_password2, {
    message: 'Passwords do not match',
    path: ['new_password2'],
  });
export type ChangePasswordInput = z.infer<typeof changePasswordSchema>;
