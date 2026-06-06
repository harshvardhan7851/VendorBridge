/**
 * RFQs API — Placeholder functions.
 */

import apiClient from './client'
import type { RFQ, PaginatedResponse } from '../types'

export const rfqsApi = {
  list: async (params?: { status?: string; page?: number }): Promise<PaginatedResponse<RFQ>> => {
    // TODO: const { data } = await apiClient.get('/rfqs', { params })
    throw new Error('Not implemented')
  },

  getById: async (id: string): Promise<RFQ> => {
    // TODO: const { data } = await apiClient.get(`/rfqs/${id}`)
    throw new Error('Not implemented')
  },

  create: async (payload: Partial<RFQ>): Promise<RFQ> => {
    // TODO: const { data } = await apiClient.post('/rfqs', payload)
    throw new Error('Not implemented')
  },

  update: async (id: string, payload: Partial<RFQ>): Promise<RFQ> => {
    // TODO: const { data } = await apiClient.put(`/rfqs/${id}`, payload)
    throw new Error('Not implemented')
  },

  publish: async (id: string, vendorIds: string[]): Promise<void> => {
    // TODO: await apiClient.post(`/rfqs/${id}/publish`, { vendor_ids: vendorIds })
    throw new Error('Not implemented')
  },

  cancel: async (id: string): Promise<void> => {
    // TODO: await apiClient.delete(`/rfqs/${id}`)
    throw new Error('Not implemented')
  },
}
