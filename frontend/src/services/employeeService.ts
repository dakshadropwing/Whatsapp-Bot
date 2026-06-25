import { api } from './api'
import type { Employee, PaginatedResponse } from '@/types'

export const employeeService = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Employee>>('/employees/', params).then(r => r.data),

  get: (id: string) =>
    api.get<{ employee: Employee }>(`/employees/${id}`).then(r => r.data),

  create: (data: Partial<Employee>) =>
    api.post<Employee>('/employees/', data).then(r => r.data),

  update: (id: string, data: Partial<Employee>) =>
    api.patch(`/employees/${id}`, data).then(r => r.data),

  delete: (id: string) =>
    api.delete(`/employees/${id}`).then(r => r.data),
}
