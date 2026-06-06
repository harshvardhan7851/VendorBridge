/**
 * Vendors — VendorForm
 * TODO: Add react-hook-form + zod validation.
 */

import { Button, Input } from '../ui'

interface VendorFormProps {
  initialValues?: Partial<Record<string, string>>
  onSubmit?: (data: object) => void
  isLoading?: boolean
}

export function VendorForm({ onSubmit, isLoading }: VendorFormProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Collect form values and call onSubmit(data)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Input label="Company Name"          id="vendor-company"   placeholder="Acme Corp" />
        <Input label="Registration Number"   id="vendor-regnum"    placeholder="REG-12345" />
        <Input label="Tax ID"                id="vendor-taxid"     placeholder="GST/VAT number" />
        <Input label="Email"                 id="vendor-email"     type="email" placeholder="contact@acme.com" />
        <Input label="Phone"                 id="vendor-phone"     type="tel"   placeholder="+1 (555) 000-0000" />
        <Input label="Website"               id="vendor-website"   type="url"   placeholder="https://acme.com" />
        <Input label="Category"              id="vendor-category"  placeholder="IT / Logistics / Office Supplies" />
        <Input label="City"                  id="vendor-city"      placeholder="New York" />
        <Input label="Country"               id="vendor-country"   placeholder="United States" />
        <Input label="Postal Code"           id="vendor-postal"    placeholder="10001" />
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="vendor-description" className="text-sm font-medium text-gray-700">Description</label>
        <textarea
          id="vendor-description"
          rows={3}
          placeholder="Brief description of the vendor's products or services..."
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline">Cancel</Button>
        <Button type="submit" variant="primary" isLoading={isLoading}>
          Register Vendor
        </Button>
      </div>
    </form>
  )
}
