// Mirrors apps/accounts/serializers.py::PersonSerializer exactly.
export type Person = {
  id: number;
  username: string;
  full_name: string;
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  role: string;
  role_display: string;
  is_active: boolean;
  identifier: string | null;
  department: string | null;
  profile_id: number | null;
};

export type CreatePersonResult = {
  id: number;
  user_id: number;
  username: string;
  temp_password: string;
  roll_number?: string;
  employee_id?: string;
};
