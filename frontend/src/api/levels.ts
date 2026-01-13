import apiClient from './http'
import type { AxiosResponse } from 'axios'

export interface Level {
  id: number
  chapter_id: number
  name: string
  description?: string
  order: number
  is_visible: boolean
  is_published: boolean
  published_at?: string
  teaching_guide_md?: string
  created_at: string
  updated_at: string
}

export interface LevelCreate {
  chapter_id: number
  name: string
  description?: string
  order?: number
}

export interface LevelUpdate {
  name?: string
  description?: string
  order?: number
  is_visible?: boolean
  teaching_guide_md?: string
}

export interface TreasureChestCreate {
  level_id: number
  name: string
  position_x: number
  position_y: number
  reward_config: any
}

export interface TreasureChest {
  id: number
  level_id: number
  name: string
  position_x: number
  position_y: number
  reward_config: any
  created_at: string
  updated_at: string
}

export const levelsApi = {
  // 获取篇章下的关卡列表
  getLevels(chapterId: number): Promise<AxiosResponse<Level[]>> {
    return apiClient.get(`/chapters/${chapterId}/levels`)
  },

  // 获取关卡详情
  getLevel(id: number): Promise<AxiosResponse<Level>> {
    return apiClient.get(`/levels/${id}`)
  },

  // 创建关卡
  createLevel(chapterId: number, data: LevelCreate): Promise<AxiosResponse<Level>> {
    return apiClient.post(`/chapters/${chapterId}/levels`, data)
  },

  // 更新关卡
  updateLevel(id: number, data: LevelUpdate): Promise<AxiosResponse<Level>> {
    return apiClient.put(`/levels/${id}`, data)
  },

  // 删除关卡
  deleteLevel(id: number): Promise<AxiosResponse<void>> {
    return apiClient.delete(`/levels/${id}`)
  },

  // 在关卡上创建宝箱
  createTreasureChest(levelId: number, data: TreasureChestCreate): Promise<AxiosResponse<TreasureChest>> {
    return apiClient.post(`/levels/${levelId}/treasure-chests`, data)
  },

  // 获取课程数据
  getCourseData(levelId: number): Promise<AxiosResponse<any>> {
    return apiClient.get(`/levels/${levelId}/course-data`)
  },

  // 更新课程数据
  updateCourseData(levelId: number, courseData: any): Promise<AxiosResponse<any>> {
    return apiClient.put(`/levels/${levelId}/course-data`, { course_data: courseData })
  },

  // 同步到MD
  syncToMD(levelId: number): Promise<AxiosResponse<any>> {
    return apiClient.post(`/levels/${levelId}/sync-md`)
  },
}

