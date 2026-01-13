import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '../api/http'

interface LoginPayload {
  identifier: string
  password: string
}

interface RegisterPayload {
  email?: string
  phone?: string
  student_id?: string
  nickname: string
  password: string
}

interface User {
  id: number
  email?: string
  phone?: string
  nickname: string
  role: 'student' | 'teacher' | 'admin'
  is_active: boolean
  created_at: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const currentUser = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => Boolean(token.value))
  const isStudent = computed(() => currentUser.value?.role === 'student')
  const isTeacher = computed(() => currentUser.value?.role === 'teacher')
  const isAdmin = computed(() => currentUser.value?.role === 'admin')

  function setToken(value: string | null) {
    token.value = value
    if (value) {
      localStorage.setItem('token', value)
      apiClient.defaults.headers.common.Authorization = `Bearer ${value}`
    } else {
      localStorage.removeItem('token')
      delete apiClient.defaults.headers.common.Authorization
    }
  }

  async function register(payload: RegisterPayload) {
    loading.value = true
    error.value = null
    try {
      await apiClient.post('/auth/register', payload)
    } catch (err: any) {
      error.value = err.response?.data?.detail || '注册失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function login(payload: LoginPayload) {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<{ access_token: string; user: User }>('/auth/login', payload)
      setToken(data.access_token)
      // Save user info from login response
      if (data.user) {
        currentUser.value = data.user
      } else {
        await fetchProfile()
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || '登录失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchProfile() {
    if (!token.value) return
    try {
      const { data } = await apiClient.get<User>('/auth/me')
      currentUser.value = data
    } catch (err) {
      logout()
      throw err
    }
  }

  function logout() {
    setToken(null)
    currentUser.value = null
  }

  if (token.value) {
    apiClient.defaults.headers.common.Authorization = `Bearer ${token.value}`
    fetchProfile().catch(() => null)
  }

  return { 
    token, 
    currentUser, 
    loading, 
    error, 
    isAuthenticated, 
    isStudent,
    isTeacher,
    isAdmin,
    register, 
    login, 
    logout, 
    fetchProfile 
  }
})

