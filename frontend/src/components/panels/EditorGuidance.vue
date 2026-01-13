<template>
  <div class="editor-guidance" v-if="showGuidance">
    <div class="guidance-header">
      <div class="guidance-icon">🚀</div>
      <div class="guidance-title">
        <h3>快速开始指南</h3>
        <p>按照以下步骤创建您的第一个交互式关卡</p>
      </div>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>

    <div class="guidance-steps">
      <div
        v-for="(step, index) in guidanceSteps"
        :key="step.id"
        class="step-item"
        :class="{ active: currentStep === step.id, completed: completedSteps.includes(step.id) }"
      >
        <div class="step-number">{{ index + 1 }}</div>
        <div class="step-content">
          <div class="step-title">{{ step.title }}</div>
          <div class="step-description">{{ step.description }}</div>
          <div v-if="step.action" class="step-action">
            <button
              class="action-btn"
              @click="$emit('action', step.action)"
              :disabled="step.disabled"
            >
              {{ step.actionText }}
            </button>
          </div>
        </div>
        <div class="step-status">
          <span v-if="completedSteps.includes(step.id)">✅</span>
          <span v-else-if="currentStep === step.id">🔄</span>
          <span v-else>⏳</span>
        </div>
      </div>
    </div>

    <div class="guidance-progress">
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: progressPercent + '%' }"
        ></div>
      </div>
      <div class="progress-text">
        完成度：{{ completedSteps.length }}/{{ guidanceSteps.length }}
      </div>
    </div>

    <div class="guidance-footer">
      <button class="skip-btn" @click="$emit('skip')">跳过引导</button>
      <div class="footer-hint">
        💡 随时可以点击右上角的帮助按钮重新查看此指南
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'

interface GuidanceStep {
  id: string
  title: string
  description: string
  action?: string
  actionText?: string
  disabled?: boolean
}

interface Props {
  showGuidance: boolean
  currentState: {
    hasContent: boolean
    hasJsonData: boolean
    hasPreview: boolean
    hasSaved: boolean
  }
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  skip: []
  action: [action: string]
}>()

const guidanceSteps: GuidanceStep[] = [
  {
    id: 'write-content',
    title: '编写教学内容',
    description: '在左侧Markdown编辑器中编写您的教学内容，包括学习目标、操作步骤等。',
    action: 'load-template',
    actionText: '📋 加载模板'
  },
  {
    id: 'use-ai',
    title: 'AI智能转换',
    description: '点击"AI转换"按钮，让AI将您的Markdown内容转换为交互式学习组件。',
    action: 'ai-convert',
    actionText: '✨ 开始转换'
  },
  {
    id: 'check-json',
    title: '检查交互数据',
    description: '在右侧查看AI生成的JSON数据，确保内容正确。',
    disabled: true
  },
  {
    id: 'preview-test',
    title: '预览测试',
    description: '点击"预览"按钮在新窗口中查看学生的学习界面。',
    action: 'preview',
    actionText: '👁️ 预览测试',
    disabled: true
  },
  {
    id: 'visual-edit',
    title: '可视化编辑',
    description: '如需精细调整，可以使用可视化编辑器进行拖拽编辑。',
    action: 'visual-editor',
    actionText: '🎨 可视化编辑',
    disabled: true
  },
  {
    id: 'save-publish',
    title: '保存发布',
    description: '保存您的关卡内容，发布后学生就可以开始学习了。',
    action: 'save',
    actionText: '💾 保存关卡',
    disabled: true
  }
]

// 计算当前步骤
const currentStep = computed(() => {
  if (!props.currentState.hasContent) return 'write-content'
  if (!props.currentState.hasJsonData) return 'use-ai'
  if (!props.currentState.hasPreview) return 'preview-test'
  if (!props.currentState.hasSaved) return 'save-publish'
  return 'completed'
})

// 计算已完成步骤
const completedSteps = computed(() => {
  const completed: string[] = []

  if (props.currentState.hasContent) completed.push('write-content')
  if (props.currentState.hasJsonData) {
    completed.push('write-content', 'use-ai', 'check-json')
  }
  if (props.currentState.hasPreview) {
    completed.push('write-content', 'use-ai', 'check-json', 'preview-test')
  }
  if (props.currentState.hasSaved) {
    completed.push('write-content', 'use-ai', 'check-json', 'preview-test', 'visual-edit', 'save-publish')
  }

  return completed
})

// 计算进度百分比
const progressPercent = computed(() => {
  return Math.round((completedSteps.value.length / guidanceSteps.length) * 100)
})

// 更新步骤状态
const updateStepStates = () => {
  guidanceSteps.forEach(step => {
    if (step.id === 'check-json') {
      step.disabled = !props.currentState.hasJsonData
    } else if (step.id === 'preview-test') {
      step.disabled = !props.currentState.hasJsonData
    } else if (step.id === 'visual-edit') {
      step.disabled = !props.currentState.hasPreview
    } else if (step.id === 'save-publish') {
      step.disabled = !props.currentState.hasPreview
    }
  })
}

watch(() => props.currentState, updateStepStates, { deep: true, immediate: true })
</script>

<style scoped>
.editor-guidance {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  z-index: 2000;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.guidance-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.guidance-icon {
  font-size: 2rem;
}

.guidance-title h3 {
  margin: 0 0 0.25rem;
  font-size: 1.25rem;
  color: #1f2937;
}

.guidance-title p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.close-btn {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background 0.15s ease;
}

.close-btn:hover {
  background: #f3f4f6;
}

.guidance-steps {
  padding: 1rem;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.step-item.active {
  background: #eff6ff;
  border-color: #3b82f6;
}

.step-item.completed {
  background: #f0fdf4;
  border-color: #22c55e;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e5e7eb;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.step-item.active .step-number {
  background: #3b82f6;
  color: white;
}

.step-item.completed .step-number {
  background: #22c55e;
  color: white;
}

.step-content {
  flex: 1;
}

.step-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.step-description {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.4;
  margin-bottom: 0.5rem;
}

.step-action {
  margin-top: 0.5rem;
}

.action-btn {
  padding: 0.375rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  color: #374151;
  cursor: pointer;
  font-size: 0.8125rem;
  transition: all 0.15s ease;
}

.action-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.step-status {
  font-size: 1.25rem;
  opacity: 0.7;
}

.guidance-progress {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #06b6d4);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  font-size: 0.875rem;
  color: #6b7280;
}

.guidance-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.skip-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #f9fafb;
  color: #6b7280;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.15s ease;
}

.skip-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.footer-hint {
  font-size: 0.75rem;
  color: #9ca3af;
  text-align: right;
  max-width: 200px;
}

@media (max-width: 640px) {
  .editor-guidance {
    width: 95%;
    margin: 1rem;
  }

  .guidance-header {
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }

  .guidance-footer {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }

  .footer-hint {
    text-align: center;
    max-width: none;
  }
}
</style>

