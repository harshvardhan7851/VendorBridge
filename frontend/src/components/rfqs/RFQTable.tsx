/**
 * RFQs — RFQTable
 * TODO: Wire to useRFQs() hook.
 */

import type { RFQ } from '../../../types'
import { Table, StatusBadge, Button } from '../ui'
import { formatDate } from '../../../utils/formatters'

interface RFQTableProps {
  rfqs?: RFQ[]
  isLoading?: boolean
  onView?: (id: string) => void
  onPublish?: (id: string) => void
}

export function RFQTable({ rfqs = [], isLoading, onView, onPublish }: RFQTableProps) {
  return (
    <Table
      data={rfqs}
      keyExtractor={(r) => r.id}
      isLoading={isLoading}
      emptyMessage="No RFQs found. Create your first request for quotation."
      columns={[
        { key: 'rfq_number',  header: 'RFQ #' },
        { key: 'title',       header: 'Title' },
        { key: 'category',    header: 'Category', render: (r) => r.category ?? '—' },
        { key: 'deadline',    header: 'Deadline',  render: (r) => r.submission_deadline ? formatDate(r.submission_deadline) : '—' },
        { key: 'status',      header: 'Status',    render: (r) => <StatusBadge status={r.status} /> },
        { key: 'items',       header: 'Line Items', render: (r) => r.line_items.length },
        {
          key: 'actions',
          header: 'Actions',
          render: (r) => (
            <div className="flex items-center gap-2">
              <Button size="sm" variant="ghost" onClick={() => onView?.(r.id)}>View</Button>
              {r.status === 'draft' && (
                <Button size="sm" variant="primary" onClick={() => onPublish?.(r.id)}>Publish</Button>
              )}
            </div>
          ),
        },
      ]}
    />
  )
}
