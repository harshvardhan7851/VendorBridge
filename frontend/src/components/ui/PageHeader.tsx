/**
 * PageHeader — Section title + actions row
 * Replaces the old PageHeader.tsx at components/PageHeader.tsx
 */

import React from 'react'

interface PageHeaderProps {
  title: string
  description?: string
  /** Action buttons slot (right-aligned) */
  actions?: React.ReactNode
  /** Breadcrumb slot (above title) */
  breadcrumb?: React.ReactNode
}

export function PageHeader({ title, description, actions, breadcrumb }: PageHeaderProps) {
  return (
    <div className="mb-6">
      {breadcrumb && <div className="mb-1">{breadcrumb}</div>}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </div>
  )
}
