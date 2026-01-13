import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    const message = error.response?.data?.message || '网络错误'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default {
  // 认证相关
  login(data) {
    return api.post('/auth/login', data)
  },
  register(data) {
    return api.post('/auth/register', data)
  },

  // 任务相关
  getTasks(courseId) {
    return api.get('/tasks', { params: { course_id: courseId } })
  },
  getTaskDetail(taskId) {
    return api.get(`/tasks/${taskId}`)
  },

  // 操作相关
  getOperationDetail(operationId) {
    return api.get(`/operations/${operationId}`)
  },
  submitOperation(operationId, formData) {
    return api.post(`/operations/${operationId}/submit`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 测试题相关
  answerInstantQuestion(questionId, data) {
    return api.post(`/questions/instant/${questionId}/answer`, data)
  },
  getUnifiedQuestions(taskId) {
    return api.get(`/tasks/${taskId}/unified-questions`)
  },
  submitUnifiedTest(taskId, data) {
    return api.post(`/tasks/${taskId}/unified-test/submit`, data)
  },

  // 进度相关
  startTask(data) {
    return api.post('/progress/start', data)
  },
  getProgress(studentId, taskId) {
    return api.get(`/progress/${studentId}/${taskId}`)
  },
  completeTask(data) {
    return api.post('/progress/complete', data)
  },

  // 知识卡片相关
  collectKnowledgeCard(data) {
    return api.post('/knowledge-cards/collect', data)
  },
  getCollectedCards(studentId) {
    return api.get(`/knowledge-cards/${studentId}`)
  },

  // 徽章相关
  getStudentBadges(studentId) {
    return api.get(`/badges/${studentId}`)
  },

  // 学习总结
  getLearningSummary(studentId, taskId) {
    return api.get(`/summary/${studentId}/${taskId}`)
  }
}
