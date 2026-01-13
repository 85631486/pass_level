<template>
  <div class="teaching-guide-assistant">
    <div class="assistant-header">
      <h3>🤖 教案生成助理</h3>
    </div>

    <div class="assistant-content">
      <!-- 提示模板选择 -->
      <div class="template-section">
        <div class="section-header">
          <label class="form-label section-title">
            <span>选择提示模板</span>
          </label>
          <button class="btn-collapse" type="button" @click="collapsed.template = !collapsed.template">
            {{ collapsed.template ? '展开' : '收起' }}
          </button>
        </div>
        <div v-show="!collapsed.template" class="template-grid">
          <button
            v-for="template in templates"
            :key="template.id"
            class="template-card"
            :class="{ active: selectedTemplate === template.id }"
            @click="selectedTemplate = template.id"
          >
            <div class="template-icon">{{ template.icon }}</div>
            <div class="template-name">{{ template.name }}</div>
            <div class="template-desc">{{ template.description }}</div>
          </button>
        </div>
      </div>

      <!-- 基本信息输入 -->
      <div class="form-section">
        <div class="section-header">
          <div class="section-title-text">基本信息</div>
          <button class="btn-collapse" type="button" @click="collapsed.basic = !collapsed.basic">
            {{ collapsed.basic ? '展开' : '收起' }}
          </button>
        </div>
        <div v-show="!collapsed.basic">
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">
              <span>任务名称</span>
              <span class="required">*</span>
            </label>
            <input
              v-model="formData.taskName"
              type="text"
              class="form-input"
              placeholder="例如：Excel界面速通"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <div class="form-label-row">
              <label class="form-label">
                <span>任务要求</span>
                <span class="required">*</span>
              </label>
              <button
                type="button"
                class="btn-inline"
                @click="handleGenerateRequirements"
                :disabled="generatingRequirements || !formData.taskName.trim()"
              >
                {{ generatingRequirements ? '生成中...' : '✨ AI 生成任务要求' }}
              </button>
            </div>
            <p class="form-hint">
              请详细描述任务的教学目标、适用对象、学习要求等，AI将根据这些信息生成结构化的实验指导书。
            </p>
            <textarea
              v-model="formData.requirements"
              class="form-textarea"
              rows="6"
              placeholder="例如：&#10;1. 认识Excel的界面布局（功能区、单元格、工作表等）&#10;2. 掌握10个最常用Excel操作&#10;3. 理解单元格引用的概念&#10;4. 能够对数据进行筛选和排序&#10;5. 能够向AI快速学习Excel操作"
            ></textarea>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">
              <span>任务时长</span>
            </label>
            <input
              v-model="formData.duration"
              type="text"
              class="form-input"
              placeholder="例如：2学时（90分钟）"
            />
          </div>
        </div>
        </div>
      </div>

      <!-- 生成按钮 -->
      <div class="action-section">
        <div class="section-header section-header-center">
          <div class="section-title-text">教案生成</div>
          <button class="btn-collapse" type="button" @click="collapsed.generate = !collapsed.generate">
            {{ collapsed.generate ? '展开' : '收起' }}
          </button>
        </div>
        <div v-show="!collapsed.generate" class="action-body">
        <button
          class="btn-generate"
          @click="handleGenerate"
          :disabled="!canGenerate || generating"
        >
          {{ generating ? '生成中...' : '✨ 生成教案' }}
        </button>
        </div>
      </div>

      <!-- 数据文件生成 -->
      <div class="data-file-section">
        <div class="data-file-header section-header">
          <div>
            <h4>📊 根据教案自动生成示例数据文件</h4>
            <p class="data-file-subtitle">
              大模型会根据上方的任务要求，生成可用于课堂训练或实验的数据集，并下载为本地文件。
            </p>
          </div>
          <button class="btn-collapse" type="button" @click="collapsed.dataFile = !collapsed.dataFile">
            {{ collapsed.dataFile ? '展开' : '收起' }}
          </button>
        </div>
        <div v-show="!collapsed.dataFile">
        <div class="data-file-controls">
          <label class="data-file-label">数据文件格式：</label>
          <select v-model="dataFileFormat" class="data-file-select">
            <option value="csv">CSV（推荐，用于表格与数据分析）</option>
            <option value="json">JSON（用于编程与接口练习）</option>
            <option value="txt">TXT（自由文本或日志类数据）</option>
          </select>
          <button
            class="btn-data-file"
            type="button"
            @click="handleGenerateDataFile"
            :disabled="generatingDataFile || !generatedContent"
          >
            {{ generatingDataFile ? '生成数据中...' : '✨ 生成数据文件' }}
          </button>
          <button
            class="btn-data-secondary"
            type="button"
            @click="handleOpenDataFile"
            :disabled="!lastDataFileUrl || generatingDataFile"
          >
            浏览数据
          </button>
          <button
            class="btn-data-secondary"
            type="button"
            @click="handleInsertDataFileLink"
            :disabled="!lastDataFileUrl"
          >
            关联到教案
          </button>
        </div>
        <div class="data-file-extra">
          <label class="data-file-label">附加数据生成要求（可选）：</label>
          <textarea
            v-model="dataExtraRequirements"
            class="data-extra-textarea"
            placeholder="例如：&#10;- 需要生成 200 行数据，每一行代表一位学生的消费记录&#10;- 时间范围为最近 6 个月&#10;- 至少包含 3 类异常值（缺失、重复、极端值）&#10;- 控制文件大小不超过 1MB 等"
          ></textarea>
        </div>
        </div>
      </div>

      <!-- 生成日志 -->
      <div v-if="logs.length > 0 || streamText" class="log-section">
        <div class="log-header section-header">
          <span class="section-title-text">生成日志</span>
          <button class="btn-collapse" type="button" @click="collapsed.logs = !collapsed.logs">
            {{ collapsed.logs ? '展开' : '收起' }}
          </button>
        </div>
        <div v-show="!collapsed.logs">
        <div v-if="streamText" class="log-stream">
          <textarea
            class="log-stream-textarea"
            :value="streamText"
            readonly
          ></textarea>
        </div>
        <div class="log-content">
          <div
            v-for="(log, index) in logs"
            :key="index"
            class="log-item"
            :class="log.type"
          >
            <span class="log-time">{{ log.time }}</span>
            <span class="log-message" v-html="formatLogMessage(log.message)"></span>
          </div>
        </div>
        </div>
      </div>

      <!-- 生成结果 -->
      <div v-if="generatedContent" class="result-section">
        <div class="result-header section-header">
          <h4>生成的教案内容</h4>
          <div class="result-actions">
            <button class="btn-copy" @click="handleCopy">📋 复制</button>
            <button class="btn-apply" @click="handleApply">✅ 应用到编辑器</button>
            <button class="btn-collapse" type="button" @click="collapsed.result = !collapsed.result">
              {{ collapsed.result ? '展开' : '收起' }}
            </button>
          </div>
        </div>
        <div v-show="!collapsed.result" class="result-content">
          <pre class="md-preview">{{ generatedContent }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { aiAssistantApi } from '../api/aiAssistant'

interface Template {
  id: string
  name: string
  description: string
  icon: string
}

interface FormData {
  taskName: string
  requirements: string
  duration: string
}

const props = defineProps<{
  levelName?: string
  levelDescription?: string
}>()

const emit = defineEmits<{
  generated: [content: string]
  insertDataLink: [url: string]
}>()

const templates: Template[] = [
  {
    id: 'standard',
    name: '标准实验指导书',
    description: '包含学习目标、操作步骤、课堂问答、作业要求等完整结构',
    icon: '📚'
  },
  {
    id: 'simple',
    name: '简化版指导书',
    description: '精简版，适合快速上手的简单任务',
    icon: '📝'
  },
  {
    id: 'detailed',
    name: '详细版指导书',
    description: '包含更多细节和扩展内容，适合复杂任务',
    icon: '📖'
  }
]

const selectedTemplate = ref<string>('standard')
const formData = ref<FormData>({
  taskName: props.levelName || '',
  requirements: '',
  duration: '2学时（90分钟）'
})

// 面板常驻（v-show）时，levelName 可能在组件初始化后才加载完成；
// 这里仅在“首次拿到有效 levelName 且任务名称为空”时自动回填一次，避免覆盖用户输入。
const taskNameAutoFilled = ref(false)
watch(
  () => props.levelName,
  (val) => {
    if (taskNameAutoFilled.value) return
    const name = (val || '').trim()
    if (!name) return
    if (formData.value.taskName.trim()) return
    formData.value.taskName = name
    taskNameAutoFilled.value = true
  },
  { immediate: true }
)

const collapsed = ref({
  template: false,
  basic: false,
  generate: false,
  dataFile: false,
  logs: false,
  result: false,
})

const generating = ref(false)
const logs = ref<Array<{ time: string; type: string; message: string }>>([])
const generatedContent = ref('')
const generatingRequirements = ref(false)
const streamText = ref('')
const dataFileFormat = ref<'csv' | 'json' | 'txt'>('csv')
const generatingDataFile = ref(false)
const lastDataFileUrl = ref('')
const lastDataFileName = ref('')
const dataExtraRequirements = ref('')

const canGenerate = computed(() => {
  return formData.value.taskName.trim() !== '' && formData.value.requirements.trim() !== ''
})

const formatLogMessage = (message: string): string => {
  return message.replace(/\n/g, '<br>')
}

const handleGenerate = async () => {
  if (!canGenerate.value || generating.value) return

  generating.value = true
  logs.value = []
  generatedContent.value = ''
  streamText.value = ''

  try {
    const template = templates.find(t => t.id === selectedTemplate.value)
    const prompt = buildPrompt(template!)

    logs.value.push({
      time: new Date().toLocaleTimeString(),
      type: 'info',
      message: '开始生成教案...'
    })

    const apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
    const baseURL = apiBaseURL.endsWith('/') ? apiBaseURL.slice(0, -1) : apiBaseURL
    const url = `${baseURL}/ai-assistant/generate-teaching-guide-stream`

    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('未登录或登录已失效，请重新登录后再试')
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        task_name: formData.value.taskName,
        requirements: formData.value.requirements,
        duration: formData.value.duration,
        template_type: selectedTemplate.value,
        prompt,
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
            logs.value.push({
              time: new Date().toLocaleTimeString(),
              type: 'info',
              message: data.message || '开始生成 ...'
            })
          } else if (data.type === 'content') {
            const chunk: string = data.content || ''
            if (chunk) {
              streamText.value += chunk
            }
          } else if (data.type === 'result') {
            const content: string = data.content || ''
            generatedContent.value = content
            logs.value.push({
              time: new Date().toLocaleTimeString(),
              type: 'success',
              message: '教案生成完成！'
            })
          } else if (data.type === 'error') {
            const msg: string = data.message || '生成教案失败'
            logs.value.push({
              time: new Date().toLocaleTimeString(),
              type: 'error',
              message: `生成失败：${msg}`
            })
          }
        } catch (e) {
          console.error('解析生成教案 SSE 消息失败:', e, line)
        }
      }
    }
  } catch (err: any) {
    logs.value.push({
      time: new Date().toLocaleTimeString(),
      type: 'error',
      message: `生成失败：${err.response?.data?.detail || err.message || '未知错误'}`
    })
    console.error('Error generating teaching guide:', err)
  } finally {
    generating.value = false
  }
}

const handleGenerateRequirements = async () => {
  if (!formData.value.taskName.trim() || generatingRequirements.value) return

  generatingRequirements.value = true
  streamText.value = ''

  try {
    logs.value.push({
      time: new Date().toLocaleTimeString(),
      type: 'info',
      message: '开始生成任务要求...'
    })

    const apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
    const baseURL = apiBaseURL.endsWith('/') ? apiBaseURL.slice(0, -1) : apiBaseURL
    const url = `${baseURL}/ai-assistant/generate-teaching-requirements-stream`

    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('未登录或登录已失效，请重新登录后再试')
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        task_name: formData.value.taskName,
        template_type: selectedTemplate.value
      })
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
            // 已在前面写了一条开始日志，这里可以忽略或补充信息
            continue
          } else if (data.type === 'content') {
            const chunk: string = data.content || ''
            if (chunk) {
              streamText.value += chunk
            }
          } else if (data.type === 'result') {
            const requirements: string = data.requirements || ''
            if (requirements) {
              formData.value.requirements = requirements
            }
            logs.value.push({
              time: new Date().toLocaleTimeString(),
              type: 'success',
              message: '任务要求生成完成，请根据实际教学情况进行修改。'
            })
          } else if (data.type === 'error') {
            const msg: string = data.message || '任务要求生成失败'
            logs.value.push({
              time: new Date().toLocaleTimeString(),
              type: 'error',
              message: `任务要求生成失败：${msg}`
            })
          }
        } catch (e) {
          console.error('解析任务要求 SSE 消息失败:', e, line)
        }
      }
    }
  } catch (err: any) {
    console.error('Error generating teaching requirements:', err)
    logs.value.push({
      time: new Date().toLocaleTimeString(),
      type: 'error',
      message: `任务要求生成失败：${err.response?.data?.detail || err.message || '未知错误'}`
    })
  } finally {
    generatingRequirements.value = false
  }
}

const handleGenerateDataFile = async () => {
  if (generatingDataFile.value) return

  // 必须先生成教案（generatedContent）才能生成数据文件
  if (!generatedContent.value.trim()) {
    alert('请先点击「生成教案」，在教案生成完成后再生成数据文件。')
    return
  }

  generatingDataFile.value = true
  // 清空之前的数据流文本，单独看本次生成过程
  streamText.value = ''

  try {
    logs.value.push({
      time: new Date().toLocaleTimeString(),
      type: 'info',
      message: '开始根据当前教案内容生成示例数据文件...'
    })

    const apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
    const baseURL = apiBaseURL.endsWith('/') ? apiBaseURL.slice(0, -1) : apiBaseURL
    const url = `${baseURL}/ai-assistant/generate-data-file-stream`

    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('未登录或登录已失效，请重新登录后再试')
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        task_name: formData.value.taskName,
        // 使用已经生成的 Markdown 教案内容驱动数据生成
        data_requirements:
          generatedContent.value +
          (dataExtraRequirements.value.trim()
            ? `\n\n【附加数据生成要求】\n${dataExtraRequirements.value.trim()}`
            : ''),
        file_format: dataFileFormat.value
      })
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
    let finalFileUrl = ''
    let finalFilename = ''

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
            // 开始提示已经写入日志，可忽略
            continue
          } else if (data.type === 'content') {
            const chunk: string = data.content || ''
            if (chunk) {
              streamText.value += chunk
            }
          } else if (data.type === 'result') {
            finalFilename = data.filename || ''
            finalFileUrl = data.url || ''
          } else if (data.type === 'error') {
            const msg: string = data.message || '生成数据文件失败'
            logs.value.push({
              time: new Date().toLocaleTimeString(),
              type: 'error',
              message: `生成数据文件失败：${msg}`
            })
          }
        } catch (e) {
          console.error('解析生成数据文件 SSE 消息失败:', e, line)
        }
      }
    }

    if (finalFilename && finalFileUrl) {
      lastDataFileName.value = finalFilename
      lastDataFileUrl.value = finalFileUrl
      logs.value.push({
        time: new Date().toLocaleTimeString(),
        type: 'success',
        message: `数据文件生成完成，可在教案中通过链接访问：${finalFileUrl}`
      })
    }
  } catch (err: any) {
    console.error('Error generating data file:', err)
    logs.value.push({
      time: new Date().toLocaleTimeString(),
      type: 'error',
      message: `生成数据文件失败：${err.response?.data?.detail || err.message || '未知错误'}`
    })
  } finally {
    generatingDataFile.value = false
  }
}

const handleOpenDataFile = () => {
  if (!lastDataFileUrl.value) return
  window.open(lastDataFileUrl.value, '_blank')
}

const handleInsertDataFileLink = () => {
  if (!lastDataFileUrl.value) return
  emit('insertDataLink', lastDataFileUrl.value)
}

const buildPrompt = (template: Template): string => {
  const basePrompt = `请生成一份结构化的实验指导书（Markdown格式），要求如下：

## 基本信息
- 任务名称：${formData.value.taskName}
${formData.value.duration ? `- 任务时长：${formData.value.duration}` : ''}

## 任务要求
${formData.value.requirements}

## 生成要求
请按照以下结构生成Markdown格式的实验指导书：

1. **标题**：使用 # 任务名称
2. **学习目标**：包含知识目标、技能目标、素养目标
3. **任务时间**：总时长和建议分配
4. **准备工作**：必备工具列表
5. **操作步骤**：
   - 每个步骤包含标题和时间
   - 详细的操作方法（使用代码块格式）
   - "立即动手"练习任务
   - "课堂问答"部分（包含问题、选项、正确答案、解析）
6. **作业要求**：提交内容和文件命名规范
7. **常见问题**：Q&A格式
8. **学习提示**：学习建议
9. **自我检查**：检查清单

请确保：
- 使用清晰的Markdown格式
- 操作步骤详细且易于理解
- 包含适当的课堂问答题目
- 语言通俗易懂，适合初学者
`

  if (template.id === 'detailed') {
    return basePrompt + '\n\n请生成更详细的内容，包含更多操作示例和扩展知识。'
  } else if (template.id === 'simple') {
    return basePrompt + '\n\n请生成精简版内容，保留核心要点即可。'
  }

  return basePrompt
}

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(generatedContent.value)
    logs.value.push({
      time: new Date().toLocaleTimeString(),
      type: 'success',
      message: '已复制到剪贴板'
    })
  } catch (err) {
    console.error('Failed to copy:', err)
    logs.value.push({
      time: new Date().toLocaleTimeString(),
      type: 'error',
      message: '复制失败，请手动复制'
    })
  }
}

const handleApply = () => {
  if (generatedContent.value) {
    emit('generated', generatedContent.value)
  }
}
</script>

<style scoped>
.teaching-guide-assistant {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0.5rem;
  box-sizing: border-box;
}
.assistant-header {
  margin-bottom: 1rem;
}
.assistant-header h3 {
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
}
.subtitle {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}
.assistant-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.template-section,
.form-section,
.data-file-section,
.log-section,
.result-section {
  padding: 1.25rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}
.section-title-text {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #374151;
}
.btn-collapse {
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #374151;
  font-size: 0.75rem;
  cursor: pointer;
}
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}
.template-card {
  padding: 1rem;
  background: #ffffff;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}
.template-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}
.template-card.active {
  border-color: #3b82f6;
  background: #eff6ff;
}
.template-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.form-row { margin-bottom: 1.25rem; display:block; }
.form-group { width:100%; margin-bottom:1rem; }
.form-label { display:block; margin-bottom:0.75rem; font-weight:600; color:#374151; }
.form-input, .form-textarea, .data-extra-textarea {
  width:100%;
  padding:0.75rem;
  border:1px solid #d1d5db;
  border-radius:8px;
  background:#ffffff;
  box-sizing:border-box;
  font-family:inherit;
}
.form-textarea { min-height:120px; resize:vertical; }
.action-section .btn-generate {
  padding:0.875rem 2rem;
  background: linear-gradient(135deg,#3b82f6 0%,#2563eb 100%);
  color:#fff;
  border:none;
  border-radius:8px;
  cursor:pointer;
  font-weight:600;
}
.action-section .btn-generate:disabled { opacity:0.6; cursor:not-allowed; }
.data-file-controls { display:flex; flex-wrap:wrap; gap:0.5rem; align-items:center; }
.data-file-select { min-width:180px; padding:0.4rem 0.6rem; border-radius:6px; border:1px solid #d1d5db; }
.btn-data-file { padding:0.45rem 0.95rem; border-radius:999px; background:#0ea5e9; color:#fff; border:none; cursor:pointer;}
.btn-data-secondary { padding:0.35rem 0.8rem; border-radius:6px; border:none; background:#eef2ff; cursor:pointer; }
.log-section .log-stream-textarea { width:100%; min-height:120px; background:#111827; color:#e5e7eb; border-radius:6px; padding:0.75rem; border:1px solid #222; }
.log-content { display:flex; flex-direction:column; gap:0.5rem; }
.log-item { padding:0.625rem; border-radius:6px; font-size:0.875rem; display:flex; gap:0.75rem; }
.log-item.info { background: rgba(59,130,246,0.08); color:#2563eb; }
.log-item.success { background: rgba(34,197,94,0.12); color:#16a34a; font-weight:600; }
.log-item.error { background: rgba(239,68,68,0.08); color:#dc2626; }
.result-section .md-preview { background:#f9fafb; padding:1rem; border-radius:6px; white-space:pre-wrap; font-family:Consolas,monospace; }
.btn-inline { display:inline-flex; align-items:center; padding:0.25rem 0.75rem; border-radius:999px; background:#2563eb; color:#fff; border:none; cursor:pointer; }
.btn-copy, .btn-apply { padding:0.5rem 1rem; border-radius:6px; border:none; cursor:pointer; }
.btn-copy { background:#f3f4f6; color:#374151; border:1px solid #d1d5db; }
.btn-apply { background:#3b82f6; color:#fff; }
@media (max-width:768px) {
  .template-grid { grid-template-columns: 1fr; }
  .data-file-controls { flex-direction:column; align-items:stretch; }
}
</style>

