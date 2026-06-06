/**
 * Quotations — QuotationTable
 */

import type { Quotation } from '../../../types'
import { Table, StatusBadge, Button } from '../ui'
import { formatCurrency } from '../../../utils/formatters'

interface QuotationTableProps {
  quotations?: Quotation[]
  isLoading?: boolean
  onView?: (id: string) => void
  onAward?: (id: string) => void
}

export function QuotationTable({ quotations = [], isLoading, onView, onAward }: QuotationTableProps) {
  return (
    <Table
      data={quotations}
      keyExtractor={(q) => q.id}
      isLoading={isLoading}
      emptyMessage="No quotations submitted yet."
      columns={[
        { key: 'quotation_number', header: 'Quotation #' },
        { key: 'currency',         header: 'Currency' },
        { key: 'total_amount',     header: 'Total',  render: (q) => q.total_amount ? formatCurrency(q.total_amount, q.currency) : '—' },
        { key: 'valid_until',      header: 'Valid Until', render: (q) => q.valid_until ?? '—' },
        { key: 'status',           header: 'Status', render: (q) => <StatusBadge status={q.status} /> },
        {
          key: 'actions',
          header: 'Actions',
          render: (q) => (
            <div className="flex items-center gap-2">
              <Button size="sm" variant="ghost" onClick={() => onView?.(q.id)}>View</Button>
              {q.status === 'under_review' && (
                <Button size="sm" variant="primary" onClick={() => onAward?.(q.id)}>Award</Button>
              )}
            </div>
          ),
        },
      ]}
    />
  )
}
