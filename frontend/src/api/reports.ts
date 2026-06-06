/**
 * Reports API — Placeholder functions.
 */

export const reportsApi = {
  spendByVendor: async (params?: object): Promise<unknown> => {
    // TODO: const { data } = await apiClient.get('/reports/spend-by-vendor', { params })
    throw new Error('Not implemented')
  },

  rfqSummary: async (params?: object): Promise<unknown> => {
    // TODO: const { data } = await apiClient.get('/reports/rfq-summary', { params })
    throw new Error('Not implemented')
  },

  approvalCycleTime: async (): Promise<unknown> => {
    throw new Error('Not implemented')
  },

  vendorPerformance: async (): Promise<unknown> => {
    throw new Error('Not implemented')
  },

  exportPdf: async (reportType: string, params?: object): Promise<Blob> => {
    // TODO: const { data } = await apiClient.get('/reports/export/pdf', {
    //   params: { type: reportType, ...params },
    //   responseType: 'blob'
    // })
    throw new Error('Not implemented')
  },
}
