/**
 * Approvals Page
 * Role-gated: admin, manager only
 */

import { ApprovalQueue } from '../../components/approvals'
import { PageHeader } from '../../components/ui'

export function ApprovalsPage() {
  return (
    <div>
      <PageHeader
        title="Approval Requests"
        description="Review and action pending approvals"
      />
      <ApprovalQueue
        approvals={[]}
        isLoading={false}
        // TODO: onApprove, onReject
      />
    </div>
  )
}
