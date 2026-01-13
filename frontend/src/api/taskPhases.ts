import apiClient from './http'
import type { AxiosResponse } from 'axios'

export interface TaskPhase {
  id: number
  task_id: number
  phase_name: string
  order: number
  is_required: boolean
  created_at: string
  updated_at: string
}

export interface TaskPhaseCreate {
  phase_name: string
  order?: number
  is_required?: boolean
}

export interface TaskPhaseUpdate {
  phase_name?: string
  order?: number
  is_required?: boolean
}

export const taskPhasesApi = {
  getPhases(taskId: number): Promise<AxiosResponse<TaskPhase[]>> {
    return apiClient.get(`/tasks/${taskId}/phases`)
  },

  createPhase(taskId: number, data: TaskPhaseCreate): Promise<AxiosResponse<TaskPhase>> {
    return apiClient.post(`/tasks/${taskId}/phases`, data)
  },

  updatePhase(taskId: number, phaseId: number, data: TaskPhaseUpdate): Promise<AxiosResponse<TaskPhase>> {
    return apiClient.put(`/tasks/${taskId}/phases/${phaseId}`, data)
  },

  deletePhase(taskId: number, phaseId: number): Promise<AxiosResponse<void>> {
    return apiClient.delete(`/tasks/${taskId}/phases/${phaseId}`)
  },
}

















