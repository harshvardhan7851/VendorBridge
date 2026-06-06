/**
 * Vendors — VendorTable
 * TODO: Wire to useVendors() hook and connect approve/reject actions.
 */

import type { Vendor } from '../../../types'
import { Table, StatusBadge, Button } from '../ui'

interface VendorTableProps {
  vendors?: Vendor[]
  isLoading?: boolean
  onApprove?: (id: string) => void
  onReject?: (id: string) => void
  onView?: (id: string) => void
}

export function VendorTable({ vendors = [], isLoading, onApprove, onReject, onView }: VendorTableProps) {
  return (
    <Table
      data={vendors}
      keyExtractor={(v) => v.id}
      isLoading={isLoading}
      emptyMessage="No vendors found. Register the first vendor to get started."
      columns={[
        { key: 'company_name', header: 'Company' },
        { key: 'email',        header: 'Email' },
        { key: 'category',     header: 'Category' },
        { key: 'city',         header: 'Location', render: (v) => [v.city, v.country].filter(Boolean).join(', ') || '—' },
        { key: 'status',       header: 'Status',   render: (v) => <StatusBadge status={v.status} /> },
        {
          key: 'actions',
          header: 'Actions',
          render: (v) => (
            <div className="flex items-center gap-2">
              <Button size="sm" variant="ghost" onClick={() => onView?.(v.id)}>View</Button>
              {v.status === 'pending' && (
                <>
                  <Button size="sm" variant="primary"  onClick={() => onApprove?.(v.id)}>Approve</Button>
                  <Button size="sm" variant="danger"   onClick={() => onReject?.(v.id)}>Reject</Button>
                </>
              )}
            </div>
          ),
        },
      ]}
    />
  )
}
