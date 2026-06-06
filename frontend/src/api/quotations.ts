/**
 * Quotations API — Placeholder functions.
 */
import apiClient from './client'
import type { Quotation, PaginatedResponse } from '../types'

export const quotationsApi = {
  list: async (params?: object): Promise<PaginatedResponse<Quotation>> => {
    throw new Error('Not implemented')
    // TODO: const { data } = await apiClient.get('/quotations', { params })
  },
  getById: async (id: string): Promise<Quotation> => {
    throw new Error('Not implemented')
  },
  create: async (payload: Partial<Quotation>): Promise<Quotation> => {
    throw new Error('Not implemented')
  },
  update: async (id: string, payload: Partial<Quotation>): Promise<Quotation> => {
    throw new Error('Not implemented')
  },
  award: async (id: string): Promise<void> => {
    // TODO: await apiClient.post(`/quotations/${id}/award`)
    throw new Error('Not implemented')
  },
}
