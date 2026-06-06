/**
 * useRFQs Hook
 * ============
 * React Query hooks for RFQ data fetching and mutations.
 * TODO: Implement when rfqsApi is ready.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { rfqsApi } from '../api/rfqs'

export const RFQ_KEYS = {
  all: ['rfqs'] as const,
  list: (params?: object) => [...RFQ_KEYS.all, 'list', params] as const,
  detail: (id: string) => [...RFQ_KEYS.all, 'detail', id] as const,
}

export function useRFQs(params?: { status?: string; page?: number }) {
  return useQuery({
    queryKey: RFQ_KEYS.list(params),
    queryFn: () => rfqsApi.list(params),
    enabled: false,
  })
}

export function useRFQ(id: string) {
  return useQuery({
    queryKey: RFQ_KEYS.detail(id),
    queryFn: () => rfqsApi.getById(id),
    enabled: false,
  })
}

export function useCreateRFQ() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: rfqsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: RFQ_KEYS.all })
      // TODO: Show success notification
    },
  })
}
