<template>
  <div class="level-editor">
    <div class="page-header">
      <div class="page-header-left">
        <button class="btn-back" @click="goBack">← 返回关卡地图</button>
        <div>
          <h2>关卡编辑：{{ level?.name || '加载中...' }}</h2>
          <p class="subtitle">编辑教案/实验指导书（Markdown 格式），系统将自动生成交互式学习页面</p>
        </div>
      </div>
      <div class="page-header-actions" v-if="level">
        <div class="action-group">
          <span class="action-label">快速操作：</span>
          <button class="btn-secondary" @click="loadTemplate">📋 加载模板</button>
          <button class="btn-secondary" @click="openVisualEditor">🎨 可视化编辑</button>
        <button class="btn-secondary" @click="showGuidance = true">❓ 帮助</button>
        </div>
        <div class="action-group">
          <span class="action-label">AI助手：</span>
          <button class="btn-secondary" @click="handleGeneratePreview" :disabled="previewLoading">
            {{ previewLoading ? '生成中...' : '✨ AI转换' }}
          </button>
          <button class="btn-secondary" @click="handleApplyToVisualEditor" :disabled="!courseData || saving">
            {{ saving ? '保存中...' : '🎯 应用到可视化编辑器' }}
          </button>
        </div>
        <div class="action-group">
          <span class="action-label">预览测试：</span>
          <button class="btn-secondary" @click="openInteractivePreview" :disabled="!courseData">👁️ 预览</button>
        </div>
        <button class="btn-primary" @click="handleSave" :disabled="saving">
          {{ saving ? '保存中...' : '💾 保存' }}
        </button>
      </div>
    </div>

    <input
      ref="jsonFileInput"
      type="file"
      accept="application/json"
      class="hidden-file-input"
      @change="handleJsonFileChange"
    />

    <div v-if="level" class="split-layout" :class="{ 'editor-fullscreen': isEditorFullscreen }">
      <!-- 左侧：Markdown 编辑器 -->
      <section class="pane editor-pane" :class="{ 'is-fullscreen': isEditorFullscreen }">
        <header class="pane-header pane-header-with-actions">
          <div>
            <h3>教案编辑（Markdown）</h3>
            <p class="pane-subtitle">编写教学内容，AI将自动转换为交互式界面</p>
          </div>
          <button class="pane-action-btn" @click="toggleEditorFullscreen">
            {{ isEditorFullscreen ? '退出全屏' : '全屏编辑' }}
          </button>
        </header>
        <div class="pane-body">
          <div class="editor-hint" v-if="!teachingGuideMd.trim()">
            <div class="hint-icon">💡</div>
            <div class="hint-content">
              <h4>开始编写教案</h4>
              <p>在这里输入教学内容，支持Markdown格式。AI助手可以帮您快速生成结构化的教学内容。</p>
              <button class="hint-btn" @click="loadTemplate">📋 使用模板</button>
              <button class="hint-btn" @click="toggleAiPanel">🤖 AI助手</button>
            </div>
          </div>
          <textarea
            v-model="teachingGuideMd"
            ref="mdEditorRef"
            class="md-editor"
            placeholder="请输入教案内容（Markdown格式）&#10;&#10;建议包含：学习目标、任务时间、准备工作、操作步骤、课堂问答、作业要求等。"
          ></textarea>
        </div>
      </section>

      <!-- 右侧：交互 JSON 结构 -->
      <section v-if="!isEditorFullscreen" class="pane preview-pane">
        <header class="pane-header">
          <div>
            <h3>交互数据（JSON）</h3>
            <p class="preview-hint">
              AI转换后的交互式内容数据，支持手动编辑和调整。
            </p>
          </div>
          <div class="json-status" :class="jsonStatus">
            {{ jsonStatusText }}
          </div>
        </header>
        <div class="pane-body json-pane-body">
          <div class="json-toolbar">
            <button class="json-btn" @click="handleJsonToInteractive" :disabled="!jsonEditorContent.trim()">
              🧩 应用到预览
            </button>
            <button class="json-btn" @click="downloadCourseJson" :disabled="!jsonEditorContent.trim()">
              💾 下载JSON
            </button>
            <button class="json-btn" @click="triggerLoadCourseJson">
              📂 加载JSON
            </button>
          </div>
          <textarea
            v-model="jsonEditorContent"
            class="json-editor"
            :placeholder="jsonPlaceholder"
          ></textarea>
        </div>
      </section>
    </div>

    <!-- 底部：生成日志 / 状态栏 -->
    <section class="log-panel">
      <header class="log-header">
        <span class="log-title">生成日志 / 状态</span>
        <span class="log-status" :class="logStatus">
          {{ logStatusLabel }}
        </span>
      </header>
      <div class="log-body">
        <div v-if="!logs.length" class="log-empty">
          这里将实时显示「生成交互页面」的大模型调用日志，方便排查问题。
        </div>
        <ul v-else class="log-list">
          <li v-for="(line, idx) in logs" :key="idx">
            {{ line }}
          </li>
        </ul>
      </div>
    </section>

    <!-- 悬浮 AI 助手按钮 -->
    <button class="ai-float-toggle" @click="toggleAiPanel">
      🤖
    </button>

    <!-- 悬浮 AI 面板 -->
    <div
      v-show="showAiPanel"
      class="ai-float-panel"
      :class="{ dragging: isDragging, maximized: isAiMaximized }"
      :style="aiPanelStyle"
    >
      <div class="ai-modal-header" @mousedown.stop="handleHeaderMouseDown">
        <button class="ai-header-btn" type="button" @click="toggleAiMaximize">
          {{ isAiMaximized ? '还原' : '最大化' }}
        </button>
        <button class="ai-close" @click="closeAiPanel">×</button>
      </div>
      <div class="ai-modal-body">
        <TeachingGuideAssistant
          :level-name="level?.name || ''"
          :level-description="level?.description || ''"
          @generated="handleAIGenerated"
          @insertDataLink="handleInsertDataLink"
        />
      </div>
    </div>

    <!-- 操作指导 -->
    <EditorGuidance
      :show-guidance="showGuidance"
      :current-state="guidanceState"
      @close="showGuidance = false"
      @skip="showGuidance = false"
      @action="handleGuidanceAction"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Level } from '../../api/levels'
import { levelsApi } from '../../api/levels'
import TeachingGuideAssistant from '../../components/panels/TeachingGuideAssistant.vue'
import EditorGuidance from '../../components/panels/EditorGuidance.vue'
import type { CourseData } from '../../types/coursePlayer'

const route = useRoute()
const router = useRouter()
const levelId = Number(route.params.levelId)

const level = ref<Level | null>(null)
const teachingGuideMd = ref('')
const saving = ref(false)
const courseData = ref<CourseData | null>(null)
const previewLoading = ref(false)
const showAiPanel = ref(false)
const showGuidance = ref(false)
const isEditorFullscreen = ref(false)
const isDragging = ref(false)
const isAiMaximized = ref(false)
const modalPosition = ref({ x: 0, y: 0 })
const dragStart = ref({ x: 0, y: 0 })
const dragMouseStart = ref({ x: 0, y: 0 })
const jsonEditorContent = ref('')
const jsonFileInput = ref<HTMLInputElement | null>(null)
const mdEditorRef = ref<HTMLTextAreaElement | null>(null)

type LogStatus = 'idle' | 'running' | 'success' | 'error'
const logs = ref<string[]>([])
const logStatus = ref<LogStatus>('idle')
const logStatusLabel = computed(() => {
  switch (logStatus.value) {
    case 'running':
      return '正在生成交互页面...'
    case 'success':
      return '生成成功'
    case 'error':
      return '生成失败'
    default:
      return '空闲'
  }
})

// JSON状态计算
const jsonStatus = computed(() => {
  if (!jsonEditorContent.value.trim()) return 'empty'
  try {
    JSON.parse(jsonEditorContent.value)
    return courseData.value ? 'ready' : 'parsed'
  } catch {
    return 'error'
  }
})

const jsonStatusText = computed(() => {
  switch (jsonStatus.value) {
    case 'empty': return '无数据'
    case 'parsed': return '已解析'
    case 'ready': return '可预览'
    case 'error': return '格式错误'
    default: return '未知'
  }
})

const jsonPlaceholder = computed(() => {
  if (!teachingGuideMd.value.trim()) {
    return '请先在左侧编写教案内容，然后点击"AI转换"按钮生成交互数据。'
  }
  return '点击"AI转换"按钮将左侧的Markdown教案转换为交互式JSON数据...'
})

// 操作指导状态
const guidanceState = computed(() => ({
  hasContent: teachingGuideMd.value.trim().length > 0,
  hasJsonData: jsonEditorContent.value.trim().length > 0 && jsonStatus.value !== 'error',
  hasPreview: courseData.value !== null,
  hasSaved: editorState.value.lastSaved !== null
}))

// 处理操作指导动作
const handleGuidanceAction = (action: string) => {
  switch (action) {
    case 'load-template':
      loadTemplate()
      break
    case 'ai-convert':
      handleGeneratePreview()
      break
    case 'preview':
      openInteractivePreview()
      break
    case 'visual-editor':
      openVisualEditor()
      break
    case 'save':
      handleSave()
      break
  }
}

const appendLog = (message: string) => {
  const time = new Date().toLocaleTimeString()
  logs.value.push(`[${time}] ${message}`)
  // 只保留最近 200 条
  if (logs.value.length > 200) {
    logs.value.splice(0, logs.value.length - 200)
  }
}

const clearLogs = () => {
  logs.value = []
}

const normalizeCourseData = (raw: CourseData): CourseData => {
  const normalizedSteps = (raw.steps || []).map((step, idx) => {
    const contentHtml = step.contentHtml || (step as any).content || ''
    return {
      ...step,
      id: step.id || `step-${idx + 1}`,
      contentHtml,
    }
  })

  const defaultMetaTitle = raw.meta?.title || level.value?.name || '交互式关卡'
  const normalizedMeta = {
    title: defaultMetaTitle,
    preparations: raw.meta?.preparations || [],
    goals: raw.meta?.goals || [],
  }

  return {
    ...raw,
    meta: normalizedMeta,
    steps: normalizedSteps,
  }
}

// 智能状态管理
const editorState = ref({
  hasUnsavedChanges: false,
  lastSaved: null as Date | null,
  aiProcessing: false,
  previewReady: false
})

// 监听内容变化
watch([teachingGuideMd, jsonEditorContent], () => {
  editorState.value.hasUnsavedChanges = true
})

watch(courseData, (newData) => {
  if (newData) {
    editorState.value.previewReady = true
    editorState.value.hasUnsavedChanges = true
  }
}, { deep: true })

// 保存时重置状态
const handleSaveSuccess = () => {
  editorState.value.hasUnsavedChanges = false
  editorState.value.lastSaved = new Date()
}

const downloadCourseJson = () => {
  if (!jsonEditorContent.value.trim()) {
    alert('当前没有可保存的 JSON 内容')
    return
  }
  const blob = new Blob([jsonEditorContent.value], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const filename = `${level.value?.name || 'level'}-course.json`
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

const triggerLoadCourseJson = () => {
  jsonFileInput.value?.click()
}

const applyJsonFromEditor = (notify = true): boolean => {
  if (!jsonEditorContent.value.trim()) {
    alert('JSON 内容为空，无法生成交互网页')
    return false
  }
  try {
    const parsed = JSON.parse(jsonEditorContent.value)
    if (!parsed.steps || !Array.isArray(parsed.steps)) {
      throw new Error('JSON 中缺少 steps 数组')
    }
    courseData.value = normalizeCourseData(parsed)
    if (notify) {
      appendLog('JSON 解析成功，已生成交互页面数据。')
      logStatus.value = 'success'
    }
    return true
  } catch (err: any) {
    const msg = err?.message || 'JSON 解析失败，请检查格式'
    appendLog(`JSON 解析失败：${msg}`)
    alert(msg)
    return false
  }
}

const handleJsonToInteractive = () => {
  applyJsonFromEditor(true)
}

const handleJsonFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  try {
    const text = await file.text()
    jsonEditorContent.value = text
    applyJsonFromEditor(false)
    appendLog(`成功加载本地文件：${file.name}`)
  } catch (err: any) {
    const msg = err?.message || '读取 JSON 文件失败'
    appendLog(`读取 JSON 文件失败：${msg}`)
    alert(msg)
  } finally {
    if (target) target.value = ''
  }
}

const openInteractivePreview = () => {
  if (!courseData.value) {
    const ok = applyJsonFromEditor(false)
    if (!ok) return
  }
  try {
    localStorage.setItem('levelInteractivePreviewData', JSON.stringify(courseData.value))
    const resolved = router.resolve({ name: 'level-interactive-preview' })
    const routeUrl = `${window.location.origin}${resolved.href}`

    const previewWindow = window.open(routeUrl, 'interactivePreviewWindow', 'width=1400,height=900')
    if (!previewWindow) {
      appendLog('浏览器阻止了弹出窗口，请允许弹窗或手动在新标签中打开预览页面。')
      alert('浏览器阻止了弹出窗口，请允许弹窗或手动在新标签中打开预览页面。')
    } else {
      appendLog('已在独立窗口中打开交互式网页预览。')
    }
  } catch (err) {
    console.error('打开预览窗口失败:', err)
    alert('无法打开预览窗口，请检查浏览器弹窗设置。')
  }
}

watch(courseData, (val) => {
  if (val) {
    jsonEditorContent.value = JSON.stringify(val, null, 2)
  } else {
    jsonEditorContent.value = ''
  }
})

const toggleEditorFullscreen = () => {
  isEditorFullscreen.value = !isEditorFullscreen.value
}

const loadLevel = async () => {
  const resp = await levelsApi.getLevel(levelId)
  level.value = resp.data
  teachingGuideMd.value = resp.data.teaching_guide_md || ''
}

const goBack = () => {
  router.back()
}

const openVisualEditor = () => {
  router.push({
    name: 'teacher-visual-editor',
    params: { levelId: levelId }
  })
}

const handleApplyToVisualEditor = async () => {
  if (!courseData.value || !level.value) {
    alert('没有可应用的数据，请先执行 AI 转换')
    return
  }

  saving.value = true
  try {
    // 保存 courseData 到数据库
    await levelsApi.updateLevel(levelId, {
      course_data_json: JSON.stringify(courseData.value)
    })
    appendLog('AI 转换的数据已保存到数据库')
    logStatus.value = 'success'
    
    // 跳转到可视化编辑器
    setTimeout(() => {
      router.push({
        name: 'teacher-visual-editor',
        params: { levelId: levelId }
      })
    }, 500)
  } catch (err: any) {
    const errorMsg = err.response?.data?.detail || '保存失败'
    appendLog(`保存失败：${errorMsg}`)
    logStatus.value = 'error'
    console.error('Error saving course data:', err)
    alert(errorMsg)
  } finally {
    saving.value = false
  }
}

const handleSave = async () => {
  if (!level.value) return

  saving.value = true
  try {
    await levelsApi.updateLevel(levelId, {
      teaching_guide_md: teachingGuideMd.value
    })
    // 重新加载关卡数据
    await loadLevel()
    handleSaveSuccess()
    appendLog('教案保存成功')
    logStatus.value = 'success'
  } catch (err: any) {
    const errorMsg = err.response?.data?.detail || '保存失败'
    appendLog(`保存失败：${errorMsg}`)
    logStatus.value = 'error'
    console.error('Error saving teaching guide:', err)
  } finally {
    saving.value = false
  }
}

const handleGeneratePreview = async () => {
  if (!teachingGuideMd.value.trim()) return
  clearLogs()
  logStatus.value = 'running'
  appendLog('开始调用大模型，将当前 Markdown 教案转换为交互式关卡 JSON ...')

  previewLoading.value = true
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('未登录或登录已失效，请重新登录后再试')
    }

    const apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
    const baseURL = apiBaseURL.endsWith('/') ? apiBaseURL.slice(0, -1) : apiBaseURL
    const url = `${baseURL}/ai-assistant/teaching-guide-to-course-json-stream`

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        markdown: teachingGuideMd.value,
      }),
    })

    if (!response.ok || !response.body) {
      let detail = `HTTP 错误 ${response.status}`
      try {
        const text = await response.text()
        const json = JSON.parse(text)
        detail = json.detail || detail
      } catch {
        // ignore
      }
      throw new Error(detail)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    appendLog('已连接到 AI 服务，开始接收流式数据 ...')

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const dataStr = line.slice(6)
        if (!dataStr.trim()) continue
        try {
          const data = JSON.parse(dataStr)
          if (data.type === 'start') {
            appendLog(data.message || '开始生成 ...')
          } else if (data.type === 'content') {
            // 逐步输出大模型增量内容到日志（适当截断避免过长）
            const snippet: string = data.content || ''
            if (snippet) {
              appendLog(snippet.length > 120 ? snippet.slice(0, 120) + ' ...' : snippet)
            }
          } else if (data.type === 'result') {
            const result: CourseData = normalizeCourseData(data.data)
            courseData.value = result
            appendLog(`解析完成，成功生成 ${result.steps?.length || 0} 个学习步骤。`)
            logStatus.value = 'success'
            previewLoading.value = false
            return
          } else if (data.type === 'error') {
            const msg: string = data.message || '生成交互页面失败'
            appendLog(`生成失败：${msg}`)
            logStatus.value = 'error'
            previewLoading.value = false
            alert(msg)
            return
          }
        } catch (e) {
          console.error('解析 SSE 消息失败:', e, line)
        }
      }
    }

    // 如果没有 result 消息，但有 courseData，则视为成功；否则给出提示
    if (!courseData.value) {
      appendLog('未收到有效的结果数据，请稍后重试或检查后端日志。')
      logStatus.value = 'error'
      alert('生成交互页面失败：未收到有效数据')
    } else {
      logStatus.value = 'success'
    }
  } catch (err: any) {
    console.error('Error generating course JSON:', err)
    const detail = err?.message || err?.response?.data?.detail || '生成交互页面失败'
    appendLog(`生成失败：${detail}`)
    logStatus.value = 'error'
    alert(detail)
  } finally {
    previewLoading.value = false
  }
}

const loadTemplate = () => {
  teachingGuideMd.value = `# 任务名称

## 📌 学习目标

通过本任务的学习，你将能够：

1. **知识目标**
   - 目标1
   - 目标2

2. **技能目标**
   - 目标1
   - 目标2

3. **素养目标**
   - 目标1
   - 目标2

---

## ⏰ 任务时间

- **总时长**：X学时（XX分钟）
- **建议分配**：
  - 步骤一：XX分钟
  - 步骤二：XX分钟

---

## 🛠️ 准备工作

### 必备工具
- [ ] 工具1
- [ ] 工具2

---

## 📋 操作步骤

### 步骤一：标题（XX分钟）

#### 1.1 子标题

操作方法：

\`\`\`
步骤：
1. 步骤1
2. 步骤2
3. 步骤3
\`\`\`

**立即动手：**
1. 练习1
2. 练习2

#### 📝 课堂问答：标题

完成上述操作后，请回答以下问题：

**问题1：** 问题内容？

A. 选项A  
B. 选项B  
C. 选项C  
D. 选项D

**正确答案：B**

**解析：** 解析内容

---

### 步骤二：标题（XX分钟）

（继续添加更多步骤...）

---

## 📝 作业要求

### 提交内容

**文件：** 文件名

**要求：**
1. 要求1
2. 要求2

**文件命名：** \`学号_姓名_任务X.docx\`

---

## ❓ 常见问题

### Q1: 问题1？
**A:** 答案1

### Q2: 问题2？
**A:** 答案2

---

## 💡 学习提示

1. 提示1
2. 提示2

---

## 🎯 自我检查

完成本任务后，请检查：

- [ ] 检查项1
- [ ] 检查项2
- [ ] 检查项3
`
}

const openAiPanel = () => {
  showAiPanel.value = true
  // 打开时重置位置为右上角附近
  const defaultWidth = 880
  const margin = 32
  const viewportWidth = window.innerWidth || document.documentElement.clientWidth || 1200
  const x = Math.max(margin, viewportWidth - defaultWidth - margin)
  const y = 140
  modalPosition.value = { x, y }
}

const closeAiPanel = () => {
  showAiPanel.value = false
  isDragging.value = false
  isAiMaximized.value = false
}

const handleHeaderMouseDown = (event: MouseEvent) => {
  if (isAiMaximized.value) return
  isDragging.value = true
  dragMouseStart.value = { x: event.clientX, y: event.clientY }
  dragStart.value = { ...modalPosition.value }
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseup', handleMouseUp)
}

const handleMouseMove = (event: MouseEvent) => {
  if (!isDragging.value) return
  const dx = event.clientX - dragMouseStart.value.x
  const dy = event.clientY - dragMouseStart.value.y
  modalPosition.value = {
    x: dragStart.value.x + dx,
    y: dragStart.value.y + dy,
  }
}

const handleMouseUp = () => {
  if (!isDragging.value) return
  isDragging.value = false
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseup', handleMouseUp)
}

const handleAIGenerated = (mdContent: string) => {
  teachingGuideMd.value = mdContent
}

const handleInsertDataLink = (url: string) => {
  const textarea = mdEditorRef.value
  const value = teachingGuideMd.value || ''
  const linkText = `[示例数据下载](${url})`

  if (!textarea) {
    teachingGuideMd.value = value + (value ? '\n\n' : '') + linkText
    return
  }

  const start = textarea.selectionStart ?? value.length
  const end = textarea.selectionEnd ?? start

  teachingGuideMd.value = value.slice(0, start) + linkText + value.slice(end)

  nextTick(() => {
    const pos = start + linkText.length
    textarea.focus()
    textarea.setSelectionRange(pos, pos)
  })
}

const toggleAiPanel = () => {
  if (showAiPanel.value) {
    showAiPanel.value = false
    return
  }
  openAiPanel()
}

const toggleAiMaximize = () => {
  isAiMaximized.value = !isAiMaximized.value
  isDragging.value = false
}

const aiPanelStyle = computed(() => {
  if (isAiMaximized.value) {
    const margin = 16
    return {
      top: `${margin}px`,
      left: `${margin}px`,
      width: `calc(100vw - ${margin * 2}px)`,
      height: `calc(100vh - ${margin * 2}px)`,
    }
  }
  return {
    top: modalPosition.value.y + 'px',
    left: modalPosition.value.x + 'px',
  }
})

onMounted(async () => {
  await loadLevel()

  // 检查是否是第一次使用
  const hasSeenGuidance = localStorage.getItem('level-editor-guidance-seen')
  if (!hasSeenGuidance) {
    showGuidance.value = true
    localStorage.setItem('level-editor-guidance-seen', 'true')
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseup', handleMouseUp)
})
</script>

<style scoped>
.level-editor {
  padding: 0.75rem 2rem 2rem;
}

.page-header {
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
}

.page-header-left {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.page-header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.action-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
  white-space: nowrap;
}

.btn-back {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.btn-back:hover {
  text-decoration: underline;
}

.page-header h2 {
  margin: 0;
  color: #1f2937 !important;
  font-weight: 700;
  font-size: 1.5rem;
}

.subtitle {
  margin: 0.25rem 0 0;
  font-size: 0.9rem;
  color: #6b7280;
}

.split-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 1.2fr);
  gap: 1.25rem;
  margin-top: 0.5rem;
  align-items: stretch;
}

.split-layout.editor-fullscreen {
  grid-template-columns: minmax(0, 1fr);
}

.pane {
  background: #ffffff;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  min-height: 600px;
}

.editor-pane.is-fullscreen {
  grid-column: 1 / -1;
}

.pane-header {
  padding: 0.9rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.pane-header-with-actions {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.pane-subtitle {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: normal;
}

.pane-header h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #111827;
}

.pane-action-btn {
  padding: 0.25rem 0.75rem;
  font-size: 0.8125rem;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  color: #4b5563;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.pane-action-btn:hover {
  background: #e5e7eb;
}

.pane-body {
  flex: 1;
  padding: 1rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.editor-hint {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #0ea5e9;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.hint-icon {
  font-size: 2rem;
  opacity: 0.8;
}

.hint-content h4 {
  margin: 0 0 0.5rem;
  color: #0c4a6e;
  font-size: 1.1rem;
}

.hint-content p {
  margin: 0 0 1rem;
  color: #0369a1;
  line-height: 1.5;
}

.hint-btn {
  padding: 0.5rem 1rem;
  margin-right: 0.5rem;
  border: 1px solid #0ea5e9;
  border-radius: 6px;
  background: white;
  color: #0ea5e9;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.hint-btn:hover {
  background: #0ea5e9;
  color: white;
}

.btn-primary,
.btn-secondary {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.editor-panel,
.preview-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 600px;
}

.editor-container {
  flex: 1;
  padding: 1.5rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.md-editor {
  width: 100%;
  flex: 1;
  padding: 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.9375rem;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  line-height: 1.6;
  resize: none;
  transition: all 0.2s ease;
  background: #ffffff;
  color: #1f2937;
  box-sizing: border-box;
}

.md-editor:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.md-editor::placeholder {
  color: #9ca3af;
}

.preview-hint {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}

.preview-container {
  flex: 1;
  overflow-y: auto;
}

.json-pane-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.json-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.json-status.empty {
  background: #f3f4f6;
  color: #6b7280;
}

.json-status.parsed {
  background: #dbeafe;
  color: #1d4ed8;
}

.json-status.ready {
  background: #dcfce7;
  color: #15803d;
}

.json-status.error {
  background: #fee2e2;
  color: #dc2626;
}

.json-toolbar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.json-btn {
  padding: 0.375rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  color: #374151;
  cursor: pointer;
  font-size: 0.8125rem;
  transition: all 0.15s ease;
}

.json-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.json-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.json-editor {
  flex: 1;
  width: 100%;
  height: 100%;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  padding: 1rem;
  box-sizing: border-box;
  resize: none;
  background: #0f172a;
  color: #e2e8f0;
  overflow: auto;
  white-space: pre;
}

.json-editor:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.preview-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #9ca3af;
  font-size: 0.9375rem;
}

.preview-content {
  min-height: 100%;
}

.preview-placeholder {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.preview-placeholder p {
  margin: 0.5rem 0;
}

/* 日志面板 */
.log-panel {
  margin-top: 1.25rem;
  background: #0b1120;
  border-radius: 8px;
  padding: 0.75rem 1rem 0.85rem;
  color: #e5e7eb;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.8rem;
}

.log-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.4rem;
}

.log-title {
  font-weight: 600;
  color: #e5e7eb;
}

.log-status {
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  font-size: 0.75rem;
  border: 1px solid rgba(148, 163, 184, 0.6);
  color: #e5e7eb;
}

.log-status.running {
  border-color: #f97316;
  color: #fed7aa;
}

.log-status.success {
  border-color: #22c55e;
  color: #bbf7d0;
}

.log-status.error {
  border-color: #f97373;
  color: #fecaca;
}

.log-body {
  max-height: 160px;
  overflow-y: auto;
  padding-top: 0.25rem;
  border-top: 1px solid rgba(148, 163, 184, 0.4);
}

.log-empty {
  color: #6b7280;
}

.log-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.log-list li {
  white-space: pre-wrap;
  word-break: break-all;
  line-height: 1.4;
}

.hidden-file-input {
  display: none;
}

.ai-panel {
  padding: 1.5rem;
  overflow-y: auto;
}

.ai-float-panel {
  width: 880px;
  max-height: 90vh;
  position: fixed;
  z-index: 1300;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.35);
  display: flex;
  flex-direction: column;
  resize: both;
  overflow: hidden;
}

.ai-modal-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0.9rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
  gap: 0.5rem;
}

.ai-modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.ai-header-btn {
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #374151;
  font-size: 0.8125rem;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.ai-header-btn:hover {
  background: #f3f4f6;
}

.ai-close {
  border: none;
  background: transparent;
  font-size: 1.4rem;
  cursor: pointer;
  color: #6b7280;
}

.ai-float-panel.dragging {
  cursor: move;
}

.ai-float-panel.maximized {
  resize: none;
  max-height: none;
}

.ai-modal-body {
  padding: 1rem 1.25rem 1.25rem;
  overflow-y: auto;
}

/* 最大化时，让助理内容铺满宽度（TeachingGuideAssistant.vue 内部有 max-width: 1000px） */
.ai-float-panel.maximized :deep(.teaching-guide-assistant) {
  max-width: none;
  width: 100%;
  margin: 0;
}

.ai-float-toggle {
  position: fixed;
  top: 130px;
  right: 40px;
  width: 44px;
  height: 44px;
  border-radius: 999px;
  border: none;
  background: #3b82f6;
  color: #ffffff;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 25px rgba(37, 99, 235, 0.45);
  cursor: pointer;
  z-index: 1350;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}

.ai-float-toggle:hover {
  transform: translateY(-2px);
  background: #2563eb;
  box-shadow: 0 14px 32px rgba(37, 99, 235, 0.55);
}
</style>
