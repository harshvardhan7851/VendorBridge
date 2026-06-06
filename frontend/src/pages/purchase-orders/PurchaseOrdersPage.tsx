/**
 * Purchase Orders Page
 */

import { POTable } from '../../components/purchase-orders'
import { PageHeader } from '../../components/ui'

export function PurchaseOrdersPage() {
  return (
    <div>
      <PageHeader
        title="Purchase Orders"
        description="Track and manage issued purchase orders"
      />
      <POTable
        orders={[]}
        isLoading={false}
        // TODO: onView, onSend
      />
    </div>
  )
}
