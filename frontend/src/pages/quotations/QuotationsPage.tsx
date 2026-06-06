/**
 * Quotations Page
 */

import { QuotationTable } from '../../components/quotations'
import { PageHeader } from '../../components/ui'

export function QuotationsPage() {
  return (
    <div>
      <PageHeader
        title="Quotations"
        description="Review and award vendor quotations"
      />
      <QuotationTable
        quotations={[]}
        isLoading={false}
        // TODO: onView, onAward
      />
    </div>
  )
}
