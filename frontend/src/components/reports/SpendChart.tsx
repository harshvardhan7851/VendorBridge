/**
 * Reports — SpendChart placeholder
 * TODO: Implement with recharts or chart.js.
 */

import { Card, CardHeader } from '../ui'

interface SpendChartProps {
  title?: string
}

export function SpendChart({ title = 'Spend by Vendor' }: SpendChartProps) {
  return (
    <Card>
      <CardHeader title={title} description="Monthly procurement spend breakdown" />
      <div className="h-64 flex items-center justify-center text-gray-400 text-sm border-2 border-dashed border-gray-200 rounded-lg">
        {/* TODO: Render recharts BarChart or PieChart here */}
        📊 Chart placeholder — connect to reportsApi.spendByVendor()
      </div>
    </Card>
  )
}
