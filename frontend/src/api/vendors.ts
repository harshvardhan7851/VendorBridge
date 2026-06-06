/**
 * Vendors API — Placeholder functions.
 */

import apiClient from './client'
import type { Vendor, PaginatedResponse } from '../types'

export const vendorsApi = {
  list: async (params?: { status?: string; page?: number }): Promise<PaginatedResponse<Vendor>> => {
    // TODO: const { data } = await apiClient.get('/vendors', { params })
    throw new Error('Not implemented')
  },

  getById: async (id: string): Promise<Vendor> => {
    // TODO: const { data } = await apiClient.get(`/vendors/${id}`)
    throw new Error('Not implemented')
  },

  create: async (payload: Partial<Vendor>): Promise<Vendor> => {
    // TODO: const { data } = await apiClient.post('/vendors', payload)
    throw new Error('Not implemented')
  },

  update: async (id: string, payload: Partial<Vendor>): Promise<Vendor> => {
    // TODO: const { data } = await apiClient.put(`/vendors/${id}`, payload)
    throw new Error('Not implemented')
  },

  approve: async (id: string): Promise<void> => {
    // TODO: await apiClient.post(`/vendors/${id}/approve`)
    throw new Error('Not implemented')
  },

  reject: async (id: string, reason: string): Promise<void> => {
    // TODO: await apiClient.post(`/vendors/${id}/reject`, { reason })
    throw new Error('Not implemented')
  },
}
