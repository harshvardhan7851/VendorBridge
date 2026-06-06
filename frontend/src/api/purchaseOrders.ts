/**
 * Purchase Orders API — Placeholder functions.
 */
import type { PurchaseOrder, PaginatedResponse } from '../types'

export const purchaseOrdersApi = {
  list: async (params?: object): Promise<PaginatedResponse<PurchaseOrder>> => {
    throw new Error('Not implemented')
  },
  getById: async (id: string): Promise<PurchaseOrder> => {
    throw new Error('Not implemented')
  },
  create: async (payload: Partial<PurchaseOrder>): Promise<PurchaseOrder> => {
    throw new Error('Not implemented')
  },
  update: async (id: string, payload: Partial<PurchaseOrder>): Promise<PurchaseOrder> => {
    throw new Error('Not implemented')
  },
  send: async (id: string): Promise<void> => {
    // TODO: await apiClient.post(`/purchase-orders/${id}/send`)
    throw new Error('Not implemented')
  },
}
