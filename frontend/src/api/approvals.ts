/**
 * Approvals API — Placeholder functions.
 */
import type { ApprovalRequest, PaginatedResponse } from '../types'

export const approvalsApi = {
  list: async (params?: object): Promise<PaginatedResponse<ApprovalRequest>> => {
    throw new Error('Not implemented')
  },
  getById: async (id: string): Promise<ApprovalRequest> => {
    throw new Error('Not implemented')
  },
  approve: async (id: string, comments?: string): Promise<void> => {
    // TODO: await apiClient.post(`/approvals/${id}/approve`, { comments })
    throw new Error('Not implemented')
  },
  reject: async (id: string, comments: string): Promise<void> => {
    // TODO: await apiClient.post(`/approvals/${id}/reject`, { comments })
    throw new Error('Not implemented')
  },
}
