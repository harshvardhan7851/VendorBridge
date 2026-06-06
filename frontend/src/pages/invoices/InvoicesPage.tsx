/**
 * Invoices Page
 */

import { InvoiceTable } from '../../components/invoices'
import { PageHeader } from '../../components/ui'

export function InvoicesPage() {
  return (
    <div>
      <PageHeader
        title="Invoices"
        description="Review and process vendor invoices"
      />
      <InvoiceTable
        invoices={[]}
        isLoading={false}
        // TODO: onView, onApprove, onReject
      />
    </div>
  )
}
