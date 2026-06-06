/**
 * Dashboard Page
 * Composes: KPICard, RecentActivity from components/dashboard/
 * TODO: Fetch real KPI data from reportsApi.
 */

import { KPICard, RecentActivity } from '../../components/dashboard'
import { PageHeader } from '../../components/ui'

// Placeholder KPI data — replace with real API data
const PLACEHOLDER_KPIS = [
  { title: 'Active Vendors',    value: '—', icon: '🏢', subtitle: 'TODO: fetch from API' },
  { title: 'Open RFQs',        value: '—', icon: '📋', subtitle: 'TODO: fetch from API' },
  { title: 'Pending Approvals',value: '—', icon: '✅', subtitle: 'TODO: fetch from API' },
  { title: 'Invoices Due',      value: '—', icon: '🧾', subtitle: 'TODO: fetch from API' },
]

export function DashboardPage() {
  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Procurement overview and quick actions"
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {PLACEHOLDER_KPIS.map((kpi) => (
          <KPICard key={kpi.title} {...kpi} />
        ))}
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentActivity items={[]} />
        {/* TODO: Add PendingApprovalsSummary, RFQStatusChart etc. */}
      </div>
    </div>
  )
}
