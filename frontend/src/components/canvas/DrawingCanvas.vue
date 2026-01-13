<template>
  <div class="canvas-container">
    <div class="toolbar">
      <button
        v-for="tool in tools"
        :key="tool"
        class="tool-btn"
        :class="{ active: currentTool === tool }"
        @click="selectTool(tool)"
      >
        {{ getToolIcon(tool) }} {{ getToolName(tool) }}
      </button>
      <button class="tool-btn" @click="clear">🗑️ 清除</button>
      <button class="tool-btn" @click="save">💾 保存</button>
    </div>
    <div class="canvas-wrapper">
      <canvas
        ref="canvasRef"
        @mousedown="startDraw"
        @mousemove="draw"
        @mouseup="stopDraw"
        @mouseleave="stopDraw"
      />
    </div>
    <div v-if="backgroundImage" class="background-info">
      背景图片已加载
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

interface Props {
  backgroundImage?: string
  tools?: string[]
  saveOnComplete?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  backgroundImage: '',
  tools: () => ['pen', 'text', 'shape'],
  saveOnComplete: true
})

const emit = defineEmits<{
  (e: 'save', imageData: string): void
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const currentTool = ref('pen')
const isDrawing = ref(false)
const lastX = ref(0)
const lastY = ref(0)
const ctx = ref<CanvasRenderingContext2D | null>(null)

const tools = ref([...props.tools])

onMounted(() => {
  if (canvasRef.value) {
    ctx.value = canvasRef.value.getContext('2d')
    if (ctx.value) {
      // 设置画布大小
      canvasRef.value.width = 800
      canvasRef.value.height = 600
      
      // 设置绘制样式
      ctx.value.strokeStyle = '#000000'
      ctx.value.lineWidth = 2
      ctx.value.lineCap = 'round'
      ctx.value.lineJoin = 'round'
    }

    // 加载背景图片
    if (props.backgroundImage) {
      loadBackgroundImage(props.backgroundImage)
    }
  }
})

watch(() => props.backgroundImage, (newImage) => {
  if (newImage && canvasRef.value && ctx.value) {
    loadBackgroundImage(newImage)
  }
})

function loadBackgroundImage(url: string) {
  if (!canvasRef.value || !ctx.value) return

  const img = new Image()
  img.crossOrigin = 'anonymous'
  img.onload = () => {
    if (canvasRef.value && ctx.value) {
      ctx.value.drawImage(img, 0, 0, canvasRef.value.width, canvasRef.value.height)
    }
  }
  img.src = url
}

function selectTool(tool: string) {
  currentTool.value = tool
}

function getToolIcon(tool: string): string {
  const icons: Record<string, string> = {
    pen: '✏️',
    text: '📝',
    shape: '🔷',
    eraser: '🧹'
  }
  return icons[tool] || '🛠️'
}

function getToolName(tool: string): string {
  const names: Record<string, string> = {
    pen: '画笔',
    text: '文字',
    shape: '形状',
    eraser: '橡皮'
  }
  return names[tool] || tool
}

function getMousePos(event: MouseEvent) {
  if (!canvasRef.value) return { x: 0, y: 0 }
  const rect = canvasRef.value.getBoundingClientRect()
  return {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
}

function startDraw(event: MouseEvent) {
  if (!ctx.value) return

  isDrawing.value = true
  const pos = getMousePos(event)
  lastX.value = pos.x
  lastY.value = pos.y

  if (currentTool.value === 'pen') {
    ctx.value.beginPath()
    ctx.value.moveTo(lastX.value, lastY.value)
  }
}

function draw(event: MouseEvent) {
  if (!isDrawing.value || !ctx.value) return

  const pos = getMousePos(event)

  if (currentTool.value === 'pen') {
    ctx.value.lineTo(pos.x, pos.y)
    ctx.value.stroke()
  } else if (currentTool.value === 'eraser') {
    ctx.value.globalCompositeOperation = 'destination-out'
    ctx.value.lineTo(pos.x, pos.y)
    ctx.value.stroke()
    ctx.value.globalCompositeOperation = 'source-over'
  }

  lastX.value = pos.x
  lastY.value = pos.y
}

function stopDraw() {
  if (isDrawing.value && ctx.value) {
    ctx.value.closePath()
  }
  isDrawing.value = false
}

function clear() {
  if (!canvasRef.value || !ctx.value) return
  if (confirm('确定要清除所有内容吗？')) {
    ctx.value.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
    // 重新加载背景图片
    if (props.backgroundImage) {
      loadBackgroundImage(props.backgroundImage)
    }
  }
}

function save() {
  if (!canvasRef.value) return
  const imageData = canvasRef.value.toDataURL('image/png')
  emit('save', imageData)
  if (props.saveOnComplete) {
    alert('图片已保存')
  }
}
</script>

<style scoped>
.canvas-container {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  background: #ffffff;
}

.toolbar {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  flex-wrap: wrap;
}

.tool-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #ffffff;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.tool-btn:hover {
  background: #f3f4f6;
}

.tool-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.canvas-wrapper {
  padding: 1rem;
  background: #f9fafb;
  display: flex;
  justify-content: center;
}

canvas {
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: #ffffff;
  cursor: crosshair;
}

.background-info {
  padding: 0.5rem 1rem;
  background: #ecfdf5;
  color: #059669;
  font-size: 0.875rem;
  text-align: center;
}
</style>


