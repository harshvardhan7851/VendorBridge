/**
 * Invoices API — Placeholder functions.
 */
import type { Invoice, PaginatedResponse } from '../types'

export const invoicesApi = {
  list: async (params?: object): Promise<PaginatedResponse<Invoice>> => {
    throw new Error('Not implemented')
  },
  getById: async (id: string): Promise<Invoice> => {
    throw new Error('Not implemented')
  },
  create: async (payload: Partial<Invoice>): Promise<Invoice> => {
    throw new Error('Not implemented')
  },
  approve: async (id: string): Promise<void> => {
    throw new Error('Not implemented')
  },
  reject: async (id: string, reason: string): Promise<void> => {
    throw new Error('Not implemented')
  },
}
