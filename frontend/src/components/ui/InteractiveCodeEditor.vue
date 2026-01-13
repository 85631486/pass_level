<template>
  <div class="code-editor-container">
    <div class="editor-header">
      <span class="language-badge">{{ language }} 代码编辑器</span>
      <button @click="runCode" :disabled="running" class="run-button">
        {{ running ? '运行中...' : '▶️ 运行代码' }}
      </button>
    </div>
    <div class="editor-wrapper">
      <textarea
        v-model="code"
        class="code-textarea"
        :placeholder="`输入${language}代码...`"
        @input="onCodeChange"
      />
    </div>
    <div v-if="output" class="output-panel">
      <div class="output-header">运行结果</div>
      <div class="output-content">
        <div v-for="(result, idx) in testResults" :key="idx" class="test-result">
          <span :class="result.passed ? 'pass' : 'fail'">
            {{ result.passed ? '✅' : '❌' }} 测试 {{ idx + 1 }}
          </span>
          <div v-if="result.message" class="result-message">{{ result.message }}</div>
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="output && !error && testResults.length === 0" class="output-text">{{ output }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  language?: string
  template?: string
  testCases?: Array<{ input: string; output: string }>
  runButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  language: 'python',
  template: '',
  testCases: () => [],
  runButton: true
})

const code = ref(props.template || '')
const running = ref(false)
const output = ref('')
const error = ref('')
const testResults = ref<Array<{ passed: boolean; message?: string }>>([])

watch(() => props.template, (newTemplate) => {
  if (newTemplate && !code.value) {
    code.value = newTemplate
  }
})

function onCodeChange() {
  output.value = ''
  error.value = ''
  testResults.value = []
}

async function runCode() {
  if (!code.value.trim()) {
    error.value = '请输入代码'
    return
  }

  running.value = true
  output.value = ''
  error.value = ''
  testResults.value = []

  try {
    // 模拟代码运行（实际应该调用后端API或Web Worker）
    await simulateCodeExecution()
  } catch (err: any) {
    error.value = err.message || '代码运行失败'
  } finally {
    running.value = false
  }
}

async function simulateCodeExecution() {
  // 模拟延迟
  await new Promise(resolve => setTimeout(resolve, 500))

  // 如果有测试用例，运行测试
  if (props.testCases && props.testCases.length > 0) {
    for (let i = 0; i < props.testCases.length; i++) {
      const testCase = props.testCases[i]
      // 这里应该实际执行代码并验证输出
      // 目前只是模拟
      const passed = Math.random() > 0.3 // 模拟70%通过率
      testResults.value.push({
        passed,
        message: passed ? '测试通过' : `期望输出: ${testCase?.output || '无期望输出'}`
      })
    }
  } else {
    // 没有测试用例，只显示输出
    output.value = '代码执行成功（模拟输出）'
  }
}
</script>

<style scoped>
.code-editor-container {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  background: #ffffff;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.language-badge {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.run-button {
  padding: 0.5rem 1rem;
  border: 1px solid #3b82f6;
  border-radius: 6px;
  background: #3b82f6;
  color: white;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.run-button:hover:not(:disabled) {
  background: #2563eb;
}

.run-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.editor-wrapper {
  position: relative;
}

.code-textarea {
  width: 100%;
  min-height: 300px;
  padding: 1rem;
  border: none;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
  resize: vertical;
  background: #1e293b;
  color: #e2e8f0;
}

.code-textarea:focus {
  outline: none;
}

.output-panel {
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.output-header {
  padding: 0.75rem 1rem;
  font-weight: 600;
  font-size: 0.875rem;
  border-bottom: 1px solid #e5e7eb;
}

.output-content {
  padding: 1rem;
}

.test-result {
  margin-bottom: 0.5rem;
}

.test-result .pass {
  color: #059669;
  font-weight: 600;
}

.test-result .fail {
  color: #dc2626;
  font-weight: 600;
}

.result-message {
  margin-left: 1.5rem;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.error-message {
  color: #dc2626;
  padding: 0.75rem;
  background: #fee2e2;
  border-radius: 4px;
  font-size: 0.875rem;
}

.output-text {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.875rem;
  color: #374151;
  white-space: pre-wrap;
}
</style>

