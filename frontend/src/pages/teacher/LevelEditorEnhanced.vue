<template>
  <div class="level-editor-enhanced" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- 顶部导航栏 -->
    <header class="top-navbar">
      <div class="navbar-left">
        <button class="btn-menu" @click="toggleSidebar">
          <span>{{ sidebarCollapsed ? '☰' : '✕' }}</span>
        </button>
        <button class="btn-back" @click="goBack">
          <span>←</span>
          <span class="btn-text">返回</span>
        </button>
        <div class="level-info">
          <h1>{{ level?.name || '加载中...' }}</h1>
          <span class="level-badge" :class="level?.is_published ? 'published' : 'draft'">
            {{ level?.is_published ? '已发布' : '草稿' }}
          </span>
        </div>
      </div>

      <div class="navbar-right">
        <button class="btn-action" @click="saveAll" title="保存">
          <span>💾</span>
          <span class="btn-text">保存</span>
        </button>
        <button
          v-if="!level?.is_published"
          class="btn-action primary"
          @click="publishLevel"
          title="发布关卡"
        >
          <span>📢</span>
          <span class="btn-text">发布</span>
        </button>
        <button
          v-else
          class="btn-action"
          @click="unpublishLevel"
          title="取消发布"
        >
          <span>🚫</span>
          <span class="btn-text">取消发布</span>
        </button>
      </div>
    </header>

    <div class="editor-main">
      <!-- 侧边栏 -->
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <nav class="nav-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="nav-tab"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-label">{{ tab.label }}</span>
            <span v-if="tab.count !== undefined" class="tab-count">{{ tab.count }}</span>
          </button>
        </nav>

        <div class="sidebar-footer">
          <div class="stats-card">
            <div class="stat-item">
              <span class="stat-icon">✅</span>
              <div class="stat-content">
                <span class="stat-value">{{ stats.tasks }}</span>
                <span class="stat-label">任务</span>
              </div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-icon">📋</span>
              <div class="stat-content">
                <span class="stat-value">{{ stats.questions }}</span>
                <span class="stat-label">考题</span>
              </div>
            </div>
          </div>

          <div class="progress-card">
            <div class="progress-header">
              <span>完成度</span>
              <span class="progress-value">{{ completionPercentage }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: completionPercentage + '%' }"></div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 内容区域 -->
      <main class="content-area">
        <Transition name="fade" mode="out-in">
          <!-- 基本信息 -->
          <section v-if="activeTab === 'basic'" key="basic" class="content-section">
            <div class="section-header">
              <h2>基本信息</h2>
              <p>配置关卡的基础信息和可见性</p>
            </div>

            <div class="form-container">
              <div class="form-card">
                <div class="form-group">
                  <label class="form-label">
                    <span>关卡名称</span>
                    <span class="required">*</span>
                  </label>
                  <input
                    v-model="levelForm.name"
                    type="text"
                    class="form-input"
                    placeholder="输入关卡名称"
                  />
                </div>

                <div class="form-group">
                  <label class="form-label">
                    <span>关卡描述</span>
                    <span class="form-hint">（支持 Markdown）</span>
                  </label>
                  <MarkdownEditor
                    v-model="levelForm.description"
                    height="300px"
                    placeholder="详细描述这个关卡的内容和学习目标..."
                  />
                </div>

                <div class="form-group">
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="levelForm.is_visible" />
                    <span>学生可见</span>
                    <span class="label-hint">勾选后学生可以在关卡地图中看到此关卡</span>
                  </label>
                </div>

                <div class="form-actions">
                  <button class="btn-primary" @click="saveBasicInfo">
                    <span>💾</span>
                    <span>保存基本信息</span>
                  </button>
                </div>
              </div>
            </div>
          </section>

          <!-- 任务配置 -->
          <section v-else-if="activeTab === 'tasks'" key="tasks" class="content-section">
            <div class="section-header">
              <h2>任务配置</h2>
              <p>创建和管理关卡中的学习任务</p>
            </div>
            <EnhancedTaskConfigPanel :level-id="levelId" @taskSelected="handleTaskSelected" />
          </section>

          <!-- 卡片配置 -->
          <section v-else-if="activeTab === 'cards'" key="cards" class="content-section">
            <div class="section-header">
              <h2>学习卡片</h2>
              <p>配置知识卡片和技能卡片，帮助学生学习</p>
            </div>
            <div v-if="!selectedTaskId" class="empty-notice">
              <span class="notice-icon">ℹ️</span>
              <p>请先在"任务配置"页面选择一个任务</p>
            </div>
            <CardConfigPanel v-else :task-id="selectedTaskId" />
          </section>

          <!-- 环节步骤 -->
          <section v-else-if="activeTab === 'phases'" key="phases" class="content-section">
            <div class="section-header">
              <h2>操作环节与步骤</h2>
              <p>设计任务的执行流程和操作步骤</p>
            </div>
            <div v-if="!selectedTaskId" class="empty-notice">
              <span class="notice-icon">ℹ️</span>
              <p>请先在"任务配置"页面选择一个任务</p>
            </div>
            <PhaseStepConfigPanel v-else :task-id="selectedTaskId" />
          </section>

          <!-- 考题配置 -->
          <section v-else-if="activeTab === 'questions'" key="questions" class="content-section">
            <div class="section-header">
              <h2>闯关考题</h2>
              <p>设置关卡的考核题目和通过标准</p>
            </div>
            <QuestionConfigPanel :level-id="levelId" />
          </section>

          <!-- 布局配置 -->
          <section v-else-if="activeTab === 'layout'" key="layout" class="content-section">
            <div class="section-header">
              <h2>界面布局</h2>
              <p>自定义学生端查看关卡时的界面布局</p>
            </div>
            <div class="feature-placeholder">
              <div class="placeholder-icon">🎨</div>
              <h3>拖拽式布局编辑器</h3>
              <p>此功能正在开发中，敬请期待</p>
              <div class="placeholder-features">
                <div class="feature-item">✓ 可视化编辑</div>
                <div class="feature-item">✓ 实时预览</div>
                <div class="feature-item">✓ 模板选择</div>
              </div>
            </div>
          </section>
        </Transition>
      </main>
    </div>

    <!-- 加载状态 -->
    <div v-if="!level" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner-large"></div>
        <p>加载关卡数据中...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Level } from '../../api/levels'
import { levelsApi } from '../../api/levels'
import EnhancedTaskConfigPanel from '../../components/panels/EnhancedTaskConfigPanel.vue'
import CardConfigPanel from '../../components/panels/CardConfigPanel.vue'
import PhaseStepConfigPanel from '../../components/panels/PhaseStepConfigPanel.vue'
import QuestionConfigPanel from '../../components/panels/QuestionConfigPanel.vue'
import MarkdownEditor from '../../components/ui/MarkdownEditor.vue'

const route = useRoute()
const router = useRouter()
const levelId = Number(route.params.levelId || route.params.id)

const level = ref<Level | null>(null)
const activeTab = ref<'basic' | 'tasks' | 'cards' | 'phases' | 'questions' | 'layout'>('tasks')
const selectedTaskId = ref<number | null>(null)
const sidebarCollapsed = ref(false)

const levelForm = ref({
  name: '',
  description: '',
  is_visible: true,
})

const tabs = computed(() => [
  { id: 'basic', label: '基本信息', icon: '📝' },
  { id: 'tasks', label: '任务配置', icon: '✅', count: stats.value.tasks },
  { id: 'cards', label: '学习卡片', icon: '📚' },
  { id: 'phases', label: '环节步骤', icon: '🔄' },
  { id: 'questions', label: '闯关考题', icon: '📋', count: stats.value.questions },
  { id: 'layout', label: '界面布局', icon: '🎨' },
])

const stats = ref({
  tasks: 0,
  questions: 0,
})

const completionPercentage = computed(() => {
  let completed = 0
  let total = 4

  if (levelForm.value.name) completed++
  if (stats.value.tasks > 0) completed++
  if (stats.value.questions > 0) completed++
  if (level.value?.is_published) completed++

  return Math.round((completed / total) * 100)
})

const loadLevel = async () => {
  try {
    const resp = await levelsApi.getLevel(levelId)
    level.value = resp.data
    levelForm.value = {
      name: level.value.name,
      description: level.value.description || '',
      is_visible: level.value.is_visible !== false,
    }
  } catch (e: any) {
    alert(e?.response?.data?.detail || '加载关卡失败')
    goBack()
  }
}

const saveBasicInfo = async () => {
  try {
    await levelsApi.updateLevel(levelId, {
      name: levelForm.value.name,
      description: levelForm.value.description,
      is_visible: levelForm.value.is_visible,
    })
    alert('保存成功！')
    await loadLevel()
  } catch (e: any) {
    alert(e?.response?.data?.detail || '保存失败')
  }
}

const saveAll = () => {
  alert('所有配置已自动保存')
}

const publishLevel = async () => {
  if (!confirm('确定要发布该关卡吗？发布后学生将可以看到该关卡。')) return
  try {
    // TODO: 调用发布API
    alert('关卡发布成功！')
    await loadLevel()
  } catch (e: any) {
    alert(e?.response?.data?.detail || '发布失败')
  }
}

const unpublishLevel = async () => {
  if (!confirm('确定要取消发布吗？取消后学生将无法看到该关卡。')) return
  try {
    // TODO: 调用取消发布API
    alert('已取消发布')
    await loadLevel()
  } catch (e: any) {
    alert(e?.response?.data?.detail || '取消发布失败')
  }
}

const goBack = () => {
  router.back()
}

const handleTaskSelected = (id: number | null) => {
  selectedTaskId.value = id
}

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

onMounted(async () => {
  await loadLevel()
})
</script>

<style scoped>
.level-editor-enhanced {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f3f4f6;
  overflow: hidden;
}

/* 顶部导航栏 */
.top-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.navbar-left,
.navbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-menu {
  display: none;
  padding: 0.5rem;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s;
}

.btn-menu:hover {
  background: #e5e7eb;
}

.btn-back {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-back:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.level-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.level-info h1 {
  margin: 0;
  font-size: 1.25rem;
  color: #111827;
  font-weight: 600;
}

.level-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.level-badge.published {
  background: #d1fae5;
  color: #065f46;
}

.level-badge.draft {
  background: #fef3c7;
  color: #92400e;
}

.btn-action {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.btn-action:hover {
  background: #f9fafb;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-action.primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #ffffff;
  border: none;
}

.btn-action.primary:hover {
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

/* 主体区域 */
.editor-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 260px;
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
  overflow-y: auto;
}

.sidebar.collapsed {
  width: 0;
  min-width: 0;
  border-right: none;
}

.nav-tabs {
  padding: 1rem 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  position: relative;
}

.nav-tab:hover {
  background: #f9fafb;
}

.nav-tab.active {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  color: #3b82f6;
  font-weight: 600;
}

.nav-tab.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: #3b82f6;
  border-radius: 0 3px 3px 0;
}

.tab-icon {
  font-size: 1.3rem;
}

.tab-label {
  flex: 1;
  font-size: 0.9rem;
}

.tab-count {
  padding: 0.15rem 0.5rem;
  background: #e5e7eb;
  color: #6b7280;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.nav-tab.active .tab-count {
  background: #3b82f6;
  color: #ffffff;
}

.sidebar-footer {
  margin-top: auto;
  padding: 1rem;
  border-top: 1px solid #f3f4f6;
}

.stats-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.stat-icon {
  font-size: 1.5rem;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
}

.stat-label {
  font-size: 0.75rem;
  color: #6b7280;
}

.stat-divider {
  width: 1px;
  background: #e5e7eb;
}

.progress-card {
  padding: 1rem;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
  border: 1px solid #bae6fd;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  color: #0369a1;
  font-weight: 600;
}

.progress-value {
  font-size: 1rem;
}

.progress-bar {
  height: 8px;
  background: #ffffff;
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
  transition: width 0.3s;
  border-radius: 999px;
}

/* 内容区域 */
.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.content-section {
  max-width: 1400px;
  margin: 0 auto;
}

.section-header {
  margin-bottom: 2rem;
}

.section-header h2 {
  margin: 0 0 0.5rem;
  font-size: 1.75rem;
  color: #111827;
}

.section-header p {
  margin: 0;
  color: #6b7280;
  font-size: 0.95rem;
}

.form-container {
  max-width: 900px;
}

.form-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 2rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
}

.required {
  color: #dc2626;
}

.form-hint {
  font-size: 0.8rem;
  font-weight: 400;
  color: #9ca3af;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border: 2px solid #e5e7eb;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 2px solid #e5e7eb;
  transition: all 0.2s;
}

.checkbox-label:hover {
  border-color: #d1d5db;
}

.checkbox-label input[type='checkbox'] {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.label-hint {
  margin-left: auto;
  font-size: 0.8rem;
  color: #9ca3af;
}

.form-actions {
  display: flex;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f3f4f6;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #ffffff;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.empty-notice {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 12px;
  color: #92400e;
}

.notice-icon {
  font-size: 2rem;
}

.empty-notice p {
  margin: 0;
  font-size: 0.95rem;
}

.feature-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4rem 2rem;
  background: #ffffff;
  border-radius: 12px;
  border: 2px dashed #d1d5db;
}

.placeholder-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.feature-placeholder h3 {
  margin: 0 0 0.5rem;
  color: #374151;
}

.feature-placeholder p {
  margin: 0 0 2rem;
  color: #9ca3af;
}

.placeholder-features {
  display: flex;
  gap: 2rem;
}

.feature-item {
  color: #6b7280;
  font-size: 0.9rem;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.spinner-large {
  width: 60px;
  height: 60px;
  border: 5px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-content p {
  margin: 0;
  color: #6b7280;
  font-size: 1.1rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 57px;
    bottom: 0;
    z-index: 200;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  }

  .sidebar-collapsed .sidebar {
    transform: translateX(-100%);
  }

  .btn-menu {
    display: block;
  }

  .content-area {
    padding: 1rem;
  }

  .btn-text {
    display: none;
  }

  .level-info h1 {
    font-size: 1rem;
  }
}

@media (max-width: 640px) {
  .top-navbar {
    padding: 0.5rem 1rem;
  }

  .navbar-left,
  .navbar-right {
    gap: 0.5rem;
  }

  .level-badge {
    display: none;
  }

  .stats-card {
    flex-direction: column;
    gap: 0.75rem;
  }

  .stat-divider {
    display: none;
  }
}
</style>
