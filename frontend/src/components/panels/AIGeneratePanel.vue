<template>
  <div class="ai-generate-panel">
    <div class="ai-header">
      <div class="ai-title">
        <span class="ai-icon">✨</span>
        <span>AI 智能生成</span>
      </div>
      <button
        v-if="canGenerate"
        class="btn-ai-generate"
        :disabled="generating"
        @click="handleGenerate"
      >
        {{ generating ? '生成中...' : '🤖 AI 生成' }}
      </button>
    </div>

    <div v-if="showPromptInput" class="prompt-section">
      <label class="prompt-label">{{ promptLabel }}</label>
      <textarea
        v-model="prompt"
        :placeholder="promptPlaceholder"
        class="prompt-textarea"
        rows="3"
      ></textarea>
    </div>

    <!-- AI 生成中的状态 -->
    <div v-if="generating" class="generating-status">
      <div class="loading-spinner"></div>
      <p>AI 正在智能生成，请稍候...</p>
    </div>

    <!-- AI 生成结果展示 -->
    <div v-if="result && !generating" class="result-section">
      <div class="result-header">
        <h4>AI 生成结果</h4>
        <div class="result-actions">
          <button class="btn-action accept" @click="handleAccept">✓ 接受</button>
          <button class="btn-action reject" @click="handleReject">✗ 拒绝</button>
          <button class="btn-action regenerate" @click="handleRegenerate">🔄 重新生成</button>
        </div>
      </div>

      <div class="result-content">
        <slot name="result" :data="result">
          <!-- 默认显示 JSON 格式 -->
          <pre class="result-json">{{ JSON.stringify(result, null, 2) }}</pre>
        </slot>
      </div>
    </div>

    <!-- 错误信息 -->
    <div v-if="error" class="error-message">
      <span class="error-icon">⚠️</span>
      <span>{{ error }}</span>
      <button class="btn-close-error" @click="error = null">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  // 是否显示 AI 生成按钮
  canGenerate?: boolean
  // 是否显示提示词输入框
  showPromptInput?: boolean
  // 提示词标签
  promptLabel?: string
  // 提示词占位符
  promptPlaceholder?: string
  // 初始提示词
  initialPrompt?: string
}

const props = withDefaults(defineProps<Props>(), {
  canGenerate: true,
  showPromptInput: false,
  promptLabel: '生成指令（可选）',
  promptPlaceholder: '请输入您希望 AI 生成的内容描述...',
  initialPrompt: '',
})

const emit = defineEmits<{
  (e: 'generate', prompt: string): void
  (e: 'accept', result: any): void
  (e: 'reject'): void
  (e: 'regenerate', prompt: string): void
}>()

const generating = ref(false)
const prompt = ref(props.initialPrompt)
const result = ref<any>(null)
const error = ref<string | null>(null)

// 开始生成
const handleGenerate = () => {
  error.value = null
  emit('generate', prompt.value)
}

// 接受结果
const handleAccept = () => {
  emit('accept', result.value)
  result.value = null
  prompt.value = ''
}

// 拒绝结果
const handleReject = () => {
  emit('reject')
  result.value = null
}

// 重新生成
const handleRegenerate = () => {
  error.value = null
  emit('regenerate', prompt.value)
}

// 暴露方法供父组件调用
defineExpose({
  setGenerating(val: boolean) {
    generating.value = val
  },
  setResult(data: any) {
    result.value = data
    generating.value = false
  },
  setError(msg: string) {
    error.value = msg
    generating.value = false
  },
  clear() {
    result.value = null
    error.value = null
    generating.value = false
  },
})
</script>

<style scoped>
.ai-generate-panel {
  border: 2px dashed #a78bfa;
  border-radius: 8px;
  padding: 1rem;
  background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
  margin-bottom: 1rem;
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.ai-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 0.95rem;
  color: #7c3aed;
}

.ai-icon {
  font-size: 1.2rem;
}

.btn-ai-generate {
  padding: 0.5rem 1.2rem;
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: #ffffff;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(139, 92, 246, 0.3);
}

.btn-ai-generate:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}

.btn-ai-generate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.prompt-section {
  margin-bottom: 0.75rem;
}

.prompt-label {
  display: block;
  font-size: 0.85rem;
  color: #6b21a8;
  margin-bottom: 0.4rem;
  font-weight: 500;
}

.prompt-textarea {
  width: 100%;
  padding: 0.6rem;
  border-radius: 6px;
  border: 1px solid #d8b4fe;
  font-size: 0.9rem;
  resize: vertical;
  background: #ffffff;
  font-family: inherit;
}

.prompt-textarea:focus {
  outline: none;
  border-color: #a78bfa;
  box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
}

.generating-status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #ffffff;
  border-radius: 6px;
  color: #7c3aed;
  font-size: 0.9rem;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #e9d5ff;
  border-top-color: #8b5cf6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.result-section {
  background: #ffffff;
  border-radius: 6px;
  padding: 0.75rem;
  border: 1px solid #e9d5ff;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #f3e8ff;
}

.result-header h4 {
  margin: 0;
  font-size: 0.9rem;
  color: #6b21a8;
}

.result-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  padding: 0.35rem 0.8rem;
  border-radius: 6px;
  border: 1px solid;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-action.accept {
  background: #10b981;
  color: #ffffff;
  border-color: #10b981;
}

.btn-action.accept:hover {
  background: #059669;
}

.btn-action.reject {
  background: #ffffff;
  color: #ef4444;
  border-color: #ef4444;
}

.btn-action.reject:hover {
  background: #fef2f2;
}

.btn-action.regenerate {
  background: #ffffff;
  color: #8b5cf6;
  border-color: #a78bfa;
}

.btn-action.regenerate:hover {
  background: #faf5ff;
}

.result-content {
  max-height: 400px;
  overflow-y: auto;
}

.result-json {
  background: #f9fafb;
  padding: 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  overflow-x: auto;
  margin: 0;
  color: #374151;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #dc2626;
  font-size: 0.85rem;
  margin-top: 0.75rem;
}

.error-icon {
  font-size: 1.1rem;
}

.btn-close-error {
  margin-left: auto;
  border: none;
  background: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #dc2626;
  padding: 0;
  line-height: 1;
}
</style>

