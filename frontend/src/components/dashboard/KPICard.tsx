/**
 * Dashboard — KPICard
 * TODO: Connect to real metrics from the reports API.
 */

import { Card } from '../ui'

interface KPICardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: string
  trend?: { value: number; isPositive: boolean }
}

export function KPICard({ title, value, subtitle, icon, trend }: KPICardProps) {
  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="mt-1 text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && <p className="mt-1 text-xs text-gray-400">{subtitle}</p>}
          {trend && (
            <p className={`mt-2 text-xs font-medium ${trend.isPositive ? 'text-green-600' : 'text-red-500'}`}>
              {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}% vs last month
            </p>
          )}
        </div>
        {icon && (
          <span className="text-3xl p-2 rounded-xl bg-blue-50">{icon}</span>
        )}
      </div>
    </Card>
  )
}
