<template>
  <div class="chapter-list-page">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">篇章管理</h1>
        <p class="page-subtitle">创建和管理教学篇章，设计游戏关卡</p>
      </div>
      <button class="btn-create" @click="showCreateDialog = true">
        <span class="btn-icon">+</span>
        <span>创建篇章</span>
      </button>
    </div>
    
    <div class="page-content">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <div class="error-icon">⚠️</div>
        <p class="error-message">{{ error }}</p>
        <button class="btn-retry" @click="fetchChapters">重试</button>
      </div>
      
      <div v-else-if="chapters.length === 0" class="empty-state">
        <div class="empty-icon">📚</div>
        <h3>还没有篇章</h3>
        <p>创建您的第一个篇章，开始设计游戏教学关卡</p>
        <button class="btn-create-primary" @click="showCreateDialog = true">
          <span class="btn-icon">+</span>
          <span>创建第一个篇章</span>
        </button>
      </div>
      
      <div v-else class="chapters-grid">
        <div 
          v-for="chapter in chapters" 
          :key="chapter.id" 
          class="chapter-card"
          @click="handleViewChapter(chapter.id)"
        >
          <div class="card-header">
            <div class="card-icon">📖</div>
            <div class="card-actions">
              <button 
                class="action-btn edit-btn" 
                @click.stop="handleEdit(chapter)"
                title="编辑"
              >
                <span>✏️</span>
              </button>
              <button 
                class="action-btn delete-btn" 
                @click.stop="handleDelete(chapter.id)"
                title="删除"
              >
                <span>🗑️</span>
              </button>
            </div>
          </div>
          
          <div class="card-body">
            <h3 class="card-title">{{ chapter.name }}</h3>
            <p class="card-description">{{ chapter.description || '暂无描述' }}</p>
          </div>
          
          <div class="card-footer">
            <div class="card-meta">
              <span class="meta-item">
                <span class="meta-icon">📅</span>
                {{ formatDate(chapter.created_at) }}
              </span>
            </div>
            <div class="card-arrow">→</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <ChapterForm
      v-if="showCreateDialog || editingChapter"
      :chapter="editingChapter"
      @close="handleCloseDialog"
      @saved="handleSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { chaptersApi, type Chapter } from '../../api/chapters'
import ChapterForm from './ChapterForm.vue'

const router = useRouter()
const authStore = useAuthStore()
const chapters = ref<Chapter[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const showCreateDialog = ref(false)
const editingChapter = ref<Chapter | null>(null)

const fetchChapters = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await chaptersApi.getChapters()
    chapters.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || '加载篇章列表失败'
    console.error('Error fetching chapters:', err)
  } finally {
    loading.value = false
  }
}

const handleViewChapter = (id: number) => {
  router.push(`/teacher/chapters/${id}/map-editor`)
}

const handleEdit = (chapter: Chapter) => {
  editingChapter.value = chapter
}

const handleDelete = async (id: number) => {
  if (!confirm('确定要删除这个篇章吗？此操作不可恢复。')) {
    return
  }
  
  try {
    await chaptersApi.deleteChapter(id)
    await fetchChapters()
  } catch (err: any) {
    alert(err.response?.data?.detail || '删除失败')
    console.error('Error deleting chapter:', err)
  }
}

const handleCloseDialog = () => {
  showCreateDialog.value = false
  editingChapter.value = null
}

const handleSaved = () => {
  handleCloseDialog()
  fetchChapters()
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

onMounted(async () => {
  // 确保用户信息已加载
  if (!authStore.currentUser && authStore.token) {
    try {
      await authStore.fetchProfile()
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return
    }
  }
  
  fetchChapters()
})
</script>

<style scoped>
.chapter-list-page {
  width: 100%;
  padding: 0;
  margin: 0;
}

.page-content {
  width: 100%;
  padding: 0;
  margin: 0;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding: 0 0.5rem 1.5rem;
  border-bottom: 2px solid #e2e8f0;
}

.header-left {
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

.btn-create {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.btn-create:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-create:active {
  transform: translateY(0);
}

.btn-icon {
  font-size: 1.2rem;
  font-weight: bold;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0.5rem;
  color: #64748b;
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

/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0.5rem;
  text-align: center;
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

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0.5rem;
  text-align: center;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin: 0 0.5rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.6;
}

.empty-state h3 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
  color: #1e293b;
}

.empty-state p {
  margin: 0 0 2rem;
  color: #64748b;
  font-size: 0.95rem;
}

.btn-create-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.btn-create-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

/* 篇章网格 */
.chapters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  padding: 0 0.5rem;
  width: 100%;
}

/* 篇章卡片 */
.chapter-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.chapter-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.chapter-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #e2e8f0;
}

.chapter-card:hover::before {
  transform: scaleX(1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-icon {
  font-size: 2rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.chapter-card:hover .card-actions {
  opacity: 1;
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: #f1f5f9;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  font-size: 1rem;
}

.edit-btn:hover {
  background: #dbeafe;
  transform: scale(1.1);
}

.delete-btn:hover {
  background: #fee2e2;
  transform: scale(1.1);
}

.card-body {
  margin-bottom: 1rem;
}

.card-title {
  margin: 0 0 0.75rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
}

.card-description {
  margin: 0;
  font-size: 0.9rem;
  color: #64748b;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

.card-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: #94a3b8;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.meta-icon {
  font-size: 0.9rem;
}

.card-arrow {
  font-size: 1.5rem;
  color: #cbd5e1;
  transition: all 0.3s ease;
}

.chapter-card:hover .card-arrow {
  color: #667eea;
  transform: translateX(4px);
}
</style>
