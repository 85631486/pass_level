<template>
  <div class="canvas-editor" ref="editorRef">
    <!-- 画布容器 -->
    <div
      class="canvas-container"
      ref="canvasContainerRef"
      :style="[canvasStyle, { left: canvasPagePos.x + 'px', top: canvasPagePos.y + 'px' }]"
      @drop="handleDrop"
      @dragover.prevent
      @mousedown="handleCanvasMouseDown"
      @wheel="handleWheel"
    >
      <!-- page-level drag handle for the canvas to allow moving the whole canvas on the page -->
      <div class="canvas-drag-handle" title="拖动画布" @mousedown.stop.prevent="startCanvasDrag($event)"></div>
      <!-- 画布背景网格 -->
      <div class="canvas-grid" :style="gridStyle"></div>

      <!-- 画布内容区域 -->
      <div
        class="canvas-content"
        :style="contentStyle"
      >
        <!-- 渲染所有步骤组件 -->
        <div
          v-for="component in components"
          :key="component.id"
            :data-id="component.id"
          class="canvas-component"
          :class="{ selected: isComponentSelected(component.id) }"
          :style="getComponentStyle(component)"
          @mousedown="handleComponentMouseDown($event, component)"
          @dblclick="handleComponentDoubleClick(component)"
        >
          <!-- 组件内容 -->
          <div class="component-content">
            <StepComponentRenderer
              :component="component"
              :embedded="true"
              @content-size="handleContentSizeChange(component.id, $event)"
            />
          </div>

          <!-- 组件选择框 -->
          <div
            v-if="isComponentSelected(component.id)"
            class="component-selection"
            @mousedown.stop
          >
            <!-- 调整大小手柄 -->
            <div
              v-for="handle in resizeHandles"
              :key="handle.position"
              class="resize-handle"
              :class="`handle-${handle.position}`"
              @mousedown.stop="startResize($event, component, handle.position)"
            ></div>
          </div>
          <!-- inline textarea for editing -->
          <textarea
            v-if="inlineEditingId === component.id"
            class="inline-textarea"
            v-model="inlineContent"
            @input="adjustInlineSize"
            @blur="() => onInlineBlur(component.id)"
            @keydown.enter="(e) => onInlineKeydown(e, component.id)"
            :style="getInlineTextareaStyle(component)"
          />
        </div>
      </div>

      <!-- 拖拽预览 -->
      <div
        v-if="dragPreview.visible"
        class="drag-preview"
        :style="dragPreview.style"
      >
        <div class="preview-icon">{{ dragPreview.icon }}</div>
        <div class="preview-name">{{ dragPreview.name }}</div>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="canvas-toolbar" ref="toolbarRef" :style="{ left: toolbarPos.x + 'px', top: toolbarPos.y + 'px' }">
      <div class="toolbar-drag-handle" title="拖动工具栏" @mousedown.stop.prevent="startToolbarDrag($event)">≡</div>
      <button
        class="toolbar-btn"
        :class="{ active: tool === 'select' }"
        @click="setTool('select')"
        title="选择工具"
      >
        ✋
      </button>
      <button
        class="toolbar-btn"
        :class="{ active: tool === 'pan' }"
        @click="setTool('pan')"
        title="平移工具"
      >
        👆
      </button>
      <span class="toolbar-separator"></span>
      <button
        class="toolbar-btn"
        @click="zoomIn"
        title="放大"
      >
        🔍+
      </button>
      <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
      <button
        class="toolbar-btn"
        @click="zoomOut"
        title="缩小"
      >
        🔍-
      </button>
      <button
        class="toolbar-btn"
        @click="fitToScreen"
        title="适应屏幕"
      >
        📐
      </button>
      <button class="toolbar-btn" @click="undo" title="撤销 (Ctrl+Z)">⎌</button>
      <button class="toolbar-btn" @click="redo" title="重做 (Ctrl+Y)">↻</button>
      <!-- 字体编辑控件 -->
      <div class="toolbar-separator"></div>
      <select class="toolbar-select" v-model="selectedStyle.fontFamily" @change="applyStylePatch({ fontFamily: selectedStyle.fontFamily })" title="字体">
        <option value="">默认</option>
        <!-- 常用中文字体（优先） -->
        <option value="Microsoft YaHei">Microsoft YaHei (微软雅黑)</option>
        <option value="Microsoft JhengHei">Microsoft JhengHei (微軟正黑體)</option>
        <option value="SimSun">SimSun (宋体)</option>
        <option value="SimHei">SimHei (黑体)</option>
        <option value="PingFang SC">PingFang SC (苹方)</option>
        <option value="Noto Sans SC">Noto Sans SC</option>
        <option value="Source Han Sans CN">Source Han Sans CN</option>
        <option value="STKaiti">STKaiti (华文楷体)</option>
        <option value="STSong">STSong (华文宋体)</option>
        <!-- 兼顾英文常用字体 -->
        <option value="Arial">Arial</option>
        <option value="Helvetica">Helvetica</option>
        <option value="Times New Roman">Times New Roman</option>
      </select>
      <div class="toolbar-btn" style="display:flex;gap:4px;align-items:center">
        <button class="toolbar-btn" @click="changeFontSize(-2)" title="减小字体">A-</button>
        <span style="min-width:28px;text-align:center">{{ selectedStyle.fontSize || defaultFontSize }}</span>
        <button class="toolbar-btn" @click="changeFontSize(2)" title="增大字体">A+</button>
      </div>
      <button class="toolbar-btn" @click="convertSelectedToTitle" title="设为标题 (H)">H</button>
      <button class="toolbar-btn" :class="{ active: selectedStyle.fontWeight && String(selectedStyle.fontWeight).includes('bold') }" @click="toggleBold" title="加粗">B</button>
      <button class="toolbar-btn" :class="{ active: selectedStyle.fontStyle === 'italic' }" @click="toggleItalic" title="斜体">I</button>
      <button class="toolbar-btn" :class="{ active: selectedStyle.textAlign === 'left' }" @click="setTextAlign('left')" title="左对齐">L</button>
      <button class="toolbar-btn" :class="{ active: selectedStyle.textAlign === 'center' }" @click="setTextAlign('center')" title="居中">C</button>
      <button class="toolbar-btn" :class="{ active: selectedStyle.textAlign === 'right' }" @click="setTextAlign('right')" title="右对齐">R</button>
      <input type="color" v-model="selectedStyle.color" @input="applyStylePatch({ color: selectedStyle.color })" title="字体颜色" style="width:36px;height:28px;padding:0;border:none;background:none"/>
      <input type="color" v-model="selectedStyle.backgroundColor" @input="applyStylePatch({ backgroundColor: selectedStyle.backgroundColor })" title="文本框背景" style="width:36px;height:28px;padding:0;border:none;background:none"/>
      <button class="toolbar-btn" :class="{ active: selectedStyle.textShadow }" @click="toggleTextShadow" title="字体阴影">S</button>
    </div>

    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      @click.stop
    >
      <div class="context-menu-item" @click="copyComponent">
        📋 复制
      </div>
      <div class="context-menu-item" @click="pasteComponent">
        📄 粘贴
      </div>
      <div class="context-menu-item danger" @click="deleteComponent">
        🗑️ 删除
      </div>
    </div>

    <!-- 快捷键提示 -->
    <div v-if="showShortcuts" class="shortcuts-panel">
      <h4>快捷键</h4>
      <div class="shortcut-item">
        <kbd>Ctrl+C</kbd> 复制组件
      </div>
      <div class="shortcut-item">
        <kbd>Ctrl+V</kbd> 粘贴组件
      </div>
      <div class="shortcut-item">
        <kbd>Delete</kbd> 删除组件
      </div>
      <div class="shortcut-item">
        <kbd>Ctrl+Z</kbd> 撤销
      </div>
      <div class="shortcut-item">
        <kbd>Ctrl+Y</kbd> 重做
      </div>
      <div class="shortcut-item">
        <kbd>Ctrl+A</kbd> 全选
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { nextTick } from 'vue'
import StepComponentRenderer from '../canvas/StepComponentRenderer.vue'
import html2canvas from 'html2canvas'
import type { StepComponent } from '../../types/coursePlayer'

// 组件属性
interface Props {
  components: StepComponent[]
  canvasConfig?: {
    width: number
    height: number
    backgroundColor?: string
  }
  selectedComponentId?: string | null
}

interface Emits {
  (e: 'update:components', components: StepComponent[]): void
  (e: 'update:canvas-config', config: any): void
  (e: 'component-drop', componentType: string, position: { x: number; y: number }): void
  (e: 'component-select', componentId: string | null): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Undo / Redo history
const undoStack = ref<any[]>([])
const redoStack = ref<any[]>([])
const isPerformingUndoRedo = ref(false)
const historyLimit = 50

watch(() => props.components, (_newV, oldV) => {
  if (isPerformingUndoRedo.value) return
  if (!oldV) return
  try {
    undoStack.value.push(JSON.parse(JSON.stringify(oldV)))
    if (undoStack.value.length > historyLimit) undoStack.value.shift()
    redoStack.value = []
  } catch (e) {
    // ignore cloning errors
  }
}, { deep: true })

function undo() {
  if (undoStack.value.length === 0) return
  const prev = undoStack.value.pop()!
  redoStack.value.push(JSON.parse(JSON.stringify(props.components)))
  isPerformingUndoRedo.value = true
  emit('update:components', JSON.parse(JSON.stringify(prev)))
  setTimeout(() => { isPerformingUndoRedo.value = false }, 0)
}

function redo() {
  if (redoStack.value.length === 0) return
  const next = redoStack.value.pop()!
  undoStack.value.push(JSON.parse(JSON.stringify(props.components)))
  isPerformingUndoRedo.value = true
  emit('update:components', JSON.parse(JSON.stringify(next)))
  setTimeout(() => { isPerformingUndoRedo.value = false }, 0)
}

// 响应式数据
const editorRef = ref<HTMLElement | null>(null)
const tool = ref<'select' | 'pan'>('select')
const zoom = ref(1)
const panOffset = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
// toolbar and canvas dragging (page-level reposition)
const toolbarRef = ref<HTMLElement | null>(null)
const toolbarPos = ref({ x: 16, y: 16 })
let toolbarDragging = false
const canvasContainerRef = ref<HTMLElement | null>(null)
const canvasPagePos = ref({ x: 0, y: 0 })
let canvasDragging = false
const startToolbarDrag = (e: MouseEvent) => {
  if ((e.target as HTMLElement).closest('.toolbar-btn')) return
  e.preventDefault()
  toolbarDragging = true
  document.addEventListener('mousemove', toolbarDragMove)
  document.addEventListener('mouseup', toolbarDragEnd)
  dragStart.value = { x: e.clientX - toolbarPos.value.x, y: e.clientY - toolbarPos.value.y }
}
const toolbarDragMove = (e: MouseEvent) => {
  if (!toolbarDragging) return
  toolbarPos.value.x = e.clientX - dragStart.value.x
  toolbarPos.value.y = e.clientY - dragStart.value.y
}
const toolbarDragEnd = () => {
  toolbarDragging = false
  document.removeEventListener('mousemove', toolbarDragMove)
  document.removeEventListener('mouseup', toolbarDragEnd)
}
const startCanvasDrag = (e: MouseEvent) => {
  // only start when clicking the drag handle
  e.preventDefault()
  canvasDragging = true
  document.addEventListener('mousemove', canvasDragMove)
  document.addEventListener('mouseup', canvasDragEnd)
  dragStart.value = { x: e.clientX - canvasPagePos.value.x, y: e.clientY - canvasPagePos.value.y }
}
const canvasDragMove = (e: MouseEvent) => {
  if (!canvasDragging) return
  canvasPagePos.value.x = e.clientX - dragStart.value.x
  canvasPagePos.value.y = e.clientY - dragStart.value.y
}
const canvasDragEnd = () => {
  canvasDragging = false
  document.removeEventListener('mousemove', canvasDragMove)
  document.removeEventListener('mouseup', canvasDragEnd)
}
const selectedComponents = ref<Set<string>>(new Set())
const dragPreview = ref({
  visible: false,
  style: '',
  icon: '',
  name: ''
})
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  targetComponent: null as StepComponent | null
})
const showShortcuts = ref(false)
const clipboard = ref<StepComponent | null>(null)

// 调整大小相关
const isResizing = ref(false)
const resizeStart = ref({ x: 0, y: 0 })
const resizeComponent = ref<StepComponent | null>(null)
const resizeHandle = ref('')

// 调整大小手柄位置
const resizeHandles = [
  { position: 'nw', cursor: 'nw-resize' },
  { position: 'n', cursor: 'n-resize' },
  { position: 'ne', cursor: 'ne-resize' },
  { position: 'e', cursor: 'e-resize' },
  { position: 'se', cursor: 'se-resize' },
  { position: 's', cursor: 's-resize' },
  { position: 'sw', cursor: 'sw-resize' },
  { position: 'w', cursor: 'w-resize' }
]

// 计算属性
const canvasStyle = computed(() => ({
  transform: `translate(${panOffset.value.x}px, ${panOffset.value.y}px) scale(${zoom.value})`,
  width: (props.canvasConfig?.width || 1920) + 'px',
  height: (props.canvasConfig?.height || 1080) + 'px'
}))

const contentStyle = computed(() => ({
  backgroundColor: props.canvasConfig?.backgroundColor || '#ffffff'
}))

const gridStyle = computed(() => ({
  backgroundImage: `radial-gradient(circle, #e5e7eb 1px, transparent 1px)`,
  backgroundSize: `${20 * zoom.value}px ${20 * zoom.value}px`
}))

const isComponentSelected = (componentId: string) => {
  return selectedComponents.value.has(componentId)
}

// 工具方法
const setTool = (newTool: 'select' | 'pan') => {
  tool.value = newTool
  if (newTool === 'pan') {
    selectedComponents.value.clear()
    emit('component-select', null)
  }
}

const getComponentStyle = (component: StepComponent) => {
  const position = component.position || { x: 0, y: 0, width: 300, height: 200 }
  return {
    left: position.x + 'px',
    top: position.y + 'px',
    width: position.width + 'px',
    height: position.height + 'px',
    transform: component.position?.rotation ? `rotate(${component.position.rotation}deg)` : undefined
  }
}

const zoomIn = () => {
  zoom.value = Math.min(zoom.value * 1.2, 3)
}

const zoomOut = () => {
  zoom.value = Math.max(zoom.value * 0.8, 0.1)
}

const fitToScreen = () => {
  if (!editorRef.value) return
  const container = editorRef.value.querySelector('.canvas-container') as HTMLElement
  if (!container) return

  const containerRect = container.getBoundingClientRect()
  const canvasWidth = props.canvasConfig?.width || 1920
  const canvasHeight = props.canvasConfig?.height || 1080

  const scaleX = containerRect.width / canvasWidth
  const scaleY = containerRect.height / canvasHeight
  zoom.value = Math.min(scaleX, scaleY, 1)

  panOffset.value = {
    x: (containerRect.width - canvasWidth * zoom.value) / 2,
    y: (containerRect.height - canvasHeight * zoom.value) / 2
  }
}

// 事件处理
const handleCanvasMouseDown = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  const clickedOnComponent = !!target.closest('.canvas-component')

  // If left-clicked on empty canvas area, start panning regardless of active tool.
  if (event.button === 0 && !clickedOnComponent) {
    // clear selection when clicking empty area
    selectedComponents.value.clear()
    emit('component-select', null)
    hideContextMenu()
    isDragging.value = true
    dragStart.value = { x: event.clientX - panOffset.value.x, y: event.clientY - panOffset.value.y }
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    return
  }

  // If pan tool is explicitly active and user clicked something that allows pan, start panning.
  if (tool.value === 'pan') {
    isDragging.value = true
    dragStart.value = { x: event.clientX - panOffset.value.x, y: event.clientY - panOffset.value.y }
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    return
  }

  // Default select behavior when clicking blank area (handled above) or other places do nothing here.
  if (tool.value === 'select') {
    // clicking on canvas container (not a component) already handled above.
    // if we reach here and tool is select, do nothing (component clicks are handled in handleComponentMouseDown)
    hideContextMenu()
  }
}

const handleMouseMove = (event: MouseEvent) => {
  if (isDragging.value) {
    panOffset.value = {
      x: event.clientX - dragStart.value.x,
      y: event.clientY - dragStart.value.y
    }
  }
}

const handleMouseUp = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}

const handleWheel = (event: WheelEvent) => {
  event.preventDefault()
  const delta = event.deltaY > 0 ? 0.9 : 1.1
  const newZoom = Math.max(0.1, Math.min(3, zoom.value * delta))

  if (newZoom !== zoom.value) {
    // 缩放时保持鼠标位置为中心
    const rect = (event.target as HTMLElement).getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    const scaleChange = newZoom / zoom.value
    panOffset.value.x = x - (x - panOffset.value.x) * scaleChange
    panOffset.value.y = y - (y - panOffset.value.y) * scaleChange

    zoom.value = newZoom
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  dragPreview.value.visible = false

  const componentType = event.dataTransfer?.getData('component-type')
  if (!componentType) return

  // 使用当前处理 drop 事件的容器（currentTarget）来计算相对于画布的坐标，
  // 避免 event.target 指向子元素导致坐标偏移。
  const container = (event.currentTarget as HTMLElement) || (editorRef.value?.querySelector('.canvas-container') as HTMLElement)
  const rect = container.getBoundingClientRect()
  const x = (event.clientX - rect.left) / zoom.value
  const y = (event.clientY - rect.top) / zoom.value

  emit('component-drop', componentType, { x: Math.max(0, x), y: Math.max(0, y) })
}

const handleComponentMouseDown = (event: MouseEvent, component: StepComponent) => {
  if (tool.value !== 'select') return

  const target = event.target as HTMLElement
  // If we're inline-editing this component and click inside the textarea, allow normal text selection
  if (inlineEditingId.value === component.id && target.closest('.inline-textarea')) {
    return
  }
  event.stopPropagation()

  // 右键菜单
  if (event.button === 2) {
    showContextMenu(event, component)
    return
  }

  // 多选逻辑
  if (event.ctrlKey || event.metaKey) {
    if (selectedComponents.value.has(component.id)) {
      selectedComponents.value.delete(component.id)
    } else {
      selectedComponents.value.add(component.id)
    }
  } else {
    selectedComponents.value.clear()
    selectedComponents.value.add(component.id)
  }

  emit('component-select', component.id)
  // 启动组件拖拽（左键按下）
  if (event.button === 0) {
    startComponentDrag(event, component)
  }
}

// --- 组件拖拽支持（基于画布容器坐标 + zoom） ---
const componentDraggingId = ref<string | null>(null)
const componentDragOffset = ref({ x: 0, y: 0 })
const componentPendingDragId = ref<string | null>(null)
const componentPendingScreenStart = ref<{ x: number; y: number } | null>(null)
const dragStartThreshold = 6

const startComponentDrag = (event: MouseEvent, component: StepComponent) => {
  if (event.button !== 0) return
  const container = editorRef.value?.querySelector('.canvas-container') as HTMLElement | null
  if (!container || !component.position) return
  // enter pending drag state, wait for movement threshold to start actual drag
  componentPendingDragId.value = component.id
  componentPendingScreenStart.value = { x: event.clientX, y: event.clientY }
  // compute offset now
  const rect = container.getBoundingClientRect()
  const mouseLogicalX = (event.clientX - rect.left) / zoom.value
  const mouseLogicalY = (event.clientY - rect.top) / zoom.value
  componentDragOffset.value = {
    x: mouseLogicalX - component.position.x,
    y: mouseLogicalY - component.position.y,
  }
  const pendingMoveHandler = (ev: MouseEvent) => {
    if (!componentPendingScreenStart.value) return
    const dx = Math.abs(ev.clientX - componentPendingScreenStart.value.x)
    const dy = Math.abs(ev.clientY - componentPendingScreenStart.value.y)
    if (dx > dragStartThreshold || dy > dragStartThreshold) {
      // start actual drag
      componentDraggingId.value = componentPendingDragId.value
      componentPendingDragId.value = null
      componentPendingScreenStart.value = null
      document.removeEventListener('mousemove', pendingMoveHandler)
      // attach real drag listeners
      document.addEventListener('mousemove', componentDragMove)
      document.addEventListener('mouseup', componentDragEnd)
    }
  }
  const pendingUpHandler = () => {
    // cancelled click without moving
    componentPendingDragId.value = null
    componentPendingScreenStart.value = null
    document.removeEventListener('mousemove', pendingMoveHandler)
    document.removeEventListener('mouseup', pendingUpHandler)
  }
  document.addEventListener('mousemove', pendingMoveHandler)
  document.addEventListener('mouseup', pendingUpHandler)
}

const componentDragMove = (event: MouseEvent) => {
  if (!componentDraggingId.value) return
  const container = editorRef.value?.querySelector('.canvas-container') as HTMLElement | null
  if (!container) return
  const rect = container.getBoundingClientRect()
  const mouseLogicalX = (event.clientX - rect.left) / zoom.value
  const mouseLogicalY = (event.clientY - rect.top) / zoom.value
  const newX = Math.max(0, mouseLogicalX - componentDragOffset.value.x)
  const newY = Math.max(0, mouseLogicalY - componentDragOffset.value.y)
  // update component position immutably
  const components = props.components.map((c) => {
    if (c.id !== componentDraggingId.value) return c
    return {
      ...c,
      position: {
        ...(c.position || { x: 0, y: 0, width: 300, height: 200 }),
        x: newX,
        y: newY,
      },
    }
  })
  emit('update:components', components as StepComponent[])
}

const componentDragEnd = () => {
  componentDraggingId.value = null
  document.removeEventListener('mousemove', componentDragMove)
  document.removeEventListener('mouseup', componentDragEnd)
}

const inlineEditingId = ref<string | null>(null)
const inlineContent = ref<string>('')

function saveInlineEdit(componentId: string) {
  const comps = props.components.map(c => {
    if (c.id !== componentId) return c
    return {
      ...c,
      config: {
        ...(c.config || {}),
        content: inlineContent.value
      }
    }
  })
  emit('update:components', comps)
}

function getInlineTextareaStyle(component: StepComponent) {
  const style: Record<string, string> = {
    position: 'absolute',
    left: '0px',
    top: '0px',
    width: '100%',
    height: '100%',
    zIndex: '999',
    resize: 'none',
    border: 'none',
    outline: 'none',
    background: component.style?.backgroundColor || '#ffffff',
    padding: '12px',
    boxSizing: 'border-box',
    overflow: 'auto',
    fontFamily: component.style?.fontFamily || 'inherit',
    fontSize: component.style?.fontSize ? `${component.style.fontSize}px` : `${defaultFontSize}px`,
    fontWeight: component.style?.fontWeight ? String(component.style.fontWeight) : 'normal',
    fontStyle: component.style?.fontStyle || 'normal',
    lineHeight: (component.style as any)?.lineHeight ? String((component.style as any).lineHeight) : '1.2',
    color: component.style?.color || '#000000',
    textAlign: component.style?.textAlign || 'left',
  }
  if ((component.style as any)?.textShadow) style.textShadow = (component.style as any).textShadow
  return style
}

function adjustInlineSize(event: Event) {
  const ta = event.target as HTMLTextAreaElement
  if (!ta) return
  ta.style.height = 'auto'
  ta.style.height = Math.max(32, ta.scrollHeight) + 'px'
}

function onInlineKeydown(e: KeyboardEvent, componentId: string) {
  // Ctrl+Enter or Cmd+Enter saves and exits; plain Enter inserts newline
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault()
    saveInlineEdit(componentId)
    inlineEditingId.value = null
    return
  }
  // allow default behavior for Enter (newline)
}

function onInlineBlur(componentId: string) {
  saveInlineEdit(componentId)
  inlineEditingId.value = null
}

// ----------------- 字体样式编辑 -----------------
const defaultFontSize = 24
const selectedStyle = ref<any>({})

const selectedComponent = computed(() => {
  const id = Array.from(selectedComponents.value)[0] || null
  return props.components.find(c => c.id === id) || null
})

watch(selectedComponent, (comp) => {
  if (!comp) {
    selectedStyle.value = {}
    return
  }
  selectedStyle.value = { ...(comp.style || {}) }
}, { immediate: true })

function applyStylePatch(patch: Record<string, any>) {
  const comp = selectedComponent.value
  if (!comp) return
  const components = props.components.map(c => {
    if (c.id !== comp.id) return c
    return { ...c, style: { ...(c.style || {}), ...patch } }
  })
  emit('update:components', components as any)
}

function changeFontSize(delta: number) {
  const current = Number(selectedStyle.value.fontSize || defaultFontSize)
  const next = Math.max(6, current + delta)
  selectedStyle.value.fontSize = next
  applyStylePatch({ fontSize: next })
}

function toggleBold() {
  const cur = selectedStyle.value.fontWeight
  const isBold = String(cur).includes('bold') || Number(cur) >= 600
  const next = isBold ? 400 : 700
  selectedStyle.value.fontWeight = next
  applyStylePatch({ fontWeight: next })
}

function toggleItalic() {
  const cur = selectedStyle.value.fontStyle
  const next = cur === 'italic' ? 'normal' : 'italic'
  selectedStyle.value.fontStyle = next
  applyStylePatch({ fontStyle: next })
}

function setTextAlign(align: 'left' | 'center' | 'right') {
  selectedStyle.value.textAlign = align
  applyStylePatch({ textAlign: align })
}

function toggleTextShadow() {
  if (selectedStyle.value.textShadow) {
    selectedStyle.value.textShadow = ''
    applyStylePatch({ textShadow: '' })
  } else {
    const shadow = '2px 2px 4px rgba(0,0,0,0.25)'
    selectedStyle.value.textShadow = shadow
    applyStylePatch({ textShadow: shadow })
  }
}

function convertSelectedToTitle() {
  if (selectedComponents.value.size === 0) return
  const components = props.components.map(c => {
    if (!selectedComponents.value.has(c.id)) return c
    const nextStyle = {
      ...(c.style || {}),
      fontSize: 48,
      fontWeight: 700
    }
    return {
      ...c,
      type: 'title',
      style: nextStyle
    }
  })
  emit('update:components', components as StepComponent[])
}


const handleComponentDoubleClick = (component: StepComponent) => {
  // 双击编辑组件（这里可以触发属性面板）
  emit('component-select', component.id)
  // start inline editing
  inlineEditingId.value = component.id
  inlineContent.value = component.config?.content || ''
  // focus next tick
  nextTick(() => {
    const selector = `.canvas-component[data-id="${component.id}"] .inline-textarea`
    const ta = document.querySelector(selector) as HTMLTextAreaElement | null
    if (ta) ta.focus()
  })
}

const handleContentSizeChange = (componentId: string, size: { width: number; height: number }) => {
  // 更新组件的自然尺寸
  const components = [...props.components]
  const component = components.find(c => c.id === componentId)
  if (component && component.position) {
    // 如果组件没有设置尺寸，使用内容尺寸
    if (!component.position.width || component.position.width === 300) {
      component.position.width = Math.max(200, size.width + 40) // 添加一些边距
    }
    if (!component.position.height || component.position.height === 200) {
      component.position.height = Math.max(100, size.height + 40)
    }
    emit('update:components', components)
  }
}

// 右键菜单
const showContextMenu = (event: MouseEvent, component: StepComponent) => {
  event.preventDefault()
  contextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    targetComponent: component
  }
}

const hideContextMenu = () => {
  contextMenu.value.visible = false
}

const copyComponent = () => {
  if (contextMenu.value.targetComponent) {
    clipboard.value = JSON.parse(JSON.stringify(contextMenu.value.targetComponent))
  }
  hideContextMenu()
}

const pasteComponent = () => {
  if (clipboard.value) {
    const newComponent = JSON.parse(JSON.stringify(clipboard.value))
    newComponent.id = `comp-${Date.now()}`
    newComponent.position = {
      ...newComponent.position,
      x: (newComponent.position?.x || 0) + 20,
      y: (newComponent.position?.y || 0) + 20
    }

    const components = [...props.components, newComponent]
    emit('update:components', components)
  }
  hideContextMenu()
}

const deleteComponent = () => {
  if (contextMenu.value.targetComponent) {
    const components = props.components.filter(c => c.id !== contextMenu.value.targetComponent!.id)
    emit('update:components', components)
    selectedComponents.value.delete(contextMenu.value.targetComponent!.id)
    emit('component-select', null)
  }
  hideContextMenu()
}

// 调整大小
const startResize = (event: MouseEvent, component: StepComponent, handle: string) => {
  event.stopPropagation()
  isResizing.value = true
  resizeComponent.value = component
  resizeHandle.value = handle

  const container = editorRef.value?.querySelector('.canvas-container') as HTMLElement | null
  const rect = container ? container.getBoundingClientRect() : { left: 0, top: 0 }
  // store initial mouse logical coordinates and initial size/pos
  resizeStart.value = {
    x: (event.clientX - rect.left) / zoom.value,
    y: (event.clientY - rect.top) / zoom.value,
    width: component.position?.width || 300,
    height: component.position?.height || 200,
    posX: component.position?.x || 0,
    posY: component.position?.y || 0,
  } as any

  document.addEventListener('mousemove', handleResizeMove)
  document.addEventListener('mouseup', handleResizeEnd)
}

const handleResizeMove = (event: MouseEvent) => {
  if (!isResizing.value || !resizeComponent.value) return

  const container = editorRef.value?.querySelector('.canvas-container') as HTMLElement | null
  const rect = container ? container.getBoundingClientRect() : { left: 0, top: 0 }
  const mouseLogicalX = (event.clientX - rect.left) / zoom.value
  const mouseLogicalY = (event.clientY - rect.top) / zoom.value
  const deltaX = mouseLogicalX - (resizeStart.value as any).x
  const deltaY = mouseLogicalY - (resizeStart.value as any).y

  const position = resizeComponent.value.position!
  const newPosition = { ...position }
  // use initial sizes from resizeStart to avoid cumulative doubling
  const startWidth = (resizeStart.value as any).width
  const startHeight = (resizeStart.value as any).height
  const startPosX = (resizeStart.value as any).posX
  const startPosY = (resizeStart.value as any).posY

  switch (resizeHandle.value) {
    case 'nw':
      newPosition.x = startPosX + deltaX
      newPosition.y = startPosY + deltaY
      newPosition.width = Math.max(50, startWidth - deltaX)
      newPosition.height = Math.max(30, startHeight - deltaY)
      break
    case 'n':
      newPosition.y = startPosY + deltaY
      newPosition.height = Math.max(30, startHeight - deltaY)
      break
    case 'ne':
      newPosition.y = startPosY + deltaY
      newPosition.width = Math.max(50, startWidth + deltaX)
      newPosition.height = Math.max(30, startHeight - deltaY)
      break
    case 'e':
      newPosition.width = Math.max(50, startWidth + deltaX)
      break
    case 'se':
      newPosition.width = Math.max(50, startWidth + deltaX)
      newPosition.height = Math.max(30, startHeight + deltaY)
      break
    case 's':
      newPosition.height = Math.max(30, startHeight + deltaY)
      break
    case 'sw':
      newPosition.x = startPosX + deltaX
      newPosition.width = Math.max(50, startWidth - deltaX)
      newPosition.height = Math.max(30, startHeight + deltaY)
      break
    case 'w':
      newPosition.x = startPosX + deltaX
      newPosition.width = Math.max(50, startWidth - deltaX)
      break
  }

  resizeComponent.value.position = newPosition
  emit('update:components', [...props.components])
}

const handleResizeEnd = () => {
  isResizing.value = false
  resizeComponent.value = null
  document.removeEventListener('mousemove', handleResizeMove)
  document.removeEventListener('mouseup', handleResizeEnd)
}

// 快捷键
const handleKeyDown = (event: KeyboardEvent) => {
  // If inline editing is active and focus is inside the inline textarea, allow native text shortcuts
  const activeEl = (document.activeElement as HTMLElement | null)
  if (inlineEditingId.value && activeEl && activeEl.closest && activeEl.closest('.inline-textarea')) {
    return
  }

  // Ctrl+A 全选
  if (event.ctrlKey && event.key === 'a') {
    event.preventDefault()
    selectedComponents.value = new Set(props.components.map(c => c.id))
    return
  }

  // Delete 删除
  if (event.key === 'Delete' && selectedComponents.value.size > 0) {
    event.preventDefault()
    const components = props.components.filter(c => !selectedComponents.value.has(c.id))
    selectedComponents.value.clear()
    emit('update:components', components)
    emit('component-select', null)
    return
  }

  // Ctrl+C 复制
  if (event.ctrlKey && event.key === 'c' && selectedComponents.value.size === 1) {
    event.preventDefault()
    const componentId = Array.from(selectedComponents.value)[0]
    const component = props.components.find(c => c.id === componentId)
    if (component) {
      clipboard.value = JSON.parse(JSON.stringify(component))
    }
    return
  }

  // Ctrl+Z 撤销
  if (event.ctrlKey && event.key === 'z') {
    event.preventDefault()
    undo()
    return
  }
  // Ctrl+Y 重做
  if (event.ctrlKey && event.key === 'y') {
    event.preventDefault()
    redo()
    return
  }

  // Ctrl+V 粘贴
  if (event.ctrlKey && event.key === 'v' && clipboard.value) {
    event.preventDefault()
    pasteComponent()
    return
  }

  // 显示快捷键面板
  if (event.key === 'F1') {
    event.preventDefault()
    showShortcuts.value = !showShortcuts.value
  }
}

// 生命周期
onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
  document.addEventListener('click', hideContextMenu)
  fitToScreen()
})
// touch refs so linter doesn't warn about unused template refs
onMounted(() => {
  void toolbarRef.value
  void canvasContainerRef.value
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeyDown)
  document.removeEventListener('click', hideContextMenu)
})

// Export a thumbnail image (data URL) of the current canvas content.
// This is used by the parent editor to show thumbnails in the page navigator.
async function exportThumbnail(): Promise<string> {
  try {
    const container = editorRef.value?.querySelector('.canvas-container') as HTMLElement | null
    if (!container) return ''

    // Prefer the static import (installed dependency) or global-injected fallback.
    let html2canvasFn: any = (window as any).html2canvas || html2canvas || null

    console.debug('[exportThumbnail] html2canvas available:', !!html2canvasFn)
    if (html2canvasFn) {
      const canvasW = props.canvasConfig?.width || 1920
      const canvasH = props.canvasConfig?.height || 1080

      // Attempt 1: temporarily normalize zoom/pan and render the real container.
      const oldZoom = zoom.value
      const oldPan = { ...panOffset.value }
      const oldPagePos = { ...canvasPagePos.value }
      try {
        console.debug('[exportThumbnail] attempt direct render visible container', { canvasW, canvasH })
        zoom.value = 1
        panOffset.value = { x: 0, y: 0 }
        canvasPagePos.value = { x: 0, y: 0 }
        await nextTick()
        // wait fonts
        try { if ((document as any).fonts && (document as any).fonts.ready) await (document as any).fonts.ready } catch (e) {}
        await new Promise((r) => setTimeout(r, 250))

        const rendered: HTMLCanvasElement = await html2canvasFn(container, { backgroundColor: null, scale: 1, width: canvasW, height: canvasH })
        const targetWidth = 160
        const targetHeight = Math.max(1, Math.round(targetWidth * (canvasH / canvasW)))
        const thumbCanvas = document.createElement('canvas')
        thumbCanvas.width = targetWidth
        thumbCanvas.height = targetHeight
        const ctx = thumbCanvas.getContext('2d')
        if (ctx) {
          ctx.fillStyle = '#ffffff'
          ctx.fillRect(0, 0, thumbCanvas.width, thumbCanvas.height)
          ctx.drawImage(rendered, 0, 0, thumbCanvas.width, thumbCanvas.height)
          return thumbCanvas.toDataURL('image/png')
        }
        return rendered.toDataURL('image/png')
      } catch (err) {
        console.error('[exportThumbnail] direct render failed', err)
        // continue to fallback
      } finally {
        // restore view
        zoom.value = oldZoom
        panOffset.value = oldPan
        canvasPagePos.value = oldPagePos
        await nextTick()
      }

      // Fallback: Clone the canvas container into an offscreen node to render without page transforms
      const clone = container.cloneNode(true) as HTMLElement
      clone.style.transform = ''
      clone.style.left = '0'
      clone.style.top = '0'
      clone.style.margin = '0'
      clone.style.width = canvasW + 'px'
      clone.style.height = canvasH + 'px'
      clone.querySelectorAll('[style]').forEach((el: Element) => {
        const e = el as HTMLElement
        if (e.style && e.style.transform) e.style.transform = ''
      })

      const wrapper = document.createElement('div')
      wrapper.style.position = 'fixed'
      wrapper.style.left = '-99999px'
      wrapper.style.top = '-99999px'
      wrapper.style.width = canvasW + 'px'
      wrapper.style.height = canvasH + 'px'
      wrapper.style.overflow = 'hidden'
      wrapper.appendChild(clone)
      document.body.appendChild(wrapper)

      try {
        console.debug('[exportThumbnail] attempt clone render', { canvasW, canvasH })
        try { if ((document as any).fonts && (document as any).fonts.ready) await (document as any).fonts.ready } catch (e) {}
        const rendered: HTMLCanvasElement = await html2canvasFn(clone, { backgroundColor: null, scale: 1, width: canvasW, height: canvasH })
        const targetWidth = 160
        const targetHeight = Math.max(1, Math.round(targetWidth * (canvasH / canvasW)))
        const thumbCanvas = document.createElement('canvas')
        thumbCanvas.width = targetWidth
        thumbCanvas.height = targetHeight
        const ctx = thumbCanvas.getContext('2d')
        if (ctx) {
          ctx.fillStyle = '#ffffff'
          ctx.fillRect(0, 0, thumbCanvas.width, thumbCanvas.height)
          ctx.drawImage(rendered, 0, 0, thumbCanvas.width, thumbCanvas.height)
          return thumbCanvas.toDataURL('image/png')
        }
        return rendered.toDataURL('image/png')
      } finally {
        try { document.body.removeChild(wrapper) } catch (e) { /* ignore */ }
      }
    }
  } catch (e) {
    console.error('[exportThumbnail] unexpected error', e)
    // ignore and fallback to placeholder generation below
  }

  // fallback: create a simple placeholder thumbnail
  try {
    const c = document.createElement('canvas')
    c.width = 160
    c.height = 90
    const ctx = c.getContext('2d')
    if (ctx) {
      ctx.fillStyle = '#f3f4f6'
      ctx.fillRect(0, 0, c.width, c.height)
      ctx.fillStyle = '#9ca3af'
      ctx.font = '12px sans-serif'
      ctx.fillText('预览', 8, 20)
    }
    return c.toDataURL('image/png')
  } catch (e) {
    return ''
  }
}

// expose to parent via ref (thumbnail + fitToScreen)
defineExpose({ exportThumbnail, fitToScreen })

// 监听外部选择变化
watch(() => props.selectedComponentId, (newId) => {
  selectedComponents.value.clear()
  if (newId) {
    selectedComponents.value.add(newId)
  }
})
</script>

<style scoped>
.canvas-editor {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #f3f4f6;
}

.canvas-container {
  position: relative;
  transform-origin: 0 0;
  cursor: default;
  user-select: none;
}

.canvas-grid {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0.3;
}

.canvas-content {
  position: relative;
  min-height: 100%;
}

.canvas-drag-handle {
  position: absolute;
  width: 18px;
  height: 18px;
  left: 6px;
  top: 6px;
  background: rgba(0,0,0,0.06);
  border-radius: 3px;
  cursor: move;
  z-index: 120;
}

.canvas-component {
  position: absolute;
  border: 2px solid transparent;
  border-radius: 6px;
  transition: border-color 0.15s ease;
  cursor: move;
}

.canvas-component:hover {
  border-color: #3b82f6;
}

.canvas-component.selected {
  border-color: #3b82f6;
  box-shadow: 0 0 0 1px #3b82f6, 0 4px 12px rgba(59, 130, 246, 0.3);
}

.component-content {
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 4px;
}

.component-selection {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  pointer-events: none;
}

.resize-handle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border: 1px solid white;
  border-radius: 50%;
  pointer-events: auto;
  cursor: pointer;
}

.handle-nw { top: -4px; left: -4px; cursor: nw-resize; }
.handle-n { top: -4px; left: 50%; transform: translateX(-50%); cursor: n-resize; }
.handle-ne { top: -4px; right: -4px; cursor: ne-resize; }
.handle-e { top: 50%; right: -4px; transform: translateY(-50%); cursor: e-resize; }
.handle-se { bottom: -4px; right: -4px; cursor: se-resize; }
.handle-s { bottom: -4px; left: 50%; transform: translateX(-50%); cursor: s-resize; }
.handle-sw { bottom: -4px; left: -4px; cursor: sw-resize; }
.handle-w { top: 50%; left: -4px; transform: translateY(-50%); cursor: w-resize; }

.drag-preview {
  position: absolute;
  pointer-events: none;
  background: rgba(59, 130, 246, 0.9);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 1000;
}

.preview-icon {
  font-size: 16px;
  margin-bottom: 4px;
}

.canvas-toolbar {
  position: absolute;
  top: 16px;
  left: 16px;
  background: white;
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 4px;
  z-index: 100;
}

.canvas-toolbar .toolbar-drag-handle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  margin-right: 6px;
  border-radius: 4px;
  cursor: move;
  user-select: none;
  font-weight: 700;
}

.toolbar-btn {
  padding: 6px 8px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.15s ease;
}

.toolbar-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.toolbar-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.toolbar-separator {
  width: 1px;
  height: 20px;
  background: #e5e7eb;
  margin: 0 4px;
}

.zoom-level {
  font-size: 12px;
  color: #6b7280;
  min-width: 40px;
  text-align: center;
}

.context-menu {
  position: fixed;
  background: white;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid #e5e7eb;
  z-index: 1000;
  min-width: 120px;
}

.context-menu-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.15s ease;
}

.context-menu-item:hover {
  background: #f3f4f6;
}

.context-menu-item.danger {
  color: #dc2626;
}

.context-menu-item.danger:hover {
  background: #fef2f2;
}

.shortcuts-panel {
  position: absolute;
  top: 16px;
  right: 16px;
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid #e5e7eb;
  z-index: 100;
  max-width: 250px;
}

.shortcuts-panel h4 {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
}

.shortcut-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
}

.shortcut-item:last-child {
  margin-bottom: 0;
}

.shortcut-item kbd {
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 3px;
  padding: 2px 6px;
  font-size: 11px;
  font-family: monospace;
  color: #374151;
}

.inline-textarea {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  border: none;
  outline: none;
  resize: none;
  white-space: pre-wrap;
  word-break: break-word;
  overflow: auto;
  font-family: inherit;
}
</style>

