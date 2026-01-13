<template>
  <div
    class="component-renderer"
    :class="{ 'positioned': component.position }"
    :style="componentStyle"
  >
    <!-- 代码编辑器 -->
    <InteractiveCodeEditor
      v-if="component.type === 'code'"
      :language="component.config?.language || 'python'"
      :template="component.config?.template || ''"
      :test-cases="component.config?.testCases || []"
      :run-button="component.config?.runButton !== false"
    />

    <!-- 拖拽排序 -->
    <DragDropSorter
      v-else-if="component.type === 'drag-drop'"
      :items="component.config?.items || []"
      :target-zones="component.config?.targetZones || []"
    />

    <!-- 视频交互 -->
    <InteractiveVideo
      v-else-if="component.type === 'video'"
      :url="component.config?.url || ''"
      :checkpoints="component.config?.checkpoints || []"
      :progress-tracking="component.config?.progressTracking !== false"
    />

    <!-- 绘图 -->
    <DrawingCanvas
      v-else-if="component.type === 'drawing'"
      :background-image="component.config?.backgroundImage"
      :tools="component.config?.tools || ['pen']"
      :save-on-complete="component.config?.saveOnComplete !== false"
      @save="handleSave"
    />

    <!-- 文本 / 标题 -->
    <div v-else-if="component.type === 'text' || component.type === 'title'" :class="['text-component', component.type === 'title' ? 'title-component' : '']">
      <div ref="contentRef" :style="contentInnerStyle" v-html="renderMarkdown(component.config?.content || '')"></div>
    </div>

    <!-- 图片 -->
    <div v-else-if="component.type === 'image'" class="image-component">
      <img :src="component.config?.url" :alt="component.config?.alt || ''" />
    </div>

    <!-- 题目 -->
    <div v-else-if="component.type === 'quiz'" class="quiz-component">
      <div class="quiz-question">{{ component.config?.question }}</div>
      <div class="quiz-options">
        <div
          v-for="(option, idx) in component.config?.options || []"
          :key="idx"
          class="quiz-option"
          @click="selectOption(option.value || String.fromCharCode(65 + idx))"
          :class="{ selected: selectedAnswer === (option.value || String.fromCharCode(65 + idx)) }"
        >
          <span class="option-label">{{ String.fromCharCode(65 + idx) }}</span>
          <span class="option-text">{{ option.text }}</span>
        </div>
      </div>
      <div v-if="showAnswer" class="quiz-answer">
        <span v-if="isCorrect" class="correct">✅ 回答正确！</span>
        <span v-else class="incorrect">❌ 回答错误，正确答案是：{{ component.config?.answer }}</span>
        <div v-if="component.config?.explanation" class="explanation">
          解析：{{ component.config.explanation }}
        </div>
      </div>
    </div>

    <!-- 未知类型 -->
    <div v-else class="unknown-component">
      未知组件类型: {{ component.type }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineAsyncComponent, onMounted, watch, nextTick } from 'vue'
import { marked } from 'marked'
import type { StepComponent } from '../../types/coursePlayer'

// 懒加载交互组件（相对路径在同一目录）
const InteractiveCodeEditor = defineAsyncComponent(() => import('../ui/InteractiveCodeEditor.vue'))
const DragDropSorter = defineAsyncComponent(() => import('./DragDropSorter.vue'))
const InteractiveVideo = defineAsyncComponent(() => import('./InteractiveVideo.vue'))
const DrawingCanvas = defineAsyncComponent(() => import('./DrawingCanvas.vue'))

interface Props {
  component: StepComponent
  embedded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  embedded: false,
})

const emit = defineEmits<{
  (e: 'content-size', size: { width: number; height: number }): void
}>()

const contentRef = ref<HTMLElement | null>(null)

async function measureAndEmitSize() {
  await nextTick()
  if (!contentRef.value) return
  const rect = contentRef.value.getBoundingClientRect()
  const width = Math.ceil(rect.width)
  const height = Math.ceil(rect.height)
  emit('content-size', { width, height })
}

onMounted(() => {
  measureAndEmitSize()
})

watch(
  () => props.component?.config?.content,
  () => {
    measureAndEmitSize()
  },
  { immediate: false }
)

const selectedAnswer = ref<string | null>(null)
const showAnswer = ref(false)
const isCorrect = ref(false)

// 计算组件样式
const componentStyle = computed(() => {
  const style: Record<string, string> = {}

  // 如果组件在“独立渲染”模式（非嵌入），则 StepComponentRenderer 负责绝对定位；
  // 在画布嵌入（embedded=true）时，外层容器负责定位和尺寸，内部应充满父元素。
  if (!props.embedded && props.component.position) {
    style.position = 'absolute'
    style.left = `${props.component.position.x}px`
    style.top = `${props.component.position.y}px`
    style.width = `${props.component.position.width}px`
    style.height = `${props.component.position.height}px`
    if (props.component.position.rotation) {
      style.transform = `rotate(${props.component.position.rotation}deg)`
    }
  } else if (props.embedded) {
    // fill the parent container
    style.position = 'relative'
    style.width = '100%'
    style.height = '100%'
  }

  // 应用组件样式
  if (props.component.style) {
    const compStyle = props.component.style
    if (compStyle.fontFamily) style.fontFamily = compStyle.fontFamily
    if (compStyle.fontSize) style.fontSize = `${compStyle.fontSize}px`
    if (compStyle.fontWeight) style.fontWeight = String(compStyle.fontWeight)
    if (compStyle.fontStyle) style.fontStyle = compStyle.fontStyle
    if (compStyle.color) style.color = compStyle.color
    if ((compStyle as any).textShadow) style.textShadow = (compStyle as any).textShadow
    if (compStyle.textAlign) style.textAlign = compStyle.textAlign
    if (compStyle.backgroundColor) style.backgroundColor = compStyle.backgroundColor
    if (compStyle.backgroundImage) style.backgroundImage = `url(${compStyle.backgroundImage})`
    if (compStyle.borderWidth) style.borderWidth = `${compStyle.borderWidth}px`
    if (compStyle.borderStyle) style.borderStyle = compStyle.borderStyle
    if (compStyle.borderColor) style.borderColor = compStyle.borderColor
    if (compStyle.borderRadius) style.borderRadius = `${compStyle.borderRadius}px`
    if (compStyle.boxShadow) style.boxShadow = compStyle.boxShadow
    if (compStyle.padding) style.padding = compStyle.padding
    if (compStyle.margin) style.margin = compStyle.margin
    if (compStyle.opacity !== undefined) style.opacity = String(compStyle.opacity)
    if (compStyle.zIndex !== undefined) style.zIndex = String(compStyle.zIndex)
    if (compStyle.transform && !props.component.position?.rotation) {
      style.transform = compStyle.transform
    }
  }

  return style
})

// 自适应字体：当组件高度变化或内容变化时，自动调整字体大小/行高以避免溢出
const adaptiveFontSize = ref<number | null>(null)
const adaptiveLineHeight = ref<string | null>(null)
const MIN_FONT_SIZE = 10

async function adjustTextToFit() {
  await nextTick()
  const el = contentRef.value
  if (!el) return

  const compStyle = props.component.style || {}
  const baseFontSize = Number(compStyle.fontSize || 24)
  // start attempt from either current adaptive or base
  let attempt = adaptiveFontSize.value ? adaptiveFontSize.value : baseFontSize
  // ensure attempt is not larger than base
  attempt = Math.min(attempt, baseFontSize)

  // helper to apply attempt and measure
  const applyAndMeasure = async (size: number) => {
    adaptiveFontSize.value = size
    // set adaptive line-height proportional unless user set explicit lineHeight
    if (!compStyle.lineHeight) {
      adaptiveLineHeight.value = `${Math.max(1, +(size * 1.2).toFixed(1))}px`
    } else {
      adaptiveLineHeight.value = String(compStyle.lineHeight)
    }
    await nextTick()
    return el.scrollHeight <= el.clientHeight
  }

  // If content already fits, try to grow up to baseFontSize
  if (await applyAndMeasure(attempt)) {
    while (attempt < baseFontSize) {
      const nextSize = Math.min(baseFontSize, attempt + 1)
      if (await applyAndMeasure(nextSize)) {
        attempt = nextSize
        continue
      }
      break
    }
    return
  }

  // Otherwise reduce until it fits or reach MIN_FONT_SIZE
  while (attempt > MIN_FONT_SIZE) {
    attempt = Math.max(MIN_FONT_SIZE, attempt - 1)
    if (await applyAndMeasure(attempt)) {
      return
    }
    if (attempt === MIN_FONT_SIZE) break
  }
}

// 为了保证通过 v-html 注入的内部 HTML（如 <h1>/<h2>/<p>）也能准确接收字体相关样式（颜色、粗体、斜体、阴影等），
// 额外计算一个只包含“文本相关”样式的内层样式，并绑定到渲染内容的内层容器上。
const contentInnerStyle = computed(() => {
  const s: Record<string, string> = {}
  const compStyle = props.component.style || {}
  if (compStyle.fontFamily) s.fontFamily = compStyle.fontFamily
  // if adaptiveFontSize is active prefer it, otherwise use configured fontSize
  if (adaptiveFontSize.value) s.fontSize = `${adaptiveFontSize.value}px`
  else if (compStyle.fontSize) s.fontSize = `${compStyle.fontSize}px`
  if (compStyle.fontWeight) s.fontWeight = String(compStyle.fontWeight)
  if (compStyle.fontStyle) s.fontStyle = compStyle.fontStyle
  if (compStyle.color) s.color = compStyle.color
  if ((compStyle as any).textShadow) s.textShadow = (compStyle as any).textShadow
  if (compStyle.textAlign) s.textAlign = compStyle.textAlign
  // prefer adaptive line-height when present
  if (adaptiveLineHeight.value) s.lineHeight = adaptiveLineHeight.value
  else if ((compStyle as any).lineHeight) s.lineHeight = String((compStyle as any).lineHeight)
  // additional text-related properties
  if ((compStyle as any).letterSpacing !== undefined) s.letterSpacing = String((compStyle as any).letterSpacing)
  if ((compStyle as any).wordSpacing !== undefined) s.wordSpacing = String((compStyle as any).wordSpacing)
  // textDecoration may be provided as a shorthand string like "underline" or "line-through"
  if ((compStyle as any).textDecoration) s.textDecoration = (compStyle as any).textDecoration
  if ((compStyle as any).textDecorationColor) s.textDecorationColor = (compStyle as any).textDecorationColor
  if ((compStyle as any).textDecorationStyle) s.textDecorationStyle = (compStyle as any).textDecorationStyle
  if ((compStyle as any).textDecorationThickness !== undefined) s.textDecorationThickness = String((compStyle as any).textDecorationThickness)
  if ((compStyle as any).textTransform) s.textTransform = (compStyle as any).textTransform
  if ((compStyle as any).textIndent !== undefined) s.textIndent = String((compStyle as any).textIndent)
  return s
})

function renderMarkdown(content: string): string {
  // Enable GFM line breaks so single newlines produce <br>, preserving user-entered newlines
  try {
    return marked(content || '', { breaks: true })
  } catch (e) {
    // fallback to escaped text with line breaks
    return (content || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>')
  }
}

// 在内容或容器变化时触发自适应
watch(
  () => [props.component.config?.content, props.component.style?.fontSize, props.component.position?.height, props.component.position?.width],
  () => {
    adjustTextToFit().catch(() => {})
  },
  { immediate: true, deep: false }
)

onMounted(() => {
  // 观察父容器尺寸变化（例如拖动改变 size），尝试在 resize 时适配文本
  const el = contentRef.value
  if (el && (window as any).ResizeObserver) {
    const ro = new (window as any).ResizeObserver(() => {
      adjustTextToFit().catch(() => {})
    })
    ro.observe(el)
  }
})

function selectOption(value: string) {
  selectedAnswer.value = value
  isCorrect.value = value === props.component.config?.answer
  showAnswer.value = true
}

function handleSave(imageData: string) {
  console.log('Image saved:', imageData)
  // 可以触发事件或保存到后端
}
</script>

<style scoped>
.component-renderer {
  margin: 1rem 0;
}

.component-renderer.positioned {
  margin: 0;
}

.text-component {
  padding: 1rem;
  background: rgba(255,255,255,0.92);
  border-radius: 8px;
  line-height: 1.8;
  border: 1px dashed #e5e7eb;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  min-height: 40px;
  color: #111827;
  overflow-wrap: break-word;
  /* Ensure text component stretches to fill the renderer when embedded,
     so resizing the selection box changes the visible text box height. */
  height: 100%;
  display: flex;
  flex-direction: column;
}

.title-component {
  /* title specific default styling; can be overridden by component.style */
  font-size: 48px;
  font-weight: 700;
  line-height: 1.1;
}

/* Make the inner content element fill the remaining space so v-html content
   grows/shrinks with the component box. */
.text-component > div[ref] {
  flex: 1 1 auto;
  overflow: auto;
}

.image-component {
  text-align: center;
  margin: 1rem 0;
}

.image-component img {
  max-width: 100%;
  border-radius: 8px;
}

.quiz-component {
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.quiz-question {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1f2937;
}

.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.quiz-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.quiz-option:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.quiz-option.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.option-label {
  font-weight: 700;
  color: #3b82f6;
  min-width: 24px;
}

.quiz-answer {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 8px;
}

.quiz-answer .correct {
  color: #059669;
  font-weight: 600;
}

.quiz-answer .incorrect {
  color: #dc2626;
  font-weight: 600;
}

.explanation {
  margin-top: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.unknown-component {
  padding: 1rem;
  background: #fee2e2;
  border: 1px solid #dc2626;
  border-radius: 8px;
  color: #dc2626;
  text-align: center;
}
</style>


