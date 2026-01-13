import apiClient from './http'
import type { AxiosResponse } from 'axios'

export interface Question {
  id: number
  level_id: number
  question_type: string
  title: string
  content?: string
  options?: string[] | null
  correct_answer?: string
  answer_analysis?: string
  difficulty: string
  score: number
  knowledge_point?: string
  tags?: string[] | null
  created_at: string
  updated_at: string
}

export interface QuestionCreate {
  question_type: string
  title: string
  content?: string
  options?: string[] | null
  correct_answer?: string
  answer_analysis?: string
  difficulty?: string
  score?: number
  knowledge_point?: string
  tags?: string[] | null
  task_id?: number
  order?: number
}

export interface QuestionUpdate {
  question_type?: string
  title?: string
  content?: string
  options?: string[] | null
  correct_answer?: string
  answer_analysis?: string
  difficulty?: string
  score?: number
  knowledge_point?: string
  tags?: string[] | null
}

export const questionsApi = {
  getQuestions(levelId: number): Promise<AxiosResponse<Question[]>> {
    return apiClient.get(`/levels/${levelId}/questions`)
  },

  createQuestion(levelId: number, data: QuestionCreate): Promise<AxiosResponse<Question>> {
    return apiClient.post(`/levels/${levelId}/questions`, data)
  },

  getQuestion(id: number): Promise<AxiosResponse<Question>> {
    return apiClient.get(`/questions/${id}`)
  },

  updateQuestion(id: number, data: QuestionUpdate): Promise<AxiosResponse<Question>> {
    return apiClient.put(`/questions/${id}`, data)
  },

  deleteQuestion(id: number): Promise<AxiosResponse<void>> {
    return apiClient.delete(`/questions/${id}`)
  },
}

















