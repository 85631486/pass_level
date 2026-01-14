<template>
  <div class="visual-editor">
    <!-- 工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <button class="toolbar-btn primary" @click="saveChanges" :disabled="saving">
          <span class="icon">💾</span>
          {{ saving ? '保存中...' : '保存' }}
        </button>
        <button class="toolbar-btn" @click="preview" :disabled="!hasContent">
          <span class="icon">👁️</span>
          预览
        </button>
      </div>
      <div class="toolbar-center">
        <div class="step-info">
          <span class="step-title">{{ currentStep?.title || '未命名步骤' }}</span>
          <span class="step-meta">{{ componentCount }} 个组件</span>
        </div>
      </div>
      <div class="toolbar-right">
        <button class="toolbar-btn" @click="undo" :disabled="!canUndo" title="撤销">
          ↶ 撤销
        </button>
        <button class="toolbar-btn" @click="togglePropertyPanel" title="显示/隐藏 属性面板">
          {{ propertyVisible ? '隐藏属性' : '显示属性' }}
        </button>
        <button class="toolbar-btn" @click="togglePageNav" title="显示/隐藏 页面导航">
          {{ pageNavVisible ? '隐藏页面栏' : '显示页面栏' }}
        </button>
        <button class="toolbar-btn" @click="redo" :disabled="!canRedo" title="重做">
          ↷ 重做
        </button>
        <button class="toolbar-btn" @click="showHelp = !showHelp" title="帮助">
          ❓
        </button>
      </div>
    </div>

    <!-- 主编辑区 -->
    <div class="editor-body" :style="editorGridStyle">
      <!-- 左侧：组件库 -->
      <aside class="component-library">
        <div class="library-header">
          <h3>组件库</h3>
          <span class="component-count">{{ componentList.length }} 个组件</span>
        </div>
        <div class="component-list">
          <div
            v-for="comp in componentList"
            :key="comp.type"
            class="component-item"
            :data-type="comp.type"
            draggable="true"
            @dragstart="handleDragStart($event, comp)"
            @click="showComponentPreview(comp)"
          >
            <div class="component-icon">{{ comp.icon }}</div>
            <div class="component-info">
              <div class="component-name">{{ comp.name }}</div>
              <div class="component-desc">{{ comp.description }}</div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 中间：画布编辑区 -->
      <main class="canvas-area">
        <div v-if="currentStep" class="canvas-wrapper">
          <CanvasEditor
            ref="canvasEditorRef"
            :components="currentStep.components || []"
            :canvas-config="currentStep.canvasConfig"
            :selected-component-id="selectedComponentId"
            @update:components="updateCurrentStepComponents"
            @update:canvas-config="updateCurrentStepCanvasConfig"
            @component-drop="handleComponentDrop"
            @component-select="handleComponentSelect"
          />
        </div>
        <div v-else class="empty-canvas">
          <div class="empty-state">
            <div class="empty-icon">🎨</div>
            <h3>开始创建交互式内容</h3>
            <p>从左侧组件库拖拽组件到画布上开始编辑</p>
            <button class="add-step-btn" @click="initializeStep">
              创建新步骤
            </button>
          </div>
        </div>
      </main>

      <!-- 右侧：属性面板 -->
      <aside class="property-panel">
        <div v-if="selectedComponent" class="panel-content">
          <div class="panel-header">
            <h3>编辑组件</h3>
            <button class="close-btn" @click="selectedComponentId = null">×</button>
          </div>
          <ComponentPropertyEditor
            :component="selectedComponent"
            @update="updateComponent"
            @delete="handleComponentDelete"
          />
        </div>
        <div v-else-if="currentStep" class="panel-content">
          <div class="panel-header">
            <h3>步骤设置</h3>
          </div>
          <StepPropertyEditor
            :step="currentStep"
            @update="updateStep"
          />
        </div>
        <div v-else class="empty-panel">
          <div class="empty-icon">⚙️</div>
          <p>选择组件或步骤进行编辑</p>
        </div>
      </aside>
    </div>

    <!-- 帮助面板 -->
    <div v-if="showHelp" class="help-overlay" @click="showHelp = false">
      <div class="help-panel" @click.stop>
        <div class="help-header">
          <h3>编辑器使用帮助</h3>
          <button class="close-btn" @click="showHelp = false">×</button>
        </div>
        <div class="help-content">
          <div class="help-section">
            <h4>🎯 基本操作</h4>
            <ul>
              <li><strong>添加组件：</strong>从左侧组件库拖拽到画布</li>
              <li><strong>选择组件：</strong>点击组件进行选择</li>
              <li><strong>移动组件：</strong>拖拽选中的组件</li>
              <li><strong>调整大小：</strong>拖拽组件边缘的圆点</li>
            </ul>
          </div>
          <div class="help-section">
            <h4>⌨️ 快捷键</h4>
            <ul>
              <li><kbd>Ctrl+Z</kbd> 撤销</li>
              <li><kbd>Ctrl+Y</kbd> 重做</li>
              <li><kbd>Delete</kbd> 删除选中的组件</li>
              <li><kbd>Ctrl+A</kbd> 全选</li>
              <li><kbd>F1</kbd> 显示/隐藏快捷键</li>
            </ul>
          </div>
          <div class="help-section">
            <h4>💡 提示</h4>
            <ul>
              <li>组件可以重叠，调整图层层级</li>
              <li>使用鼠标滚轮可以缩放画布</li>
              <li>右键组件可以打开上下文菜单</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 组件预览提示 -->
    <div v-if="previewComponent" class="component-preview-tooltip">
      <div class="preview-content">
        <div class="preview-icon">{{ previewComponent.icon }}</div>
        <div class="preview-info">
          <div class="preview-name">{{ previewComponent.name }}</div>
          <div class="preview-desc">{{ previewComponent.description }}</div>
        </div>
      </div>
    </div>
    <!-- 底部页面导航：新建页面 + 浏览历史缩略图 -->
    <div class="page-navigation" :class="{ hidden: !pageNavVisible }">
      <div class="nav-left">
        <button class="nav-btn" @click="prevPage" :disabled="!hasPrev">上一页</button>
        <button class="nav-btn" @click="nextPage">下一页</button>
        <button class="nav-btn" @click="createNewPage">新建页面</button>
      </div>
      <div class="nav-right">
          <div class="page-thumbnails" style="display:flex;gap:8px;align-items:center;overflow:auto;max-width:70vw;padding:8px 0">
            <div v-for="(step, idx) in (courseData.steps || [])" :key="step.id" class="page-item"
              :class="{ active: step.id === selectedStepId, 'drag-over': dragOverIdx === idx }"
              @click="goToPage(idx)"
              @contextmenu.prevent.stop="showPageContext(idx, $event)"
              title="切换页面"
              draggable="true"
              @dragstart="onThumbnailDragStart($event, idx)"
              @dragover.prevent="onThumbnailDragOver($event, idx)"
              @drop.prevent="onThumbnailDrop($event, idx)"
              @dragend="onThumbnailDragEnd"
            >
            <div class="page-thumbnail">
              <img v-if="(step as any).__thumb" :src="(step as any).__thumb" alt="thumb" class="page-thumbnail-img" />
              <div v-else class="page-thumbnail-fallback"></div>
              <!-- badge shown on hover -->
              <div class="page-thumb-badge">第{{ idx + 1 }}页</div>
            </div>
          </div>
          </div>
        </div>
      </div>
    </div>
  <!-- page context menu -->
  <div v-if="pageContext.visible" class="page-context-menu" :style="{ left: pageContext.x + 'px', top: pageContext.y + 'px' }" @click.stop>
    <div class="context-item" @click="handleContextDelete">删除页面</div>
    <div class="context-item" @click="handleContextCopy">复制页面</div>
    <div class="context-item" @click="handleContextRename">重命名页面</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount, onMounted, nextTick } from 'vue'
import type { CourseData, CourseStep, StepComponent, CanvasConfig } from '../types/coursePlayer'
import StepPropertyEditor from './panels/StepPropertyEditor.vue'
import ComponentPropertyEditor from './panels/ComponentPropertyEditor.vue'
import CanvasEditor from './editor/CanvasEditor.vue'
import { levelsApi } from '../api/levels'
import { getFeedbackSystem } from '../utils/feedbackSystem'
import { autoLayoutComponents, hasOverlappingComponents } from '../utils/autoLayout'

const feedbackSystem = getFeedbackSystem()

interface ComponentDefinition {
  type: string
  name: string
  icon: string
  description: string
}

// page context menu state (right-click on thumbnail)
const pageContext = ref<{ visible: boolean; x: number; y: number; idx: number }>({ visible: false, x: 0, y: 0, idx: -1 })

const props = defineProps<{
  levelId: number
  initialData?: CourseData | null
}>()

const emit = defineEmits<{
  (e: 'save', data: CourseData): void
  (e: 'preview', data: CourseData): void
}>()

// 响应式数据
const saving = ref(false)
const courseData = ref<CourseData>({
  steps: [],
  meta: {}
})

const selectedStepId = ref<string | null>(null)
const selectedComponentId = ref<string | null>(null)
const showHelp = ref(false)
const propertyVisible = ref(true)
const canvasEditorRef = ref<any>(null)
// computed grid style to collapse/expand property panel
const editorGridStyle = computed(() => {
  return {
    gridTemplateColumns: propertyVisible.value ? '200px 1fr 300px' : '200px 1fr 0px'
  }
})
// page navigation visibility
const pageNavVisible = ref(true)
const previewComponent = ref<ComponentDefinition | null>(null)
// reference to child CanvasEditor so we can request a thumbnail image when saving history
// (canvasEditorRef moved above)

// 编辑历史
const history = ref<CourseData[]>([])
const historyIndex = ref(-1)
// drag-reorder state for page thumbnails
const draggingIdx = ref<number | null>(null)
const dragOverIdx = ref<number | null>(null)

// (no automatic title preview; thumbnails display images only)

// 计算属性
const canUndo = computed(() => historyIndex.value > 0)
const canRedo = computed(() => historyIndex.value < history.value.length - 1)

const currentStep = computed(() => {
  const steps = courseData.value.steps || []
  if (steps.length === 0) return null
  // prefer explicit selectedStepId, fallback to first step
  if (selectedStepId.value) {
    const found = steps.find(s => s.id === selectedStepId.value)
    if (found) return found
  }
  // if no selectedStepId or not found, pick first
  return steps[0] || null
})

const selectedComponent = computed(() => {
  if (!selectedComponentId.value || !currentStep.value) return null
  return (currentStep.value.components || []).find(c => c.id === selectedComponentId.value) || null
})

const hasContent = computed(() => {
  return currentStep.value && (currentStep.value.components || []).length > 0
})

const componentCount = computed(() => {
  return currentStep.value ? (currentStep.value.components || []).length : 0
})

const currentStepIndex = computed(() => {
  const steps = courseData.value.steps || []
  return steps.findIndex(s => s.id === selectedStepId.value)
})

const hasPrev = computed(() => currentStepIndex.value > 0)

// 组件库定义
const componentList: ComponentDefinition[] = [
  { type: 'text', name: '标题组件', icon: '📝', description: '显示标题文本，默认大号加粗' },
  { type: 'code', name: '代码编辑器', icon: '💻', description: '交互式代码编辑和运行' },
  { type: 'quiz', name: '题目', icon: '🎯', description: '创建选择题和判断题' },
  { type: 'video', name: '视频', icon: '🎬', description: '嵌入视频播放器' },
  { type: 'image', name: '图片', icon: '🖼️', description: '显示图片和图表' },
  { type: 'drawing', name: '绘图', icon: '🎨', description: '手绘和图形绘制' },
  { type: 'dragdrop', name: '拖拽排序', icon: '🔄', description: '拖拽排序练习' },
]

// 加载数据
async function loadData() {
  try {
    const response = await levelsApi.getCourseData(props.levelId)
    if (response.data && response.data.steps && response.data.steps.length > 0) {
      courseData.value = migrateData(response.data)
      saveToHistory()
      // 自动选中第一个步骤（防止 steps 未定义）
      const steps = courseData.value?.steps || []
      if (steps.length > 0) {
        selectedStepId.value = steps[0]!.id
        selectedComponentId.value = null
      }
    } else {
      // 如果没有数据，初始化空结构
      courseData.value = {
        steps: [],
        meta: {}
      }
      saveToHistory()
    }
  } catch (error: any) {
    console.error('Failed to load course data:', error)
    feedbackSystem.showToast('加载数据失败：' + (error.response?.data?.detail || error.message), 'error')
    // 初始化空结构
    courseData.value = {
      steps: [],
      meta: {}
    }
    saveToHistory()
  }
}

// 数据迁移：为旧数据设置默认值，并将内容转换为组件
function migrateData(data: CourseData): CourseData {
  const migrated = JSON.parse(JSON.stringify(data))
  
  migrated.steps = migrated.steps.map((step: CourseStep) => {
    // 设置默认画布配置
    if (!step.canvasConfig) {
      step.canvasConfig = {
        width: 1920,
        height: 1080,
        backgroundColor: '#ffffff',
      }
    }
    
    // 应用自动布局算法以修复组件重叠问题
    const canvasWidth = step.canvasConfig?.width || 1920
    const canvasHeight = step.canvasConfig?.height || 1080
    if (step.components && step.components.length > 0 && hasOverlappingComponents(step.components)) {
      step.components = autoLayoutComponents(step.components, canvasWidth, canvasHeight, 20)
    }
    
    // 确保组件数组存在并使用局部变量统一引用，避免类型推断问题
    const comps: StepComponent[] = (step.components || []) as StepComponent[]
    
    // 如果步骤有标题但没有对应的标题组件，创建一个标题组件
    if (step.title) {
      // Do not auto-create a title component from step.title.
    }
    
    // 如果步骤有内容但没有对应的文本组件，创建一个文本组件
    if (step.content || step.contentHtml) {
      const contentText = step.contentHtml || step.content || ''
      const hasContentComponent = comps.some(c => {
        if (c.type !== 'text') return false
        const compContent = c.config?.content || ''
        return compContent.substring(0, 100) === contentText.substring(0, 100) ||
               compContent.includes(contentText.substring(0, 50)) ||
               contentText.includes(compContent.substring(0, 50))
      })
      
      if (!hasContentComponent && contentText.trim()) {
        const contentComponent: StepComponent = {
          id: `content-${step.id}`,
          type: 'text',
          config: {
            content: contentText,
          },
          position: {
            x: 100,
            y: 200,
            width: 1720,
            height: 600,
          },
          style: {
            fontSize: 18,
            fontWeight: 400,
            color: '#374151',
            textAlign: 'left',
            padding: '30px',
            margin: '0',
            backgroundColor: 'transparent',
          },
        }
        comps.push(contentComponent)
      }
    }
    
    // 如果步骤有题目但没有对应的题目组件，创建题目组件
    if (step.questions && step.questions.length > 0) {
      step.questions.forEach((question, qIdx) => {
        const hasQuizComponent = comps.some(c =>
          c.type === 'quiz' && 
          (c.config?.question === question.text || c.id === `quiz-${step.id}-${qIdx}`)
        )
        
        if (!hasQuizComponent) {
          const quizComponent: StepComponent = {
            id: `quiz-${step.id}-${qIdx}`,
            type: 'quiz',
            config: {
              question: question.text,
              options: question.options.map(opt => ({
                value: opt.value,
                text: opt.text,
              })),
              answer: question.correctAnswer,
              explanation: question.explanation,
            },
            position: {
              x: 100 + (qIdx % 2) * 900,
              y: 850 + Math.floor(qIdx / 2) * 400,
              width: 800,
              height: 350,
            },
            style: {
              fontSize: 16,
              color: '#374151',
              padding: '20px',
              backgroundColor: '#ffffff',
              borderRadius: 8,
              borderWidth: 1,
              borderStyle: 'solid',
              borderColor: '#e5e7eb',
            },
          }
          comps.push(quizComponent)
        }
      })
    }
    
    // 为所有组件设置默认位置和样式（如果缺失）
    const existingPositions: Array<{ x: number; y: number; width: number; height: number }> = []
    
    const normalized = comps.map((comp: StepComponent, idx: number) => {
      if (!comp.position) {
        const defaultSizes: Record<string, { width: number; height: number }> = {
          text: { width: 800, height: 400 },
          code: { width: 1000, height: 500 },
          quiz: { width: 800, height: 400 },
          video: { width: 1000, height: 600 },
          image: { width: 600, height: 400 },
          drawing: { width: 800, height: 600 },
          dragdrop: { width: 800, height: 500 },
        }
        
        const size = defaultSizes[comp.type] || { width: 300, height: 200 }
        
        let x = 100
        let y = 100 + idx * 450
        let attempts = 0
        while (attempts < 10) {
          const overlaps = existingPositions.some(pos => 
            !(x + size.width < pos.x || x > pos.x + pos.width || 
              y + size.height < pos.y || y > pos.y + pos.height)
          )
          if (!overlaps) break
          x += 50
          if (x + size.width > (step.canvasConfig?.width ?? 1920) - 100) {
            x = 100
            y += size.height + 50
          }
          attempts++
        }
        
        comp.position = {
          x,
          y,
          width: size.width,
          height: size.height,
        }
        
        existingPositions.push(comp.position)
      } else {
        existingPositions.push(comp.position)
      }
      
      if (!comp.style) {
        comp.style = {}
      }
      return comp
    })
    
    step.components = normalized
    return step
  })
  
  return migrated
}

// 初始化数据
onMounted(() => {
  if (props.initialData && props.initialData.steps && props.initialData.steps.length > 0) {
    courseData.value = migrateData(props.initialData)
    saveToHistory()
    // 自动选中第一个步骤（防止 steps 未定义）
    const steps = courseData.value?.steps || []
    if (steps.length > 0) {
      selectedStepId.value = steps[0]!.id
      selectedComponentId.value = null
    }
  } else {
    loadData()
  }
})
// hide page context on any click outside
onMounted(() => {
  window.addEventListener('click', hidePageContext)
})

// 监听 initialData 变化
watch(() => props.initialData, (newData) => {
  if (newData && newData.steps && newData.steps.length > 0 && (courseData.value?.steps || []).length === 0) {
    courseData.value = migrateData(newData)
    saveToHistory()
    // 自动选中第一个步骤（防止 steps 未定义）
    const steps = courseData.value?.steps || []
    if (steps.length > 0) {
      selectedStepId.value = steps[0]!.id
      selectedComponentId.value = null
    }
  }
}, { deep: true })

// 保存到历史
function saveToHistory() {
  // 确保courseData有有效数据
  if (!courseData.value || !courseData.value.steps) {
    return
  }
  
  const snapshot = JSON.parse(JSON.stringify(courseData.value))
  
  // 如果历史记录为空，先添加初始状态
  if (history.value.length === 0) {
    history.value.push(snapshot)
    historyIndex.value = 0
    return
  }
  
  // 检查是否与上一个历史记录相同（避免重复记录）
  const lastHistory = history.value[historyIndex.value]
  if (JSON.stringify(lastHistory) === JSON.stringify(snapshot)) {
    return
  }
  
  history.value = history.value.slice(0, historyIndex.value + 1)
  history.value.push(snapshot)
  historyIndex.value = history.value.length - 1
  
  // 限制历史记录数量
  if (history.value.length > 50) {
    history.value.shift()
    historyIndex.value--
  }
  // 不在 saveToHistory() 中生成缩略图（缩略图应仅在用户点击保存时生成）
}

// 撤销
function undo() {
  if (canUndo.value) {
    historyIndex.value--
    const snapshot = JSON.parse(JSON.stringify(history.value[historyIndex.value]))
    courseData.value = snapshot
    feedbackSystem.showToast('已撤销', 'info')
  }
}

// 重做
function redo() {
  if (canRedo.value) {
    historyIndex.value++
    const snapshot = JSON.parse(JSON.stringify(history.value[historyIndex.value]))
    courseData.value = snapshot
    feedbackSystem.showToast('已重做', 'info')
  }
}

// 处理组件选择
function handleComponentSelect(componentId: string | null) {
  selectedComponentId.value = componentId
}

// 初始化步骤
function initializeStep() {
  const newStep: CourseStep = {
    id: `step-${Date.now()}`,
    type: 'content',
    title: '',
    components: [],
    canvasConfig: {
      width: 1920,
      height: 1080,
      backgroundColor: '#ffffff',
    },
  }

  courseData.value.steps = [newStep]
  selectedStepId.value = newStep.id
  selectedComponentId.value = null
  onContentChange()

  feedbackSystem.showToast('已创建新步骤', 'success')
}

// 新建页面（追加一个空步骤）
function createNewPage() {
  const newStep: CourseStep = {
    id: `step-${Date.now()}`,
    type: 'content',
    title: '',
    components: [],
    canvasConfig: {
      width: 1920,
      height: 1080,
      backgroundColor: '#ffffff',
    },
  }
  courseData.value.steps = courseData.value.steps || []
  courseData.value.steps.push(newStep)
  // 选中新页面
  selectedStepId.value = newStep.id
  selectedComponentId.value = null
  onContentChange()
  feedbackSystem.showToast('已创建新页面', 'success')
}

// 历史版本切换功能已保留但 goToHistory 不再在此文件内部使用.

// 跳转到页面（按页面索引）
function goToPage(idx: number) {
  // before switching, save current step snapshot
  onContentChange()
  const steps = courseData.value.steps || []
  if (idx < 0 || idx >= steps.length) return
  const target = steps[idx]
  if (!target) return
  selectedStepId.value = target.id
  selectedComponentId.value = null
  feedbackSystem.showToast(`已切换到 页面${idx + 1}`, 'info')
}

// 上一页 / 下一页 功能：在切换时保存当前页面并切换
function prevPage() {
  const idx = currentStepIndex.value
  if (idx <= 0) return
  // save current page
  onContentChange()
  goToPage(idx - 1)
}

function nextPage() {
  const steps = courseData.value.steps || []
  const idx = currentStepIndex.value
  // save current page first
  onContentChange()
  if (idx === -1 || idx === steps.length - 1) {
    // create new blank page and switch to it
    createNewPage()
    // new page will be appended; its index is steps.length - 1
    const newIdx = (courseData.value.steps || []).length - 1
    goToPage(newIdx)
  } else {
    goToPage(idx + 1)
  }
}

// 已移除批量生成缩略图功能：缩略图仅在用户点击“保存”时生成

// 删除页面（确认后移除），保证至少保留一个页面
function deletePage(idx: number) {
  const steps = courseData.value.steps || []
  if (idx < 0 || idx >= steps.length) return
  const step = steps[idx]
  if (!step) return
  const ok = window.confirm(`确认删除 页面${idx + 1} 吗？此操作不可撤销。`)
  if (!ok) return
  // save current state to history so deletion can be undone
  saveToHistory()
  steps.splice(idx, 1)
  courseData.value.steps = steps

  // 如果删除的是当前选中页，切换到相邻页（优先上一页）
  if (selectedStepId.value === step.id) {
    if (steps.length === 0) {
      // 如果没有页面了，新建一个空页
      createNewPage()
    } else {
      const newIndex = Math.max(0, idx - 1)
      const target = steps[newIndex]
      selectedStepId.value = target ? target.id : null
    }
    selectedComponentId.value = null
  }

  // 保存历史快照
  onContentChange()
  feedbackSystem.showToast(`已删除 页面${idx + 1}`, 'info')
}

function showPageContext(idx: number, e: MouseEvent) {
  pageContext.value = { visible: true, x: e.clientX, y: e.clientY, idx }
}

function hidePageContext() {
  pageContext.value.visible = false
}

function togglePropertyPanel() {
  propertyVisible.value = !propertyVisible.value
  // after layout change, ask CanvasEditor to refit the canvas
  nextTick(() => {
    try {
      const cref = canvasEditorRef.value
      if (cref && typeof cref.fitToScreen === 'function') {
        cref.fitToScreen()
      }
    } catch (e) {
      console.error('fitToScreen failed on toggle', e)
    }
  })
}

function togglePageNav() {
  pageNavVisible.value = !pageNavVisible.value
  // after layout change, ask CanvasEditor to refit the canvas
  nextTick(() => {
    try {
      const cref = canvasEditorRef.value
      if (cref && typeof cref.fitToScreen === 'function') {
        cref.fitToScreen()
      }
    } catch (e) {
      console.error('fitToScreen failed on togglePageNav', e)
    }
  })
}

// --- thumbnail drag-and-drop handlers ---
function onThumbnailDragStart(e: DragEvent, idx: number) {
  draggingIdx.value = idx
  try {
    if (e.dataTransfer) e.dataTransfer.setData('text/plain', String(idx))
  } catch (err) {}
}

function onThumbnailDragOver(e: DragEvent, idx: number) {
  // indicate potential drop position
  dragOverIdx.value = idx
  e.preventDefault()
}

function onThumbnailDrop(e: DragEvent, idx: number) {
  e.preventDefault()
  const from = draggingIdx.value != null ? draggingIdx.value : Number(e.dataTransfer?.getData('text/plain') || -1)
  const to = idx
  draggingIdx.value = null
  dragOverIdx.value = null
  if (from < 0 || to < 0 || from === to) return
  const steps = courseData.value.steps || []
  if (from >= steps.length || to > steps.length) return
  const item = steps.splice(from, 1)[0]
  if (!item) return
  // compute insert index after removal: if removed before target, target index decreases by 1
  let insertIndex = from < to ? to - 1 : to
  insertIndex = Math.max(0, Math.min(steps.length, insertIndex))
  steps.splice(insertIndex, 0, item)
  courseData.value.steps = [...steps]
  // keep selection on moved page
  selectedStepId.value = item.id
  onContentChange()
}

function onThumbnailDragEnd() {
  draggingIdx.value = null
  dragOverIdx.value = null
}

// 复制页面：深拷贝指定步骤并插入到后面，选中新页面
function copyPage(idx: number) {
  const steps = courseData.value.steps || []
  if (idx < 0 || idx >= steps.length) return
  // ensure current changes saved
  onContentChange()
  const original = steps[idx]
  if (!original) return
  const copy = JSON.parse(JSON.stringify(original)) as CourseStep
  copy.id = `step-${Date.now()}`
  // make a readable title for the copy
  // do not auto-assign title to copied pages
  copy.title = ''
  // insert after original
  steps.splice(idx + 1, 0, copy)
  courseData.value.steps = steps
  // select the new copied page
  selectedStepId.value = copy.id
  selectedComponentId.value = null
  // record history
  onContentChange()
  feedbackSystem.showToast('已复制页面', 'success')
}

// 重命名页面：提示用户输入新名称并保存
function renamePage(idx: number) {
  const steps = courseData.value.steps || []
  if (idx < 0 || idx >= steps.length) return
  const step = steps[idx]
  if (!step) return
  const currentTitle = step.title || `页面${idx + 1}`
  const newTitle = window.prompt('输入新页面名称：', currentTitle)
  if (newTitle === null) return // user cancelled
  const trimmed = String(newTitle).trim()
  if (!trimmed) {
    feedbackSystem.showToast('名称不能为空', 'error')
    return
  }
  step.title = trimmed
  courseData.value.steps = steps
  onContentChange()
  feedbackSystem.showToast('页面已重命名', 'success')
}

function handleContextDelete() {
  const idx = pageContext.value?.idx ?? -1
  if (idx >= 0) deletePage(idx)
  hidePageContext()
}

function handleContextCopy() {
  const idx = pageContext.value?.idx ?? -1
  if (idx >= 0) copyPage(idx)
  hidePageContext()
}

function handleContextRename() {
  const idx = pageContext.value?.idx ?? -1
  if (idx >= 0) renamePage(idx)
  hidePageContext()
}

// return truncated title preview for thumbnail (first 3 chars + ellipsis) or empty if no title
// No title preview functions — thumbnails show images only.

// 拖拽开始
function handleDragStart(event: DragEvent, component: ComponentDefinition) {
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'copy'
    event.dataTransfer.setData('component-type', component.type)
    event.dataTransfer.setData('component-data', JSON.stringify(component))
  }
}

// 处理组件拖拽到画布
function handleComponentDrop(componentType: string, position: { x: number; y: number }) {
  if (!currentStep.value) {
    initializeStep()
    return
  }

  // 确保 step 存在以便类型推断
  const step = currentStep.value!
  step.components = step.components || []

  const newComponent: StepComponent = {
    id: `comp-${Date.now()}`,
    type: componentType as any,
    config: getDefaultConfig(componentType),
    position: {
      x: position.x,
      y: position.y,
      width: 300,
      height: 200,
    },
    style: componentType === 'text' ? { fontSize: 48, fontWeight: 700, color: '#111827' } : {},
  }

  step.components.push(newComponent)
  selectedComponentId.value = newComponent.id
  onContentChange()

  feedbackSystem.showToast(`已添加 ${getComponentName(componentType)} 组件`, 'success')
}

// 更新当前步骤的组件
function updateCurrentStepComponents(components: StepComponent[]) {
  if (!currentStep.value) return
  const step = currentStep.value!
  step.components = components
  onContentChange()
}

// 更新当前步骤的画布配置
function updateCurrentStepCanvasConfig(config: CanvasConfig) {
  if (!currentStep.value) return
  currentStep.value.canvasConfig = config
  onContentChange()
}

// 删除组件
function handleComponentDelete() {
  if (!currentStep.value || !selectedComponentId.value) return
  const step = currentStep.value!

  const comps = step.components || []
  const index = comps.findIndex(c => c.id === selectedComponentId.value)
    if (index !== -1) {
    const componentName = getComponentName(comps[index]!.type)
    comps.splice(index, 1)
    step.components = comps
      selectedComponentId.value = null
      onContentChange()
      feedbackSystem.showToast(`已删除 ${componentName} 组件`, 'info')
  }
}

// 更新步骤
function updateStep(updatedStep: CourseStep) {
  const index = courseData.value.steps.findIndex(s => s.id === updatedStep.id)
  if (index !== -1) {
    courseData.value.steps[index] = { ...courseData.value.steps[index], ...updatedStep }
    onContentChange()
  }
}

// 更新组件
function updateComponent(updatedComponent: StepComponent) {
  if (!currentStep.value) return
  const step = currentStep.value!

  const comps = step.components || []
  const index = comps.findIndex(c => c.id === updatedComponent.id)
  if (index !== -1) {
    comps[index] = { ...comps[index], ...updatedComponent }
    step.components = comps
    onContentChange()
  }
}

// 内容变化处理
function onContentChange() {
  saveToHistory()
}

// 获取默认配置
function getDefaultConfig(type: string): any {
  const configs: Record<string, any> = {
    text: { content: '在这里输入文本内容...' },
    code: { language: 'python', template: '', testCases: [] },
    quiz: { question: '问题内容？', options: [
      { value: 'A', text: '选项A' },
      { value: 'B', text: '选项B' },
      { value: 'C', text: '选项C' }
    ], answer: 'A' },
    video: { url: '', checkpoints: [] },
    image: { url: '', alt: '图片描述' },
    drawing: { tools: ['pen'], backgroundImage: '' },
    dragdrop: { items: ['项目1', '项目2', '项目3'], targetZones: ['区域1', '区域2'] }
  }
  return configs[type] || { content: '' }
}

// 获取组件名称
function getComponentName(type: string): string {
  const comp = componentList.find(c => c.type === type)
  return comp?.name || type
}

// 显示组件预览
function showComponentPreview(component: ComponentDefinition) {
  previewComponent.value = component
  setTimeout(() => {
    previewComponent.value = null
  }, 2000)
}

// 保存更改
async function saveChanges() {
  if (!courseData.value || !courseData.value.steps || courseData.value.steps.length === 0) {
    feedbackSystem.showToast('请先创建至少一个步骤', 'error')
    return
  }

  saving.value = true
  try {
    await levelsApi.updateCourseData(props.levelId, courseData.value)
    emit('save', courseData.value)
    feedbackSystem.showToast('保存成功！', 'success')
    saveToHistory()
    // 在保存时为当前步骤生成缩略图并持久化（如果 CanvasEditor 提供 exportThumbnail）
    try {
      const canvasRef = canvasEditorRef.value
      if (canvasRef && typeof canvasRef.exportThumbnail === 'function') {
        const dataUrl = await canvasRef.exportThumbnail()
        if (dataUrl) {
          const step = currentStep.value
          if (step) {
            ;(step as any).__thumb = dataUrl
            // persist the thumbnail to backend (一次性更新，不阻塞用户)
            try {
              await levelsApi.updateCourseData(props.levelId, courseData.value)
            } catch (e) {
              console.error('Failed to persist thumbnail:', e)
            }
          }
        }
      }
    } catch (e) {
      console.error('exportThumbnail error on save:', e)
    }
  } catch (error: any) {
    const message = error.response?.data?.detail || error.message || '保存失败'
    feedbackSystem.showToast('保存失败：' + message, 'error')
    console.error('Failed to save course data:', error)
  } finally {
    saving.value = false
  }
}

// 预览
function preview() {
  if (!hasContent.value) {
    feedbackSystem.showToast('请先添加一些组件再预览', 'error')
    return
  }
  emit('preview', courseData.value)
}

// 组件卸载时清理
onBeforeUnmount(() => {
  feedbackSystem.destroy()
  window.removeEventListener('click', hidePageContext)
})
</script>

<style scoped>
.visual-editor {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f3f4f6;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 0.5rem;
}

.toolbar-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #ffffff;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.toolbar-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.toolbar-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.editor-body {
  display: grid;
  grid-template-columns: 200px 1fr 300px;
  gap: 1rem;
  padding: 1rem;
  flex: 1;
  overflow: hidden;
}

.component-library {
  background: #ffffff;
  border-radius: 8px;
  padding: 1rem;
  overflow-y: auto;
}

.component-library h3 {
  margin: 0 0 1rem;
  font-size: 1rem;
  font-weight: 600;
}

.component-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.component-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: grab;
  transition: all 0.2s;
  user-select: none;
  -webkit-user-drag: element;
}

.component-item:active {
  cursor: grabbing;
}

.component-item:hover {
  background: #f3f4f6;
  border-color: #3b82f6;
}

.component-item:active {
  cursor: grabbing;
}

.component-item .icon {
  font-size: 1.25rem;
}

.canvas-area {
  background: #ffffff;
  border-radius: 8px;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.canvas-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.step-header-bar {
  padding: 0.75rem 1rem;
  background: #f3f4f6;
  border-bottom: 1px solid #e5e7eb;
  border-radius: 8px 8px 0 0;
}

.step-header-bar h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.empty-canvas {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6b7280;
  gap: 1rem;
}

.step-container {
  margin-bottom: 1.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s;
}

.step-container.selected {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.step-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.step-number {
  font-size: 0.875rem;
  color: #6b7280;
}

.step-title-input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 1rem;
}

.step-actions {
  display: flex;
  gap: 0.25rem;
}

.step-actions button {
  padding: 0.25rem 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: #ffffff;
  cursor: pointer;
}

.step-content-area {
  min-height: 100px;
  padding: 1rem;
  border: 2px dashed #d1d5db;
  border-radius: 6px;
}

.component-preview {
  margin-bottom: 0.75rem;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.component-preview.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.component-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.component-delete {
  margin-left: auto;
  padding: 0.25rem 0.5rem;
  border: none;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 4px;
  cursor: pointer;
}

.add-component-hint {
  text-align: center;
  color: #9ca3af;
  padding: 2rem;
}

.add-step-btn {
  width: 100%;
  padding: 1rem;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  background: #ffffff;
  cursor: pointer;
  font-size: 1rem;
  color: #6b7280;
  transition: all 0.2s;
}

.add-step-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.property-panel {
  background: #ffffff;
  border-radius: 8px;
  padding: 1rem;
  overflow-y: auto;
}

.property-panel h3 {
  margin: 0 0 1rem;
  font-size: 1rem;
  font-weight: 600;
}

.empty-panel {
  text-align: center;
  color: #9ca3af;
  padding: 2rem;
}


.page-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: #ffffff;
  border-top: 1px solid #e5e7eb;
}

.nav-left,
.nav-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #ffffff;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.nav-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-indicator {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.page-list-sidebar {
  position: fixed;
  right: 0;
  top: 0;
  bottom: 0;
  width: 300px;
  background: #ffffff;
  border-left: 1px solid #e5e7eb;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.sidebar-header button {
  padding: 0.25rem 0.5rem;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 1.5rem;
  color: #6b7280;
}

.sidebar-header button:hover {
  color: #374151;
}

.page-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.page-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 0.5rem;
}

.page-item:hover {
  background: #f3f4f6;
}

.page-item.active {
  background: #eff6ff;
  border: 1px solid #3b82f6;
}

.page-thumbnail {
  width: 60px;
  height: 40px;
  background: #f3f4f6;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.page-thumbnail-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}
.page-thumbnail-fallback {
  font-size: 0.75rem;
  color: #6b7280;
  text-align: center;
}
.page-delete {
  margin-left: 8px;
  background: transparent;
  border: none;
  color: #ef4444;
  font-weight: 700;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
}
.page-item:hover .page-delete {
  background: rgba(239,68,68,0.08);
}
.page-navigation.hidden {
  height: 0;
  padding-top: 0;
  padding-bottom: 0;
  overflow: hidden;
  opacity: 0;
  transition: all 0.18s ease;
}
.page-context-menu {
  position: fixed;
  z-index: 2000;
  background: white;
  border: 1px solid #e5e7eb;
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
  border-radius: 6px;
  overflow: hidden;
}
.page-context-menu .context-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 0.9rem;
}
.page-context-menu .context-item:hover {
  background: #f3f4f6;
}

.page-thumb-label {
  position: absolute;
  top: 4px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255,255,255,0.8);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #374151;
  pointer-events: none;
  white-space: nowrap;
  max-width: 80%;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
}

.page-thumb-badge {
  position: absolute;
  right: 4px;
  bottom: 2px;
  background: rgba(0,0,0,0.6);
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.7rem;
  opacity: 0;
  transition: opacity 0.15s;
  pointer-events: none;
}
.page-item:hover .page-thumb-badge {
  opacity: 1;
}
.page-item.drag-over {
  outline: 2px dashed #3b82f6;
  transform: scale(1.02);
}

.page-number {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
}

.page-item.active .page-number {
  color: #3b82f6;
}

.page-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.page-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.page-meta {
  font-size: 0.75rem;
  color: #6b7280;
}
</style>

