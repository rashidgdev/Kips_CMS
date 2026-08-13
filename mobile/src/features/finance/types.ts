// Mirrors apps/finance/api_views.py + serializers.py exactly.

export type StudentFeeItem = {
  id: number;
  category: number;
  category_label: string;
  semester: number;
  semester_label: string;
  amount_due: number;
  due_date: string;
};

export type FeeOverviewRow = {
  item: StudentFeeItem;
  paid: number;
  outstanding: number;
  status: 'paid' | 'partial' | 'overdue' | 'unpaid';
};

export type FeeOverview = {
  rows: FeeOverviewRow[];
  total_due: number;
  total_paid: number;
  total_outstanding: number;
};

export type ChallanStatus = 'paid' | 'overdue' | 'unpaid' | 'cancelled';

export type Challan = {
  id: number;
  challan_number: string;
  student: number;
  student_label: string;
  semester: number;
  semester_label: string;
  issue_date: string;
  due_date: string;
  total_amount: number;
  is_cancelled: boolean;
  status: ChallanStatus;
};

export type ChallanLine = { id: number; fee_item: number; category: string; amount: number };

export type Payment = {
  id: number;
  fee_item: number;
  challan: number | null;
  amount_paid: number;
  payment_date: string;
  payment_method: 'cash' | 'bank_transfer' | 'cheque' | 'online';
};

export type StudentFeeSummaryRow = {
  student_id: number;
  roll_number: string;
  name: string;
  program: string;
  total_due: number;
  total_paid: number;
  total_outstanding: number;
};

export type StudentFeeDetail = {
  student_id: number;
  roll_number: string;
  overview: FeeOverview;
  challans: Challan[];
};

export type MyFeeOverview = {
  overview: FeeOverview;
  challans: Challan[];
};

export type ChallanDetail = {
  challan: Challan;
  lines: ChallanLine[];
  pdf_url: string;
};

export type OutstandingItem = { fee_item: StudentFeeItem; outstanding: number };

export type ChallanGenerateOptions = {
  student_id: number;
  semester: string;
  outstanding_items: OutstandingItem[];
};
