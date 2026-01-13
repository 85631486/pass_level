import apiClient from './http'
import type { AxiosResponse } from 'axios'

export interface StudentSkill {
  skill_node_id: number
  skill_name: string
  skill_description?: string
  level: number
  experience: number
  parent_id?: number
}

export interface StudentProfile {
  user_id: number
  level: number
  experience: number
  total_score: number
  skills: StudentSkill[]
}

export const studentsApi = {
  // 获取学生档案和技能树
  getProfile(userId: number): Promise<AxiosResponse<StudentProfile>> {
    return apiClient.get(`/students/${userId}/profile`)
  },
}

