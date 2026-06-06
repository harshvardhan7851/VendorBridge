/**
 * Vendors List Page
 * Composes: VendorTable, VendorFilters, VendorForm (in Modal)
 * TODO: Connect to useVendors() hook.
 */

import { useState } from 'react'
import { VendorTable, VendorFilters, VendorForm } from '../../components/vendors'
import { PageHeader, Modal, Button } from '../../components/ui'

export function VendorsPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false)

  // TODO: const { data, isLoading } = useVendors()
  // TODO: const { mutate: approve } = useApproveVendor()

  return (
    <div>
      <PageHeader
        title="Vendors"
        description="Manage and approve registered vendors"
        actions={
          <Button onClick={() => setIsCreateOpen(true)}>+ Register Vendor</Button>
        }
      />

      <VendorFilters />
      <VendorTable
        vendors={[]}
        isLoading={false}
        // TODO: onApprove={approve}
        // TODO: onReject={reject}
        // TODO: onView={(id) => navigate(`/vendors/${id}`)}
      />

      {/* Create Vendor Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Register New Vendor"
        size="xl"
      >
        <VendorForm onSubmit={() => setIsCreateOpen(false)} />
      </Modal>
    </div>
  )
}
