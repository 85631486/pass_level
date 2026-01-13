import apiClient from './http'
import type { AxiosResponse } from 'axios'

export interface Task {
  id: number
  level_id: number
  name: string
  description?: string
  objective?: string
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  name: string
  description?: string
  objective?: string
}

export interface TaskUpdate {
  name?: string
  description?: string
  objective?: string
}

export const tasksApi = {
  getTasks(levelId: number): Promise<AxiosResponse<Task[]>> {
    return apiClient.get(`/levels/${levelId}/tasks`)
  },

  createTask(levelId: number, data: TaskCreate): Promise<AxiosResponse<Task>> {
    return apiClient.post(`/levels/${levelId}/tasks`, data)
  },

  getTask(id: number): Promise<AxiosResponse<Task>> {
    return apiClient.get(`/tasks/${id}`)
  },

  updateTask(id: number, data: TaskUpdate): Promise<AxiosResponse<Task>> {
    return apiClient.put(`/tasks/${id}`, data)
  },

  deleteTask(id: number): Promise<AxiosResponse<void>> {
    return apiClient.delete(`/tasks/${id}`)
  },
}

















