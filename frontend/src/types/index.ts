/**
 * TypeScript Types / Interfaces
 * ==============================
 * Shared domain types matching backend Pydantic schemas.
 * Keep in sync with backend/app/schemas/
 */

// ---------------------------------------------------------------------------
// Common
// ---------------------------------------------------------------------------

export type UUID = string

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// ---------------------------------------------------------------------------
// User & Auth
// ---------------------------------------------------------------------------

export type UserRole = 'admin' | 'procurement_officer' | 'vendor' | 'manager'

export interface User {
  id: UUID
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  is_verified: boolean
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  email: string
  full_name: string
  password: string
  role?: UserRole
}

// ---------------------------------------------------------------------------
// Vendor
// ---------------------------------------------------------------------------

export type VendorStatus = 'pending' | 'approved' | 'rejected' | 'suspended'

export interface Vendor {
  id: UUID
  company_name: string
  email: string
  phone?: string
  city?: string
  country?: string
  category?: string
  status: VendorStatus
  is_active: boolean
}

// ---------------------------------------------------------------------------
// RFQ
// ---------------------------------------------------------------------------

export type RFQStatus = 'draft' | 'published' | 'closed' | 'awarded' | 'cancelled'

export interface RFQLineItem {
  id: UUID
  item_number: number
  description: string
  quantity: number
  unit?: string
  estimated_unit_price?: number
}

export interface RFQ {
  id: UUID
  rfq_number: string
  title: string
  description?: string
  category?: string
  submission_deadline?: string
  delivery_date?: string
  status: RFQStatus
  line_items: RFQLineItem[]
}

// ---------------------------------------------------------------------------
// Quotation
// ---------------------------------------------------------------------------

export type QuotationStatus = 'draft' | 'submitted' | 'under_review' | 'awarded' | 'rejected'

export interface QuotationLineItem {
  id: UUID
  item_number: number
  description: string
  quantity: number
  unit_price: number
  total_price?: number
}

export interface Quotation {
  id: UUID
  quotation_number: string
  status: QuotationStatus
  subtotal?: number
  tax_amount?: number
  total_amount?: number
  currency: string
  valid_until?: string
  notes?: string
  line_items: QuotationLineItem[]
}

// ---------------------------------------------------------------------------
// Approval
// ---------------------------------------------------------------------------

export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'escalated'
export type ApprovalType = 'rfq' | 'purchase_order' | 'vendor_registration'

export interface ApprovalRequest {
  id: UUID
  approval_number: string
  approval_type: ApprovalType
  status: ApprovalStatus
  requester_notes?: string
  approver_comments?: string
}

// ---------------------------------------------------------------------------
// Purchase Order
// ---------------------------------------------------------------------------

export type POStatus =
  | 'draft' | 'pending_approval' | 'approved' | 'sent'
  | 'acknowledged' | 'partially_delivered' | 'delivered' | 'closed' | 'cancelled'

export interface POLineItem {
  id: UUID
  item_number: number
  description: string
  quantity: number
  unit_price: number
  total_price?: number
  quantity_received?: number
}

export interface PurchaseOrder {
  id: UUID
  po_number: string
  status: POStatus
  total_amount?: number
  currency: string
  order_date?: string
  expected_delivery_date?: string
  line_items: POLineItem[]
}

// ---------------------------------------------------------------------------
// Invoice
// ---------------------------------------------------------------------------

export type InvoiceStatus =
  | 'received' | 'under_review' | 'approved' | 'rejected'
  | 'payment_pending' | 'paid' | 'partially_paid'

export interface Invoice {
  id: UUID
  invoice_number: string
  status: InvoiceStatus
  total_amount: number
  amount_paid?: number
  currency: string
  invoice_date: string
  due_date?: string
  payment_date?: string
}

// ---------------------------------------------------------------------------
// Notification
// ---------------------------------------------------------------------------

export interface Notification {
  id: UUID
  title: string
  message: string
  notification_type: string
  is_read: boolean
  related_entity_type?: string
  related_entity_id?: UUID
}
