/**
 * Approvals — ApprovalQueue
 * TODO: Wire to approvalsApi and approval mutations.
 */

import type { ApprovalRequest } from '../../../types'
import { Table, StatusBadge, Button } from '../ui'

interface ApprovalQueueProps {
  approvals?: ApprovalRequest[]
  isLoading?: boolean
  onApprove?: (id: string) => void
  onReject?: (id: string) => void
}

export function ApprovalQueue({ approvals = [], isLoading, onApprove, onReject }: ApprovalQueueProps) {
  return (
    <Table
      data={approvals}
      keyExtractor={(a) => a.id}
      isLoading={isLoading}
      emptyMessage="No pending approvals. You're all caught up!"
      columns={[
        { key: 'approval_number', header: 'Approval #' },
        { key: 'approval_type',   header: 'Type',   render: (a) => a.approval_type.replace(/_/g, ' ') },
        { key: 'status',          header: 'Status', render: (a) => <StatusBadge status={a.status} /> },
        { key: 'requester_notes', header: 'Notes',  render: (a) => a.requester_notes ?? '—' },
        {
          key: 'actions',
          header: 'Actions',
          render: (a) =>
            a.status === 'pending' ? (
              <div className="flex items-center gap-2">
                <Button size="sm" variant="primary" onClick={() => onApprove?.(a.id)}>Approve</Button>
                <Button size="sm" variant="danger"  onClick={() => onReject?.(a.id)}>Reject</Button>
              </div>
            ) : null,
        },
      ]}
    />
  )
}
