/**
 * RFQs List Page
 * Composes: RFQTable, RFQForm (in Modal)
 */

import { useState } from 'react'
import { RFQTable, RFQForm } from '../../components/rfqs'
import { PageHeader, Modal, Button } from '../../components/ui'

export function RFQsPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false)

  // TODO: const { data, isLoading } = useRFQs()

  return (
    <div>
      <PageHeader
        title="Requests for Quotation"
        description="Create and manage RFQs sent to vendors"
        actions={
          <Button onClick={() => setIsCreateOpen(true)}>+ Create RFQ</Button>
        }
      />

      <RFQTable
        rfqs={[]}
        isLoading={false}
        // TODO: onView={(id) => navigate(`/rfqs/${id}`)}
        // TODO: onPublish={publishRFQ}
      />

      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create New RFQ" size="xl">
        <RFQForm onSubmit={() => setIsCreateOpen(false)} />
      </Modal>
    </div>
  )
}
