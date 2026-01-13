import apiClient from './http'
import type { AxiosResponse } from 'axios'

export interface Chapter {
  id: number
  name: string
  description?: string
  teacher_id: number
  created_at: string
  updated_at: string
}

export interface ChapterCreate {
  name: string
  description?: string
}

export interface ChapterUpdate {
  name?: string
  description?: string
}

export const chaptersApi = {
  // 获取篇章列表
  getChapters(): Promise<AxiosResponse<Chapter[]>> {
    return apiClient.get('/chapters')
  },

  // 获取篇章详情
  getChapter(id: number): Promise<AxiosResponse<Chapter>> {
    return apiClient.get(`/chapters/${id}`)
  },

  // 创建篇章
  createChapter(data: ChapterCreate): Promise<AxiosResponse<Chapter>> {
    return apiClient.post('/chapters', data)
  },

  // 更新篇章
  updateChapter(id: number, data: ChapterUpdate): Promise<AxiosResponse<Chapter>> {
    return apiClient.put(`/chapters/${id}`, data)
  },

  // 删除篇章
  deleteChapter(id: number): Promise<AxiosResponse<void>> {
    return apiClient.delete(`/chapters/${id}`)
  },
}

