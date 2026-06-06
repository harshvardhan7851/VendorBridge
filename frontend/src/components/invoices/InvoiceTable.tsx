/**
 * Invoices — InvoiceTable
 */

import type { Invoice } from '../../../types'
import { Table, StatusBadge, Button } from '../ui'
import { formatCurrency, formatDate } from '../../../utils/formatters'

interface InvoiceTableProps {
  invoices?: Invoice[]
  isLoading?: boolean
  onView?: (id: string) => void
  onApprove?: (id: string) => void
  onReject?: (id: string) => void
}

export function InvoiceTable({ invoices = [], isLoading, onView, onApprove, onReject }: InvoiceTableProps) {
  return (
    <Table
      data={invoices}
      keyExtractor={(i) => i.id}
      isLoading={isLoading}
      emptyMessage="No invoices received yet."
      columns={[
        { key: 'invoice_number', header: 'Invoice #' },
        { key: 'total_amount',   header: 'Amount',   render: (i) => formatCurrency(i.total_amount, i.currency) },
        { key: 'invoice_date',   header: 'Date',     render: (i) => formatDate(i.invoice_date) },
        { key: 'due_date',       header: 'Due Date', render: (i) => i.due_date ? formatDate(i.due_date) : '—' },
        { key: 'status',         header: 'Status',   render: (i) => <StatusBadge status={i.status} /> },
        {
          key: 'actions',
          header: 'Actions',
          render: (i) => (
            <div className="flex items-center gap-2">
              <Button size="sm" variant="ghost" onClick={() => onView?.(i.id)}>View</Button>
              {i.status === 'under_review' && (
                <>
                  <Button size="sm" variant="primary" onClick={() => onApprove?.(i.id)}>Approve</Button>
                  <Button size="sm" variant="danger"  onClick={() => onReject?.(i.id)}>Reject</Button>
                </>
              )}
            </div>
          ),
        },
      ]}
    />
  )
}
