/**
 * Vendor Detail Page
 * TODO: Fetch vendor by ID from URL params.
 */

import { useParams } from 'react-router-dom'
import { PageHeader, Card, CardHeader, StatusBadge, Breadcrumb } from '../../components/ui'

export function VendorDetailPage() {
  const { id } = useParams<{ id: string }>()

  // TODO: const { data: vendor, isLoading } = useVendor(id!)

  return (
    <div>
      <Breadcrumb items={[{ label: 'Vendors', path: '/vendors' }, { label: 'Vendor Detail' }]} />

      <PageHeader
        title="Vendor Detail"
        description={`Viewing vendor ID: ${id}`}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader title="Company Information" />
            {/* TODO: Render vendor fields */}
            <p className="text-sm text-gray-400">TODO: Vendor details — connect to API</p>
          </Card>
        </div>

        {/* Sidebar Info */}
        <div className="space-y-4">
          <Card>
            <CardHeader title="Status" />
            {/* TODO: <StatusBadge status={vendor?.status ?? 'pending'} /> */}
            <StatusBadge status="pending" />
          </Card>
        </div>
      </div>
    </div>
  )
}
