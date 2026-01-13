import apiClient from './http'
import type { AxiosResponse } from 'axios'

export interface LevelMap {
  id: number
  chapter_id: number
  map_config_json?: string
}

export interface LevelMapUpdate {
  map_config_json?: string
}

export const levelMapsApi = {
  // 获取地图配置
  getMap(chapterId: number): Promise<AxiosResponse<LevelMap>> {
    return apiClient.get(`/chapters/${chapterId}/map`)
  },

  // 更新地图配置
  updateMap(chapterId: number, data: LevelMapUpdate): Promise<AxiosResponse<LevelMap>> {
    return apiClient.put(`/chapters/${chapterId}/map`, data)
  },
}

