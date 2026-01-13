import apiClient from './http'
import type { AxiosResponse } from 'axios'

export interface GenerateMindmapRequest {
  chapter_name?: string
  description?: string
  knowledge_points?: string[]
  syllabus?: string  // 教学大纲
}

export interface GenerateTaskRequest {
  level_name: string
  level_description?: string
}

export interface GenerateCardsRequest {
  task_name: string
  task_description?: string
}

export interface GeneratePhasesRequest {
  task_name: string
  task_description?: string
}

export interface GenerateQuestionsRequest {
  level_name: string
  knowledge_points?: string[]
  skill_points?: string[]
}

export interface LearningHelpRequest {
  question: string
  context?: string
}

export interface GenerateSyllabusRequest {
  course_name: string
  course_requirements: string
  stream?: boolean
}

export interface GenerateTeachingGuideRequest {
  task_name: string
  course_name?: string
  requirements: string
  duration?: string
  template_type?: string
  prompt?: string
}

export interface GenerateTeachingRequirementsRequest {
  task_name: string
  course_name?: string
  template_type?: string
}

export interface TeachingGuideToCourseRequest {
  markdown: string
}

export type DataFileFormat = 'csv' | 'json' | 'txt'

export interface GenerateDataFileRequest {
  task_name: string
  data_requirements: string
  file_format: DataFileFormat
}

export interface CourseOption {
  value: string
  text: string
}

export interface CourseQuestion {
  id: string
  text: string
  options: CourseOption[]
  correctAnswer: string
  explanation?: string
  points?: number
}

export interface CoursePractice {
  title: string
  tasks: string[]
}

export interface KnowledgeCard {
  icon: string
  title: string
  content: string
}

export interface SubmissionConfig {
  enable: boolean
  title?: string
  description?: string
  successMessage?: string
}

export type StepType = 'content' | 'quiz' | 'operation' | 'summary'

export interface CourseStep {
  id: string
  type: StepType
  title: string
  subtitle?: string
  content?: string
  questions?: CourseQuestion[]
  practice?: CoursePractice
  knowledgeCard?: KnowledgeCard
  submission?: SubmissionConfig
}

export interface CourseData {
  steps: CourseStep[]
}

export const aiAssistantApi = {
  // AI生成思维导图
  generateMindmap(data: GenerateMindmapRequest): Promise<AxiosResponse<any>> {
    return apiClient.post('/ai-assistant/generate-mindmap', data)
  },

  // AI生成关卡任务
  generateTask(data: GenerateTaskRequest): Promise<AxiosResponse<any>> {
    return apiClient.post('/ai-assistant/generate-task', data)
  },

  // AI生成知识/技能卡片
  generateCards(data: GenerateCardsRequest): Promise<AxiosResponse<any>> {
    return apiClient.post('/ai-assistant/generate-cards', data)
  },

  // AI生成环节步骤
  generatePhases(data: GeneratePhasesRequest): Promise<AxiosResponse<any>> {
    return apiClient.post('/ai-assistant/generate-phases', data)
  },

  // AI生成闯关考题
  generateQuestions(data: GenerateQuestionsRequest): Promise<AxiosResponse<any>> {
    return apiClient.post('/ai-assistant/generate-questions', data)
  },

  // AI学习助手
  learningHelp(data: LearningHelpRequest): Promise<AxiosResponse<{ answer: string }>> {
    return apiClient.post('/ai-assistant/learning-help', data)
  },

  // AI生成教学大纲
  generateSyllabus(data: GenerateSyllabusRequest): Promise<AxiosResponse<{ syllabus: string }>> {
    return apiClient.post('/ai-assistant/generate-syllabus', data)
  },

  // AI生成实验指导书
  generateTeachingGuide(data: GenerateTeachingGuideRequest): Promise<AxiosResponse<{ content: string }>> {
    return apiClient.post('/ai-assistant/generate-teaching-guide', data)
  },

  // AI生成「任务要求」段落
  generateTeachingRequirements(
    data: GenerateTeachingRequirementsRequest
  ): Promise<AxiosResponse<{ requirements: string }>> {
    return apiClient.post('/ai-assistant/generate-teaching-requirements', data)
  },

  // 教案 Markdown 转交互课程 JSON
  teachingGuideToCourseJson(data: TeachingGuideToCourseRequest): Promise<AxiosResponse<CourseData>> {
    return apiClient.post('/ai-assistant/teaching-guide-to-course-json', data)
  },

  // AI 生成示例数据文件
  generateDataFile(data: GenerateDataFileRequest): Promise<
    AxiosResponse<{ filename: string; content: string; file_format: DataFileFormat; url: string }>
  > {
    return apiClient.post('/ai-assistant/generate-data-file', data)
  },
}

