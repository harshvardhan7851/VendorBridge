/**
 * Purchase Orders — POTable
 */

import type { PurchaseOrder } from '../../../types'
import { Table, StatusBadge, Button } from '../ui'
import { formatCurrency, formatDate } from '../../../utils/formatters'

interface POTableProps {
  orders?: PurchaseOrder[]
  isLoading?: boolean
  onView?: (id: string) => void
  onSend?: (id: string) => void
}

export function POTable({ orders = [], isLoading, onView, onSend }: POTableProps) {
  return (
    <Table
      data={orders}
      keyExtractor={(o) => o.id}
      isLoading={isLoading}
      emptyMessage="No purchase orders yet."
      columns={[
        { key: 'po_number',              header: 'PO #' },
        { key: 'total_amount',           header: 'Total',    render: (o) => o.total_amount ? formatCurrency(o.total_amount, o.currency) : '—' },
        { key: 'order_date',             header: 'Order Date', render: (o) => o.order_date ? formatDate(o.order_date) : '—' },
        { key: 'expected_delivery_date', header: 'Delivery',   render: (o) => o.expected_delivery_date ? formatDate(o.expected_delivery_date) : '—' },
        { key: 'status',                 header: 'Status',  render: (o) => <StatusBadge status={o.status} /> },
        {
          key: 'actions',
          header: 'Actions',
          render: (o) => (
            <div className="flex items-center gap-2">
              <Button size="sm" variant="ghost" onClick={() => onView?.(o.id)}>View</Button>
              {o.status === 'approved' && (
                <Button size="sm" variant="primary" onClick={() => onSend?.(o.id)}>Send to Vendor</Button>
              )}
            </div>
          ),
        },
      ]}
    />
  )
}
