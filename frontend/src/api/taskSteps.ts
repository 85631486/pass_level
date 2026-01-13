import apiClient from './http'
import type { AxiosResponse } from 'axios'

export interface TaskStep {
  id: number
  phase_id: number
  step_name: string
  content?: string
  requirements?: string
  submission_type: string
  validation_rules?: Record<string, any> | null
  order: number
  created_at: string
  updated_at: string
}

export interface TaskStepCreate {
  step_name: string
  content?: string
  requirements?: string
  submission_type?: string
  validation_rules?: Record<string, any> | null
  order?: number
}

export interface TaskStepUpdate {
  step_name?: string
  content?: string
  requirements?: string
  submission_type?: string
  validation_rules?: Record<string, any> | null
  order?: number
}

export const taskStepsApi = {
  getSteps(taskId: number, phaseId: number): Promise<AxiosResponse<TaskStep[]>> {
    return apiClient.get(`/tasks/${taskId}/phases/${phaseId}/steps`)
  },

  createStep(taskId: number, phaseId: number, data: TaskStepCreate): Promise<AxiosResponse<TaskStep>> {
    return apiClient.post(`/tasks/${taskId}/phases/${phaseId}/steps`, data)
  },

  updateStep(taskId: number, phaseId: number, stepId: number, data: TaskStepUpdate): Promise<AxiosResponse<TaskStep>> {
    return apiClient.put(`/tasks/${taskId}/phases/${phaseId}/steps/${stepId}`, data)
  },

  deleteStep(taskId: number, phaseId: number, stepId: number): Promise<AxiosResponse<void>> {
    return apiClient.delete(`/tasks/${taskId}/phases/${phaseId}/steps/${stepId}`)
  },
}

















