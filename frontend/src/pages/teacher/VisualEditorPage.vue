<template>
  <div class="visual-editor-page">
    <div class="page-header">
      <button class="btn-back" @click="goBack">← 返回关卡编辑</button>
      <h2>可视化编辑器：{{ level?.name || '加载中...' }}</h2>
    </div>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">
      <p>加载失败：{{ error }}</p>
      <button @click="loadData">重试</button>
    </div>
    <VisualCourseEditor
      v-else-if="level"
      :level-id="levelId"
      :initial-data="courseData"
      @save="handleSave"
      @preview="handlePreview"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import VisualCourseEditor from '../../components/VisualCourseEditor.vue'
import { levelsApi } from '../../api/levels'
import type { Level } from '../../api/levels'
import type { CourseData } from '../../types/coursePlayer'

const route = useRoute()
const router = useRouter()
const levelId = Number(route.params.levelId)

const level = ref<Level | null>(null)
const courseData = ref<CourseData | null>(null)

const loading = ref(true)
const error = ref<string | null>(null)

const loadData = async () => {
  loading.value = true
  error.value = null
  try {
    const levelResp = await levelsApi.getLevel(levelId)
    level.value = levelResp.data

    const courseResp = await levelsApi.getCourseData(levelId)
    if (courseResp.data) {
      courseData.value = courseResp.data
    } else {
      // 如果没有课程数据，初始化为空结构
      courseData.value = {
        steps: [],
        meta: {}
      }
    }
  } catch (err: any) {
    console.error('Failed to load data:', err)
    error.value = err.response?.data?.detail || err.message || '加载数据失败'
    alert('加载数据失败：' + error.value)
    // 即使加载失败，也初始化为空结构，允许用户创建新内容
    courseData.value = {
      steps: [],
      meta: {}
    }
  } finally {
    loading.value = false
  }
}

const handleSave = (data: CourseData) => {
  console.log('Course data saved:', data)
}

const handlePreview = (data: CourseData) => {
  // 保存到localStorage并打开预览
  localStorage.setItem('levelInteractivePreviewData', JSON.stringify(data))
  const resolved = router.resolve({ name: 'level-interactive-preview' })
  const routeUrl = `${window.location.origin}${resolved.href}`
  window.open(routeUrl, 'interactivePreviewWindow', 'width=1400,height=900')
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.visual-editor-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
  padding: 1rem 2rem;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-back {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-back:hover {
  text-decoration: underline;
}

.page-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 1.2rem;
  color: #6b7280;
}

.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 1rem;
  color: #dc2626;
}

.error button {
  padding: 0.5rem 1rem;
  border: 1px solid #dc2626;
  border-radius: 4px;
  background: #fee2e2;
  color: #dc2626;
  cursor: pointer;
}
</style>

