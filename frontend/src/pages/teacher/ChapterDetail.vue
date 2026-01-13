<template>
  <div class="chapter-detail-page">
    <div class="page-header">
      <div class="header-left">
        <button class="btn-back" @click="handleBack">
          <span class="back-icon">←</span>
          <span>返回</span>
        </button>
        <div class="header-info">
          <h1 class="page-title">{{ chapter?.name || '加载中...' }}</h1>
          <p class="page-subtitle" v-if="chapter">篇章详情与关卡管理</p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-primary" @click="handleEdit">
          <span>✏️</span>
          <span>编辑篇章</span>
        </button>
      </div>
    </div>
    
    <div class="page-content">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <div class="error-icon">⚠️</div>
        <p class="error-message">{{ error }}</p>
        <button class="btn-retry" @click="fetchChapter">重试</button>
      </div>
      
      <div v-else-if="chapter" class="detail-content">
        <div class="info-card">
          <div class="card-header">
            <h3 class="card-title">📚 篇章信息</h3>
          </div>
          <div class="card-body">
            <div class="info-item">
              <label class="info-label">篇章名称</label>
              <div class="info-value">{{ chapter.name }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">篇章描述</label>
              <div class="info-value">{{ chapter.description || '暂无描述' }}</div>
            </div>
            <div class="info-row">
              <div class="info-item">
                <label class="info-label">创建时间</label>
                <div class="info-value">{{ formatDate(chapter.created_at) }}</div>
              </div>
              <div class="info-item">
                <label class="info-label">更新时间</label>
                <div class="info-value">{{ formatDate(chapter.updated_at) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑对话框 -->
    <ChapterForm
      v-if="showEditDialog"
      :chapter="chapter"
      @close="showEditDialog = false"
      @saved="handleSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { chaptersApi, type Chapter } from '../../api/chapters'
import ChapterForm from './ChapterForm.vue'

const route = useRoute()
const router = useRouter()
const chapter = ref<Chapter | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const showEditDialog = ref(false)

const fetchChapter = async () => {
  const chapterId = parseInt(route.params.id as string)
  if (!chapterId) {
    error.value = '无效的篇章ID'
    return
  }
  
  loading.value = true
  error.value = null
  try {
    const response = await chaptersApi.getChapter(chapterId)
    chapter.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || '加载篇章详情失败'
    console.error('Error fetching chapter:', err)
  } finally {
    loading.value = false
  }
}

const handleBack = () => {
  router.push('/teacher/chapters')
}

const handleEdit = () => {
  showEditDialog.value = true
}

const handleSaved = () => {
  showEditDialog.value = false
  fetchChapter()
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchChapter()
})
</script>

<style scoped>
.chapter-detail-page {
  width: 100%;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #e2e8f0;
}

.header-left {
  flex: 1;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  color: #475569;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-back:hover {
  background: #e2e8f0;
  color: #334155;
  transform: translateX(-2px);
}

.back-icon {
  font-size: 1.2rem;
}

.header-info {
  flex: 1;
}

.page-title {
  margin: 0 0 0.5rem;
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  margin: 0;
  font-size: 0.95rem;
  color: #64748b;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: white;
  color: #475569;
  border: 2px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

/* 加载和错误状态 */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e2e8f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-message {
  color: #ef4444;
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}

.btn-retry {
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-retry:hover {
  background: #5568d3;
  transform: translateY(-1px);
}

/* 详情内容 */
.detail-content {
  display: grid;
  gap: 1.5rem;
}

.info-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.info-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #e2e8f0;
}

.card-header {
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
}

.card-body {
  padding: 1.5rem;
}

.info-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.info-item {
  margin-bottom: 1.5rem;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.info-value {
  font-size: 1rem;
  color: #1e293b;
  line-height: 1.6;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 3px solid #667eea;
}
</style>
