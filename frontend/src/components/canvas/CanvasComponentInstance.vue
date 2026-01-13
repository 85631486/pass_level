<template>
  <div
    class="component-instance"
    :class="{ selected: selected }"
    :style="componentStyle"
    @mousedown.stop="handleMouseDown"
    @dblclick.stop="handleDoubleClick"
  >
    <!-- 组件内容 -->
    <div class="component-content" :style="contentStyle">
      <div class="component-content-inner">
        <StepComponentRenderer :component="component" :embedded="true" @content-size="handleContentSize" />
        <!-- 内联编辑 textarea -->
        <textarea
          v-if="inlineEditing"
          class="inline-textarea"
          v-model="inlineContent"
          @blur="() => { saveInlineEdit(); inlineEditing = false }"
          @keydown.enter.prevent="saveInlineEdit()"
          ref="inlineTextareaRef"
        />
      </div>
    </div>

    <!-- 选择框 -->
    <div v-if="selected" class="selection-box">
      <!-- 调整手柄 -->
      <div
        v-for="handle in resizeHandles"
        :key="handle.position"
        class="resize-handle"
        :class="`handle-${handle.position}`"
        :style="handle.style"
        @mousedown.stop="handleResizeStart($event, handle.position)"
      />
    </div>

    <!-- 删除按钮 -->
    <button
      v-if="selected"
      class="delete-button"
      @click.stop="handleDelete"
    >
      ×
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { StepComponent, ComponentPosition } from '../../types/coursePlayer'
import StepComponentRenderer from './StepComponentRenderer.vue'

interface Props {
  component: StepComponent
  selected: boolean
  zoom?: number
  snapToGrid?: boolean
  gridSize?: number
}

interface Emits {
  (e: 'select'): void
  (e: 'update:position', position: ComponentPosition): void
  (e: 'update:size', width: number, height: number): void
  (e: 'delete'): void
  (e: 'update:component', partial: any): void
}

const props = withDefaults(defineProps<Props>(), {
  zoom: 1,
  snapToGrid: false,
  gridSize: 20,
})

const emit = defineEmits<Emits>()

// 默认位置和尺寸
const defaultPosition: ComponentPosition = {
  x: 100,
  y: 100,
  width: 300,
  height: 200,
}

const position = computed(() => props.component.position || defaultPosition)

// 组件样式
const componentStyle = computed(() => {
  const pos = position.value
  return {
    position: 'absolute' as const,
    left: `${pos.x}px`,
    top: `${pos.y}px`,
    width: `${pos.width}px`,
    height: `${pos.height}px`,
    zIndex: props.component.style?.zIndex || 1,
  }
})

// 内容样式（应用组件的 style）
const contentStyle = computed(() => {
  const style = props.component.style || {}
  return {
    fontFamily: style.fontFamily || 'inherit',
    fontSize: style.fontSize ? `${style.fontSize}px` : 'inherit',
    fontWeight: style.fontWeight || 'normal',
    fontStyle: style.fontStyle || 'normal',
    color: style.color || 'inherit',
    textAlign: style.textAlign || 'left',
    backgroundColor: style.backgroundColor || 'transparent',
    backgroundImage: style.backgroundImage ? `url(${style.backgroundImage})` : 'none',
    borderWidth: style.borderWidth ? `${style.borderWidth}px` : '0',
    borderStyle: style.borderStyle || 'none',
    borderColor: style.borderColor || 'transparent',
    borderRadius: style.borderRadius ? `${style.borderRadius}px` : '0',
    boxShadow: style.boxShadow || 'none',
    padding: style.padding || '0',
    margin: style.margin || '0',
    opacity: style.opacity !== undefined ? style.opacity : 1,
    transform: style.transform || 'none',
    width: '100%',
    height: '100%',
    overflow: 'auto',
  }
})

// 调整手柄
const resizeHandles = computed(() => {
  const handleSize = 8
  const halfHandle = handleSize / 2
  
  return [
    { position: 'nw', style: { top: `-${halfHandle}px`, left: `-${halfHandle}px` } },
    { position: 'n', style: { top: `-${halfHandle}px`, left: `calc(50% - ${halfHandle}px)` } },
    { position: 'ne', style: { top: `-${halfHandle}px`, right: `-${halfHandle}px` } },
    { position: 'e', style: { top: `calc(50% - ${halfHandle}px)`, right: `-${halfHandle}px` } },
    { position: 'se', style: { bottom: `-${halfHandle}px`, right: `-${halfHandle}px` } },
    { position: 's', style: { bottom: `-${halfHandle}px`, left: `calc(50% - ${halfHandle}px)` } },
    { position: 'sw', style: { bottom: `-${halfHandle}px`, left: `-${halfHandle}px` } },
    { position: 'w', style: { top: `calc(50% - ${halfHandle}px)`, left: `-${halfHandle}px` } },
  ]
})

// 拖拽状态
const isDragging = ref(false)
const isResizing = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const resizeStart = ref({ x: 0, y: 0, width: 0, height: 0, handle: '' })
// 在 mousedown 后进入 pending 状态，只有移动超过阈值才真正认为是拖拽（降低误触）
const pendingDrag = ref(false)
const dragThreshold = 6
// 内联编辑状态
const inlineEditing = ref(false)
const inlineContent = ref(props.component.config?.content || '')


// rAF 批量更新拖拽位置
const pendingPosition = ref<{ x: number; y: number } | null>(null)
const rafId = ref<number | null>(null)

function scheduleFlushPosition() {
  if (rafId.value != null) return
  rafId.value = window.requestAnimationFrame(() => {
    rafId.value = null
    if (!pendingPosition.value) return
    emit('update:position', {
      ...position.value,
      x: Math.max(0, pendingPosition.value.x),
      y: Math.max(0, pendingPosition.value.y),
    } as ComponentPosition)
    pendingPosition.value = null
  })
}

// 处理鼠标按下
function handleMouseDown(event: MouseEvent) {
  // 检查是否点击在调整手柄上
  const target = event.target as HTMLElement
  if (target.classList.contains('resize-handle') || target.closest('.resize-handle')) {
    return // 调整大小由 handleResizeStart 处理
  }
  
  // 检查是否点击在删除按钮上
  if (target.classList.contains('delete-button') || target.closest('.delete-button')) {
    return // 删除由 handleDelete 处理
  }
  
  // 如果点击的是交互控件（输入、按钮、链接等），不要触发拖拽
  const interactiveTags = ['INPUT', 'TEXTAREA', 'BUTTON', 'A', 'SELECT', 'LABEL']
  if (interactiveTags.includes((target.tagName || '').toUpperCase()) || target.closest('[data-no-drag]')) {
    // 仍然选中该组件但不进入拖拽
    emit('select')
    return
  }
  
  // 如果未选中，先选中
  if (!props.selected) {
    emit('select')
    // 标记 pending 状态，等待用户移动超过阈值再真正开始拖拽
    pendingDrag.value = true
    // 计算相对于画布（canvas-container）的逻辑坐标（考虑缩放）
    const container = (event.currentTarget as HTMLElement).closest('.canvas-container') as HTMLElement | null
    let containerRectLeft = 0
    let containerRectTop = 0
    if (container) {
      const r = container.getBoundingClientRect()
      containerRectLeft = r.left
      containerRectTop = r.top
    }
    // 将鼠标位置转换为画布逻辑坐标，然后记录相对于组件位置的偏移
    dragStart.value = {
      x: (event.clientX - containerRectLeft) / props.zoom - position.value.x,
      y: (event.clientY - containerRectTop) / props.zoom - position.value.y,
    }
    event.stopPropagation()
    return
  }
  
  // 已选中时也进入 pending 状态以减少误触
  pendingDrag.value = true
  const container = (event.currentTarget as HTMLElement).closest('.canvas-container') as HTMLElement | null
  let containerRectLeft = 0
  let containerRectTop = 0
  if (container) {
    const r = container.getBoundingClientRect()
    containerRectLeft = r.left
    containerRectTop = r.top
  }
  dragStart.value = {
    x: (event.clientX - containerRectLeft) / props.zoom - position.value.x,
    y: (event.clientY - containerRectTop) / props.zoom - position.value.y,
  }
  event.preventDefault()
  event.stopPropagation()
}

// 处理调整大小开始
function handleResizeStart(event: MouseEvent, handlePosition: string) {
  isResizing.value = true
  const pos = position.value
  resizeStart.value = {
    x: event.clientX,
    y: event.clientY,
    width: pos.width,
    height: pos.height,
    handle: handlePosition,
  }
  event.preventDefault()
  event.stopPropagation()
}

// 处理删除
function handleDelete() {
  if (confirm('确定要删除这个组件吗？')) {
    emit('delete')
  }
}

// 处理双击
function handleDoubleClick() {
  // 双击进入内联编辑（仅对文本组件）
  if (props.component.type === 'text') {
    inlineEditing.value = true
    inlineContent.value = props.component.config?.content || ''
    // 阻止冒泡以免触发画布其他逻辑
  }
}

// 鼠标移动处理
function handleMouseMove(event: MouseEvent) {
  if (pendingDrag.value && !isDragging.value) {
    // 计算位移判断是否超过阈值（将拖拽偏移比较转换到屏幕像素）
    const container = document.querySelector('.canvas-container') as HTMLElement | null
    let containerLeft = 0
    let containerTop = 0
    if (container) {
      const r = container.getBoundingClientRect()
      containerLeft = r.left
      containerTop = r.top
    }
    const currentMouseX = (dragStart.value.x + position.value.x) * props.zoom + containerLeft
    const currentMouseY = (dragStart.value.y + position.value.y) * props.zoom + containerTop
    const dx = Math.abs(event.clientX - currentMouseX)
    const dy = Math.abs(event.clientY - currentMouseY)
    if (dx > dragThreshold || dy > dragThreshold) {
      isDragging.value = true
      pendingDrag.value = false
      console.debug('[CanvasComponentInstance] drag started', props.component.id)
    }
  }
  
  if (isDragging.value) {
    // 将鼠标坐标转换为画布逻辑坐标，再减去起始偏移得到组件左上角位置
    const container = document.querySelector('.canvas-container') as HTMLElement | null
    let containerLeft = 0
    let containerTop = 0
    if (container) {
      const r = container.getBoundingClientRect()
      containerLeft = r.left
      containerTop = r.top
    }
    const mouseLogicalX = (event.clientX - containerLeft) / props.zoom
    const mouseLogicalY = (event.clientY - containerTop) / props.zoom
    const newX = mouseLogicalX - dragStart.value.x
    const newY = mouseLogicalY - dragStart.value.y
    
    let finalX = newX
    let finalY = newY
    
    // 网格对齐
    if (props.snapToGrid) {
      finalX = Math.round(newX / props.gridSize) * props.gridSize
      finalY = Math.round(newY / props.gridSize) * props.gridSize
    }
    
    // 边界检查
    finalX = Math.max(0, finalX)
    finalY = Math.max(0, finalY)
    
    // 使用 rAF 批量更新以提高拖拽跟随性能
    pendingPosition.value = { x: finalX, y: finalY }
    scheduleFlushPosition()
  } else if (isResizing.value) {
    const deltaX = (event.clientX - resizeStart.value.x) / props.zoom
    const deltaY = (event.clientY - resizeStart.value.y) / props.zoom
    
    let newWidth = resizeStart.value.width
    let newHeight = resizeStart.value.height
    let newX = position.value.x
    let newY = position.value.y
    
    const handle = resizeStart.value.handle
    
    // 根据手柄位置调整大小和位置
    if (handle.includes('e')) {
      newWidth = Math.max(50, resizeStart.value.width + deltaX)
    }
    if (handle.includes('w')) {
      newWidth = Math.max(50, resizeStart.value.width - deltaX)
      newX = position.value.x + deltaX
    }
    if (handle.includes('s')) {
      newHeight = Math.max(50, resizeStart.value.height + deltaY)
    }
    if (handle.includes('n')) {
      newHeight = Math.max(50, resizeStart.value.height - deltaY)
      newY = position.value.y + deltaY
    }
    
    // 网格对齐
    if (props.snapToGrid) {
      newWidth = Math.round(newWidth / props.gridSize) * props.gridSize
      newHeight = Math.round(newHeight / props.gridSize) * props.gridSize
      newX = Math.round(newX / props.gridSize) * props.gridSize
      newY = Math.round(newY / props.gridSize) * props.gridSize
    }
    
    emit('update:position', {
      ...position.value,
      x: newX,
      y: newY,
      width: newWidth,
      height: newHeight,
    })
    
    emit('update:size', newWidth, newHeight)
  }
}

// 鼠标释放处理
function handleMouseUp() {
  isDragging.value = false
  isResizing.value = false
  pendingDrag.value = false
  // flush pending position immediately if any
  if (rafId.value != null) {
    window.cancelAnimationFrame(rafId.value)
    rafId.value = null
  }
  if (pendingPosition.value) {
    emit('update:position', {
      ...position.value,
      x: Math.max(0, pendingPosition.value.x),
      y: Math.max(0, pendingPosition.value.y),
    } as ComponentPosition)
    pendingPosition.value = null
  }
}

// 处理子组件内容尺寸变化（DOM 像素），将其转换为画布坐标并上报
function handleContentSize(size: { width: number; height: number }) {
  // DOM size is affected by canvas scaling; convert back to logical canvas coords
  const logicalWidth = Math.max(50, Math.round(size.width / props.zoom))
  const logicalHeight = Math.max(30, Math.round(size.height / props.zoom))
  // 发出更新尺寸事件
  emit('update:size', logicalWidth, logicalHeight)
}

// 监听鼠标事件
onMounted(() => {
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
})

const inlineTextareaRef = ref<HTMLTextAreaElement | null>(null)

async function saveInlineEdit() {
  // emit update to parent with new content
  const newContent = inlineContent.value
  emit('update:component', {
    ...props.component,
    config: {
      ...(props.component.config || {}),
      content: newContent,
    },
  })
  // wait nextTick so StepComponentRenderer measures updated DOM and emits size
  await Promise.resolve()
}
</script>

<style scoped>
.component-instance {
  cursor: move;
  user-select: none;
  pointer-events: auto;
  touch-action: none; /* 防止移动端默认行为 */
}

.component-instance.selected {
  outline: 2px dashed #3b82f6;
  outline-offset: -2px;
}

.component-content {
  width: 100%;
  height: 100%;
  pointer-events: none; /* 让鼠标事件穿透到父组件 */
  user-select: none;
}

.component-content-inner {
  width: 100%;
  height: 100%;
  pointer-events: auto; /* 内容区域可以交互 */
  user-select: text; /* 允许文本选择（默认父级禁用时覆盖） */
}

.inline-textarea {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  padding: 12px;
  border: 1px solid rgba(0,0,0,0.12);
  border-radius: 6px;
  resize: none;
  font-size: 14px;
  line-height: 1.6;
  z-index: 30;
}

.selection-box {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.resize-handle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border: 1px solid #ffffff;
  border-radius: 2px;
  pointer-events: auto;
  cursor: nwse-resize;
}

.handle-n {
  cursor: ns-resize;
}

.handle-s {
  cursor: ns-resize;
}

.handle-e {
  cursor: ew-resize;
}

.handle-w {
  cursor: ew-resize;
}

.handle-nw {
  cursor: nwse-resize;
}

.handle-ne {
  cursor: nesw-resize;
}

.handle-sw {
  cursor: nesw-resize;
}

.handle-se {
  cursor: nwse-resize;
}

.delete-button {
  position: absolute;
  top: -12px;
  right: -12px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #dc2626;
  color: #ffffff;
  border: 2px solid #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  line-height: 1;
  z-index: 10;
}

.delete-button:hover {
  background: #b91c1c;
}
</style>

