/**
 * useVendors Hook
 * ================
 * React Query hooks for vendor data fetching and mutations.
 * TODO: Implement when vendorsApi is ready.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { vendorsApi } from '../api/vendors'

export const VENDOR_KEYS = {
  all: ['vendors'] as const,
  list: (params?: object) => [...VENDOR_KEYS.all, 'list', params] as const,
  detail: (id: string) => [...VENDOR_KEYS.all, 'detail', id] as const,
}

export function useVendors(params?: { status?: string; page?: number }) {
  return useQuery({
    queryKey: VENDOR_KEYS.list(params),
    queryFn: () => vendorsApi.list(params),
    enabled: false,  // TODO: Set to true when API is implemented
  })
}

export function useVendor(id: string) {
  return useQuery({
    queryKey: VENDOR_KEYS.detail(id),
    queryFn: () => vendorsApi.getById(id),
    enabled: false,  // TODO: Set to !!id when API is implemented
  })
}

export function useApproveVendor() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => vendorsApi.approve(id),
    onSuccess: () => {
      // TODO: Invalidate vendor queries, show success toast
      queryClient.invalidateQueries({ queryKey: VENDOR_KEYS.all })
    },
  })
}
