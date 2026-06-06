/**
 * Reports Page
 * Role-gated: admin only
 */

import { SpendChart } from '../../components/reports'
import { PageHeader, Button } from '../../components/ui'

export function ReportsPage() {
  return (
    <div>
      <PageHeader
        title="Reports & Analytics"
        description="Procurement insights and spend analytics"
        actions={<Button variant="outline">📥 Export PDF</Button>}
      />

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <SpendChart title="Spend by Vendor" />
        <SpendChart title="RFQ Status Distribution" />
        {/* TODO: VendorPerformanceChart, ApprovalCycleTimeChart */}
      </div>
    </div>
  )
}
