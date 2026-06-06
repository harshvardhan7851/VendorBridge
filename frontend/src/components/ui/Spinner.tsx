/**
 * Spinner — Loading indicator
 * Replaces the old LoadingSpinner.tsx at components/LoadingSpinner.tsx
 */

type SpinnerSize = 'sm' | 'md' | 'lg'

const sizeMap: Record<SpinnerSize, string> = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-4',
}

interface SpinnerProps {
  size?: SpinnerSize
  className?: string
  /** If true, centers the spinner in its container */
  centered?: boolean
}

export function Spinner({ size = 'md', className = '', centered = true }: SpinnerProps) {
  const spinner = (
    <div
      className={`animate-spin rounded-full border-blue-600 border-t-transparent ${sizeMap[size]} ${className}`}
    />
  )
  if (!centered) return spinner
  return <div className="flex items-center justify-center w-full h-full py-12">{spinner}</div>
}
