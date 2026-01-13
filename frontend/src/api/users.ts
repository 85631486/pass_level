import apiClient from './http'

export interface User {
  id: number
  email?: string
  phone?: string
  student_id?: string
  nickname: string
  role: 'student' | 'teacher' | 'admin'
  is_active: boolean
  class_name?: string  // 班级
  notes?: string  // 备注
  created_at: string
}

export interface UserListResponse {
  items: User[]
  total: number
  skip: number
  limit: number
}

export interface CreateUserPayload {
  email?: string
  phone?: string
  student_id?: string
  nickname: string
  password: string
  role: 'student' | 'teacher' | 'admin'
  class_name?: string  // 班级
  notes?: string  // 备注
}

export interface UpdateUserPayload {
  email?: string
  phone?: string
  student_id?: string
  nickname?: string
  password?: string
  role?: 'student' | 'teacher' | 'admin'
  is_active?: boolean
  class_name?: string  // 班级
  notes?: string  // 备注
}

export const userApi = {
  // Get user list
  getUsers: (params?: { role?: string; search?: string; skip?: number; limit?: number }) => {
    return apiClient.get<UserListResponse>('/admin/users', { params })
  },

  // Get user by ID
  getUser: (userId: number) => {
    return apiClient.get<User>(`/admin/users/${userId}`)
  },

  // Create user
  createUser: (payload: CreateUserPayload) => {
    return apiClient.post<User>('/admin/users', payload)
  },

  // Update user
  updateUser: (userId: number, payload: UpdateUserPayload) => {
    return apiClient.put<User>(`/admin/users/${userId}`, payload)
  },

  // Delete user (soft delete)
  deleteUser: (userId: number) => {
    return apiClient.delete(`/admin/users/${userId}`)
  },
}

