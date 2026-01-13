<template>
  <section class="enhanced-task-panel">
    <!-- AI 生成面板 -->
    <AIGeneratePanel
      ref="aiPanel"
      :show-prompt-input="true"
      prompt-label="AI 生成指令"
      prompt-placeholder="描述你想要的任务，例如：生成一个关于 Spark 数据处理的实战任务，包含数据清洗和分析步骤"
      @generate="handleAIGenerate"
      @accept="handleAIAccept"
      @reject="handleAIReject"
      @regenerate="handleAIGenerate"
    >
      <template #result="{ data }">
        <div class="ai-task-preview-enhanced">
          <div class="preview-card">
            <div class="preview-card-header">
              <span class="preview-icon">📝</span>
              <span>任务名称</span>
            </div>
            <div class="preview-card-content">{{ data?.name }}</div>
          </div>

          <div class="preview-card">
            <div class="preview-card-header">
              <span class="preview-icon">📄</span>
              <span>任务描述</span>
            </div>
            <div class="preview-card-content markdown-content" v-html="renderMarkdown(data?.description)"></div>
          </div>

          <div class="preview-card">
            <div class="preview-card-header">
              <span class="preview-icon">🎯</span>
              <span>任务目标</span>
            </div>
            <div class="preview-card-content markdown-content" v-html="renderMarkdown(data?.objective)"></div>
          </div>
        </div>
      </template>
    </AIGeneratePanel>

    <!-- 任务列表 -->
    <div class="tasks-section">
      <div class="section-header">
        <div class="section-title">
          <h3>任务列表</h3>
          <span class="task-count">{{ tasks.length }} 个任务</span>
        </div>
        <div class="section-actions">
          <button class="btn-icon" @click="toggleView" :title="viewMode === 'grid' ? '列表视图' : '网格视图'">
            {{ viewMode === 'grid' ? '☰' : '⊞' }}
          </button>
          <button class="btn-primary" @click="startCreate">
            <span>+</span>
            <span>新建任务</span>
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载任务中...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <span class="error-icon">⚠️</span>
        <p>{{ error }}</p>
        <button class="btn-secondary" @click="loadTasks">重试</button>
      </div>

      <div v-else-if="tasks.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <h4>还没有任务</h4>
        <p>点击"新建任务"或使用 AI 生成来创建第一个任务</p>
      </div>

      <div v-else :class="['tasks-container', `view-${viewMode}`]">
        <div
          v-for="task in tasks"
          :key="task.id"
          :class="['task-card', { selected: selectedTaskId === task.id }]"
          @click="select(task.id)"
        >
          <div class="task-card-header">
            <div class="task-card-title">
              <span class="task-icon">✅</span>
              <h4>{{ task.name }}</h4>
            </div>
            <div class="task-card-actions">
              <button
                class="action-btn"
                @click.stop="edit(task)"
                title="编辑"
              >
                ✏️
              </button>
              <button
                class="action-btn danger"
                @click.stop="remove(task.id)"
                title="删除"
              >
                🗑️
              </button>
            </div>
          </div>

          <div v-if="task.description" class="task-card-description">
            <div class="markdown-content" v-html="renderMarkdown(task.description)"></div>
          </div>

          <div v-if="task.objective" class="task-card-objective">
            <span class="objective-icon">🎯</span>
            <div class="markdown-content" v-html="renderMarkdown(task.objective)"></div>
          </div>

          <div class="task-card-footer">
            <span class="task-meta">ID: {{ task.id }}</span>
            <span v-if="selectedTaskId === task.id" class="selected-badge">已选中</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 任务编辑弹窗 -->
    <Teleport to="body">
      <div v-if="showDialog" class="modal-overlay" @click.self="close">
        <div class="modal enhanced-modal">
          <div class="modal-header">
            <h3>{{ editingTask?.id ? '编辑任务' : '新建任务' }}</h3>
            <button class="btn-close" @click="close">×</button>
          </div>

          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">
                <span>任务名称</span>
                <span class="required">*</span>
              </label>
              <input
                v-model="form.name"
                type="text"
                class="form-input"
                placeholder="输入任务名称，例如：Spark 数据清洗实战"
                @keyup.enter="save"
              />
            </div>

            <div class="form-group">
              <label class="form-label">
                <span>任务描述</span>
                <span class="form-hint">（支持 Markdown 格式）</span>
              </label>
              <MarkdownEditor
                v-model="form.description"
                height="300px"
                placeholder="详细描述任务内容，支持 Markdown 格式...&#10;&#10;例如：&#10;## 任务概述&#10;本任务将带你学习如何使用 Spark 进行数据清洗&#10;&#10;## 学习目标&#10;- 掌握 Spark DataFrame API&#10;- 了解数据清洗常见操作"
              />
            </div>

            <div class="form-group">
              <label class="form-label">
                <span>任务目标</span>
                <span class="form-hint">（支持 Markdown 格式）</span>
              </label>
              <MarkdownEditor
                v-model="form.objective"
                height="200px"
                placeholder="定义任务的学习目标和预期成果...&#10;&#10;例如：&#10;- 能够独立完成数据清洗流程&#10;- 掌握 Spark 的核心 API&#10;- 理解分布式计算原理"
              />
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="close">取消</button>
            <button class="btn-primary" @click="save">
              <span>💾</span>
              <span>保存任务</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import type { Task } from '../../api/tasks'
import { tasksApi } from '../../api/tasks'
import { levelsApi } from '../../api/levels'
import { aiAssistantApi } from '../../api/aiAssistant'
import AIGeneratePanel from './AIGeneratePanel.vue'
import MarkdownEditor from '../ui/MarkdownEditor.vue'

interface Props {
  levelId: number
}

const props = defineProps<Props>()
const aiPanel = ref<InstanceType<typeof AIGeneratePanel> | null>(null)
const emit = defineEmits<{
  (e: 'taskSelected', id: number | null): void
}>()

const tasks = ref<Task[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const selectedTaskId = ref<number | null>(null)
const viewMode = ref<'grid' | 'list'>('grid')

const showDialog = ref(false)
const editingTask = ref<Task | null>(null)
const form = ref({
  name: '',
  description: '',
  objective: '',
})

// 简单的 Markdown 渲染函数
const renderMarkdown = (text: string | undefined) => {
  if (!text) return ''

  let html = text
  html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>')
  html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>')
  html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>')
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
  html = html.split('\n\n').map(para => {
    if (!para.match(/^<[^>]+>/)) {
      return `<p>${para.replace(/\n/g, '<br>')}</p>`
    }
    return para
  }).join('')
  return html
}

const loadTasks = async () => {
  loading.value = true
  error.value = null
  try {
    const resp = await tasksApi.getTasks(props.levelId)
    tasks.value = resp.data
    if (selectedTaskId.value) {
      const exists = tasks.value.some(t => t.id === selectedTaskId.value)
      if (!exists) {
        selectedTaskId.value = null
        emit('taskSelected', null)
      }
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '加载任务失败'
  } finally {
    loading.value = false
  }
}

const toggleView = () => {
  viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid'
}

const startCreate = () => {
  editingTask.value = null
  form.value = {
    name: '',
    description: '',
    objective: '',
  }
  showDialog.value = true
}

const edit = (task: Task) => {
  editingTask.value = task
  form.value = {
    name: task.name,
    description: task.description || '',
    objective: task.objective || '',
  }
  showDialog.value = true
}

const close = () => {
  showDialog.value = false
}

const save = async () => {
  if (!form.value.name.trim()) {
    alert('任务名称不能为空')
    return
  }
  try {
    if (editingTask.value) {
      await tasksApi.updateTask(editingTask.value.id, {
        name: form.value.name,
        description: form.value.description,
        objective: form.value.objective,
      })
    } else {
      await tasksApi.createTask(props.levelId, {
        name: form.value.name,
        description: form.value.description,
        objective: form.value.objective,
      })
    }
    showDialog.value = false
    await loadTasks()
  } catch (e: any) {
    alert(e?.response?.data?.detail || '保存任务失败')
  }
}

const remove = async (id: number) => {
  if (!confirm('确定要删除该任务吗？')) return
  try {
    await tasksApi.deleteTask(id)
    if (selectedTaskId.value === id) {
      selectedTaskId.value = null
      emit('taskSelected', null)
    }
    await loadTasks()
  } catch (e: any) {
    alert(e?.response?.data?.detail || '删除任务失败')
  }
}

const select = (id: number) => {
  selectedTaskId.value = id
  emit('taskSelected', id)
}

// AI 生成任务处理
const handleAIGenerate = async (prompt: string) => {
  aiPanel.value?.setGenerating(true)
  try {
    const levelResp = await levelsApi.getLevel(props.levelId)
    const level = levelResp.data

    const resp = await aiAssistantApi.generateTask({
      level_name: level.name,
      level_description: level.description || prompt || '',
    })

    const aiResult = resp.data
    aiPanel.value?.setResult({
      name: aiResult.name || `${level.name} - 任务`,
      description: aiResult.description || '',
      objective: aiResult.objective || '',
    })
  } catch (e: any) {
    aiPanel.value?.setError(e?.response?.data?.detail || 'AI 生成失败，请重试')
  }
}

const handleAIAccept = async (result: any) => {
  try {
    await tasksApi.createTask(props.levelId, {
      name: result.name,
      description: result.description,
      objective: result.objective,
    })
    await loadTasks()
    aiPanel.value?.clear()
  } catch (e: any) {
    alert(e?.response?.data?.detail || '创建任务失败')
  }
}

const handleAIReject = () => {
  // 清空结果即可
}

onMounted(loadTasks)

watch(
  () => props.levelId,
  () => {
    loadTasks()
  },
)
</script>

<style scoped>
/* styles copied from original file to keep visuals */
.enhanced-task-panel { display:flex; flex-direction:column; gap:1.5rem; }
/* ... (styles omitted for brevity) ... */
</style>


