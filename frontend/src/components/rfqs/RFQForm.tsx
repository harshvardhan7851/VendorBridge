/**
 * RFQs — RFQForm
 * TODO: Implement with dynamic line item add/remove.
 */

import { Button, Input } from '../ui'

interface RFQFormProps {
  onSubmit?: (data: object) => void
  isLoading?: boolean
}

export function RFQForm({ onSubmit, isLoading }: RFQFormProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Collect line items array and submit
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Basic Info */}
      <section className="space-y-4">
        <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">RFQ Details</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="sm:col-span-2">
            <Input label="Title" id="rfq-title" placeholder="e.g. Office Furniture Q1 2025" />
          </div>
          <Input label="Category"            id="rfq-category"  placeholder="IT / Furniture..." />
          <Input label="Submission Deadline" id="rfq-deadline"  type="date" />
          <Input label="Expected Delivery"   id="rfq-delivery"  type="date" />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="rfq-desc" className="text-sm font-medium text-gray-700">Description</label>
          <textarea id="rfq-desc" rows={3} className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </section>

      {/* Line Items */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Line Items</h3>
          <Button type="button" variant="outline" size="sm">+ Add Item</Button>
          {/* TODO: Implement dynamic line item rows */}
        </div>
        <div className="border border-dashed border-gray-300 rounded-lg p-4 text-center text-sm text-gray-400">
          No line items yet. Click "+ Add Item" to begin.
          {/* TODO: Render line item rows dynamically */}
        </div>
      </section>

      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline">Save as Draft</Button>
        <Button type="submit" variant="primary" isLoading={isLoading}>Create RFQ</Button>
      </div>
    </form>
  )
}
