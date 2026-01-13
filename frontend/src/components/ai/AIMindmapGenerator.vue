<template>
  <div class="modal-overlay">
    <div 
      class="modal-content"
      :class="{ dragging: isDragging }"
      :style="{ transform: `translate(${position.x}px, ${position.y}px)` }"
      @mousedown="handleMouseDown"
    >
      <div class="modal-header" @mousedown.stop="handleHeaderMouseDown">
        <h3>课程智能设计</h3>
        <button class="btn-close-header" @click="handleCancel" :disabled="generating || generatingSyllabus" title="关闭">
          ×
        </button>
      </div>
      
      <!-- 选项卡 -->
      <div class="tabs">
        <button 
          class="tab-item" 
          :class="{ active: activeTab === 'syllabus' }"
          @click="activeTab = 'syllabus'"
        >
          生成教学大纲
        </button>
        <button 
          class="tab-item" 
          :class="{ active: activeTab === 'mindmap' }"
          @click="activeTab = 'mindmap'"
        >
          生成思维导图
        </button>
      </div>
      
      <div class="modal-body">
        <!-- 生成思维导图选项卡 -->
        <div v-if="activeTab === 'mindmap' && !generating" class="form-section">
          <label class="form-label">
            <span>教学大纲</span>
            <span class="required">*</span>
          </label>
          <p class="form-hint">请输入完整的教学大纲内容，AI将自动解析知识点并生成层次化的思维导图</p>
          <textarea
            v-model="syllabus"
            class="syllabus-input"
            rows="10"
            placeholder="例如：&#10;第一章：Excel基础&#10;  1.1 Excel界面介绍&#10;  1.2 单元格操作&#10;  1.3 数据输入&#10;&#10;第二章：Excel函数&#10;  2.1 常用函数&#10;  2.2 函数嵌套&#10;  2.3 数组公式&#10;&#10;..."
          ></textarea>

          <div class="instructions-section">
            <label class="form-label">
              <span>生成规则 / 自然语言命令</span>
              <span class="optional">可选</span>
            </label>
            <p class="form-hint">
              可以用自然语言告诉 AI 如何组织思维导图，例如按照章节、知识类型或难度分层归类。
            </p>
            <textarea
              v-model="instructions"
              class="instructions-input"
              rows="4"
              placeholder="示例：&#10;• 按“基础操作 / 进阶技巧 / 综合应用”三大类分组；&#10;• 每一类内部再按“先易后难”的顺序排布；&#10;• 把练习题和综合项目放在最后一层；&#10;• 每个节点名称尽量简短，突出关键词。"
            ></textarea>
          </div>
        </div>
        
        <!-- 生成教学大纲选项卡 -->
        <div v-if="activeTab === 'syllabus' && !generatingSyllabus" class="form-section">
          <label class="form-label">
            <span>课程名称</span>
            <span class="required">*</span>
          </label>
          <p class="form-hint">请输入课程名称，AI将根据课程名称和要求生成完整的教学大纲</p>
          <input
            v-model="courseName"
            type="text"
            class="form-input"
            placeholder="例如：Excel数据分析基础"
          />

          <div class="instructions-section" style="margin-top: 1.5rem;">
            <label class="form-label">
              <span>课程要求</span>
              <span class="required">*</span>
            </label>
            <p class="form-hint">
              请详细描述课程的教学目标、适用对象、学习要求等，AI将根据这些信息生成结构化的教学大纲。
            </p>
            <textarea
              v-model="courseRequirements"
              class="instructions-input"
              rows="8"
              placeholder="例如：&#10;• 教学目标：掌握Excel基础操作和常用函数，能够进行数据分析和处理&#10;• 适用对象：零基础学员，需要具备基本的计算机操作能力&#10;• 学习要求：完成所有章节的学习，完成课后练习和综合项目&#10;• 课程时长：预计30学时&#10;• 重点内容：函数使用、数据透视表、图表制作等"
            ></textarea>
          </div>
        </div>

        <!-- 生成教学大纲结果展示 -->
        <div v-if="activeTab === 'syllabus' && generatedSyllabus" class="syllabus-result">
          <div class="result-header">
            <h4>生成的教学大纲</h4>
            <div class="result-actions">
              <button class="btn-copy" @click="copySyllabus" :disabled="copying">
                {{ copying ? '复制中...' : '📋 复制' }}
              </button>
              <button class="btn-send" @click="sendToMindmap">
                发送到思维导图
              </button>
            </div>
          </div>
          <div class="syllabus-content">
            <pre>{{ generatedSyllabus }}</pre>
          </div>
        </div>

        <!-- 生成教学大纲中状态 -->
        <div v-if="activeTab === 'syllabus' && generatingSyllabus" class="generating-state">
          <div class="progress-section">
            <div class="progress-header">
              <h4>生成进度</h4>
              <span class="progress-percent">{{ syllabusProgress }}%</span>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar" :style="{ width: syllabusProgress + '%' }"></div>
            </div>
          </div>
          
          <div class="log-section">
            <div class="log-header">
              <h4>AI生成日志</h4>
              <button class="btn-clear-log" @click="clearLog" title="清空日志">清空</button>
            </div>
            <div class="log-content" ref="logContentRef">
              <div 
                v-for="(log, index) in logs" 
                :key="index" 
                class="log-item"
                :class="log.type"
              >
                <span class="log-time">{{ log.time }}</span>
                <span class="log-message" v-html="formatLogMessage(log.message)"></span>
              </div>
              <div v-if="logs.length === 0" class="log-empty">等待AI响应...</div>
            </div>
          </div>
        </div>

        <!-- 生成思维导图中状态 -->
        <div v-if="activeTab === 'mindmap' && generating" class="generating-state">
          <!-- 进度条 -->
          <div class="progress-section">
            <div class="progress-header">
              <h4>生成进度</h4>
              <span class="progress-percent">{{ progress }}%</span>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar" :style="{ width: progress + '%' }"></div>
            </div>
          </div>
          
          <!-- 日志框 -->
          <div class="log-section">
            <div class="log-header">
              <h4>AI生成日志</h4>
              <button class="btn-clear-log" @click="clearLog" title="清空日志">清空</button>
            </div>
            <div class="log-content" ref="logContentRef">
              <div 
                v-for="(log, index) in logs" 
                :key="index" 
                class="log-item"
                :class="log.type"
              >
                <span class="log-time">{{ log.time }}</span>
                <span class="log-message" v-html="formatLogMessage(log.message)"></span>
              </div>
              <div v-if="logs.length === 0" class="log-empty">等待AI响应...</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button 
          v-if="activeTab === 'mindmap'"
          type="button" 
          class="btn-primary" 
          @click="handleGenerate" 
          :disabled="!canGenerate || generating"
        >
          {{ generating ? '生成中...' : '生成思维导图' }}
        </button>
        <button 
          v-if="activeTab === 'syllabus'"
          type="button" 
          class="btn-primary" 
          @click="handleGenerateSyllabus" 
          :disabled="!canGenerateSyllabus || generatingSyllabus"
        >
          {{ generatingSyllabus ? '生成中...' : '生成教学大纲' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
// import apiClient from '../api/http' // 暂时不需要

interface Props {
  chapterName?: string
  chapterDescription?: string
}

interface LogItem {
  type: 'info' | 'content' | 'error' | 'success'
  message: string
  time: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  generated: [mindmapData: any]
}>()

const activeTab = ref<'mindmap' | 'syllabus'>('syllabus')
const syllabus = ref('')
const instructions = ref('')
const courseName = ref('')
const courseRequirements = ref('')
const generating = ref(false)
const generatingSyllabus = ref(false)
const generatedSyllabus = ref('')
const copying = ref(false)
const position = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const progress = ref(0)
const syllabusProgress = ref(0)
const logs = ref<LogItem[]>([])
const logContentRef = ref<HTMLElement | null>(null)
let eventSource: EventSource | null = null

// 初始化位置（居中）
const initPosition = () => {
  position.value = { x: 0, y: 0 }
}

const canGenerate = computed(() => {
  return syllabus.value.trim().length > 0
})

const canGenerateSyllabus = computed(() => {
  return courseName.value.trim().length > 0 && courseRequirements.value.trim().length > 0
})

const addLog = (type: LogItem['type'], message: string) => {
  const now = new Date()
  const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  logs.value.push({
    type,
    message,
    time: timeStr
  })
  
  // 自动滚动到底部
  nextTick(() => {
    if (logContentRef.value) {
      logContentRef.value.scrollTop = logContentRef.value.scrollHeight
    }
  })
}

const clearLog = () => {
  logs.value = []
}

const formatLogMessage = (message: string) => {
  // 转义HTML，但保留换行
  return message
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
}

const handleHeaderMouseDown = (e: MouseEvent) => {
  if (generating.value) return
  
  isDragging.value = true
  dragStart.value = {
    x: e.clientX - position.value.x,
    y: e.clientY - position.value.y
  }
  
  const handleMouseMove = (e: MouseEvent) => {
    if (isDragging.value) {
      let newX = e.clientX - dragStart.value.x
      let newY = e.clientY - dragStart.value.y
      
      const maxX = window.innerWidth / 2 - 350
      const maxY = window.innerHeight / 2 - 45
      const minX = -window.innerWidth / 2 + 350
      const minY = -window.innerHeight / 2 + 45
      
      newX = Math.max(minX, Math.min(maxX, newX))
      newY = Math.max(minY, Math.min(maxY, newY))
      
      position.value = { x: newX, y: newY }
    }
  }
  
  const handleMouseUp = () => {
    isDragging.value = false
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const handleMouseDown = (e: MouseEvent) => {
  e.stopPropagation()
}

const handleCancel = () => {
  if (generating.value || generatingSyllabus.value) {
    // 取消流式请求
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
    generating.value = false
    generatingSyllabus.value = false
    progress.value = 0
    syllabusProgress.value = 0
    logs.value = []
  } else {
    emit('close')
  }
}

const handleGenerate = async () => {
  if (!canGenerate.value || generating.value) return
  
  generating.value = true
  progress.value = 0
  logs.value = []
  
  addLog('info', '🚀 开始生成思维导图...')
  addLog('info', `📝 教学大纲长度: ${syllabus.value.trim().length} 字符`)
  
  try {
    // 使用fetch接收流式数据
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('未登录')
    }
    
    // 使用统一的API配置（与http.ts保持一致）
    // http.ts中的baseURL是 'http://127.0.0.1:8000/api/v1'，所以这里也需要保持一致
    const apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
    // 确保URL格式正确
    const baseURL = apiBaseURL.endsWith('/') ? apiBaseURL.slice(0, -1) : apiBaseURL
    const url = `${baseURL}/ai-assistant/generate-mindmap`
    
    addLog('info', `🔗 连接地址: ${url}`)
    
    // 使用fetch进行流式请求
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        syllabus: syllabus.value.trim(),
        chapter_name: props.chapterName,
        description: props.chapterDescription,
        extra_instructions: instructions.value.trim() || undefined,
        stream: true
      })
    })
    
    if (!response.ok) {
      let errorDetail = `HTTP错误 ${response.status}`
      try {
        const errorText = await response.text()
        const errorJson = JSON.parse(errorText)
        errorDetail = errorJson.detail || errorDetail
      } catch {
        // 忽略解析错误，使用默认错误信息
      }
      throw new Error(errorDetail)
    }
    
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let fullContent = ''
    
    if (!reader) {
      throw new Error('无法读取流式数据')
    }
    
    addLog('info', '✅ 已连接到AI服务，开始接收数据...')
    progress.value = 10
    
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // 保留最后一个不完整的行
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const dataStr = line.slice(6)
            if (dataStr.trim() === '') continue
            
            const data = JSON.parse(dataStr)
            
            if (data.type === 'start') {
              addLog('info', `📌 ${data.message}`)
              progress.value = 20
            } else if (data.type === 'content') {
              fullContent += data.content
              addLog('content', data.content)
              // 根据内容长度估算进度（20-90%）
              const estimatedProgress = Math.min(20 + Math.floor((fullContent.length / 1000) * 70), 90)
              progress.value = estimatedProgress
            } else if (data.type === 'result') {
              progress.value = 100
              addLog('success', '✅ 思维导图生成完成！')
              addLog('info', '📊 正在解析结果...')
              
              // 延迟一下再发送结果，让用户看到完成消息
              setTimeout(() => {
                emit('generated', {
                  syllabus: syllabus.value.trim(),
                  chapter_name: props.chapterName,
                  description: props.chapterDescription,
                  result: data.data
                })
              }, 500)
              return
            } else if (data.type === 'error') {
              progress.value = 0
              addLog('error', `❌ 错误: ${data.message}`)
              generating.value = false
              return
            }
          } catch (e) {
            console.error('解析SSE数据失败:', e, line)
          }
        }
      }
    }
    
    // 如果没有收到result消息，尝试解析完整内容
    if (fullContent) {
      try {
        addLog('info', '📊 正在解析AI返回的内容...')
        progress.value = 95
        
        // 清理可能的markdown代码块
        let cleaned = fullContent.trim()
        if (cleaned.startsWith('```json')) {
          cleaned = cleaned.slice(7)
        }
        if (cleaned.startsWith('```')) {
          cleaned = cleaned.slice(3)
        }
        if (cleaned.endsWith('```')) {
          cleaned = cleaned.slice(0, -3)
        }
        cleaned = cleaned.trim()
        
        const result = JSON.parse(cleaned)
        progress.value = 100
        addLog('success', '✅ 思维导图生成完成！')
        
        setTimeout(() => {
          emit('generated', {
            syllabus: syllabus.value.trim(),
            chapter_name: props.chapterName,
            description: props.chapterDescription,
            result: result
          })
        }, 500)
      } catch (e) {
        addLog('error', `❌ 解析结果失败: ${e}`)
        generating.value = false
      }
    } else {
      addLog('error', '❌ 未收到有效数据')
      generating.value = false
    }
  } catch (err: any) {
    progress.value = 0
    let errorMessage = '未知错误'
    
    if (err.message) {
      if (err.message.includes('Failed to fetch') || err.message.includes('ERR_CONNECTION_REFUSED')) {
        errorMessage = '❌ 无法连接到后端服务器，请确保后端服务正在运行'
      } else if (err.message.includes('未登录')) {
        errorMessage = '❌ 未登录，请先登录'
      } else {
        errorMessage = `❌ ${err.message}`
      }
    }
    
    addLog('error', errorMessage)
    console.error('Error generating mindmap:', err)
    generating.value = false
  }
}

// 监听生成状态，自动滚动日志
watch(generating, (newVal) => {
  if (newVal) {
    nextTick(() => {
      if (logContentRef.value) {
        logContentRef.value.scrollTop = logContentRef.value.scrollHeight
      }
    })
  }
})

// 初始化位置
onMounted(() => {
  initPosition()
})

// 生成教学大纲
const handleGenerateSyllabus = async () => {
  if (!canGenerateSyllabus.value || generatingSyllabus.value) return
  
  generatingSyllabus.value = true
  syllabusProgress.value = 0
  logs.value = []
  generatedSyllabus.value = ''
  
  addLog('info', '🚀 开始生成教学大纲...')
  addLog('info', `📝 课程名称: ${courseName.value}`)
  
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('未登录')
    }
    
    const apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
    const baseURL = apiBaseURL.endsWith('/') ? apiBaseURL.slice(0, -1) : apiBaseURL
    const url = `${baseURL}/ai-assistant/generate-syllabus`
    
    addLog('info', '🔗 连接AI服务...')
    syllabusProgress.value = 10
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        course_name: courseName.value.trim(),
        course_requirements: courseRequirements.value.trim(),
        stream: true
      })
    })
    
    if (!response.ok) {
      let errorDetail = `HTTP错误 ${response.status}`
      try {
        const errorText = await response.text()
        const errorJson = JSON.parse(errorText)
        errorDetail = errorJson.detail || errorDetail
      } catch {
        // 忽略解析错误
      }
      throw new Error(errorDetail)
    }
    
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let fullContent = ''
    
    if (!reader) {
      throw new Error('无法读取流式数据')
    }
    
    addLog('info', '✅ 已连接到AI服务，开始接收数据...')
    syllabusProgress.value = 20
    
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const dataStr = line.slice(6)
            if (dataStr.trim() === '') continue
            
            const data = JSON.parse(dataStr)
            
            if (data.type === 'start') {
              addLog('info', `📌 ${data.message}`)
              syllabusProgress.value = 30
            } else if (data.type === 'content') {
              fullContent += data.content
              addLog('content', data.content)
              const estimatedProgress = Math.min(30 + Math.floor((fullContent.length / 2000) * 60), 90)
              syllabusProgress.value = estimatedProgress
            } else if (data.type === 'result') {
              syllabusProgress.value = 100
              generatedSyllabus.value = data.data || fullContent
              addLog('success', '✅ 教学大纲生成完成！')
              generatingSyllabus.value = false
              return
            } else if (data.type === 'error') {
              syllabusProgress.value = 0
              addLog('error', `❌ 错误: ${data.message}`)
              generatingSyllabus.value = false
              return
            }
          } catch (e) {
            console.error('解析SSE数据失败:', e, line)
          }
        }
      }
    }
    
    // 如果没有收到result消息，使用完整内容
    if (fullContent) {
      generatedSyllabus.value = fullContent.trim()
      syllabusProgress.value = 100
      addLog('success', '✅ 教学大纲生成完成！')
    } else {
      addLog('error', '❌ 未收到有效数据')
    }
    
    generatingSyllabus.value = false
  } catch (err: any) {
    syllabusProgress.value = 0
    let errorMessage = '未知错误'
    
    if (err.message) {
      if (err.message.includes('Failed to fetch') || err.message.includes('ERR_CONNECTION_REFUSED')) {
        errorMessage = '❌ 无法连接到后端服务器，请确保后端服务正在运行'
      } else if (err.message.includes('未登录')) {
        errorMessage = '❌ 未登录，请先登录'
      } else {
        errorMessage = `❌ ${err.message}`
      }
    }
    
    addLog('error', errorMessage)
    console.error('Error generating syllabus:', err)
    generatingSyllabus.value = false
  }
}

// 复制教学大纲
const copySyllabus = async () => {
  if (!generatedSyllabus.value) return
  
  copying.value = true
  try {
    await navigator.clipboard.writeText(generatedSyllabus.value)
    addLog('success', '✅ 教学大纲已复制到剪贴板')
    setTimeout(() => {
      copying.value = false
    }, 1000)
  } catch (err) {
    addLog('error', '❌ 复制失败，请手动复制')
    copying.value = false
  }
}

// 发送教学大纲到思维导图页面
const sendToMindmap = () => {
  if (!generatedSyllabus.value) return
  
  // 切换到思维导图选项卡
  activeTab.value = 'mindmap'
  // 将生成的教学大纲填入输入框
  syllabus.value = generatedSyllabus.value
  // 清空生成的教学大纲，以便重新生成
  generatedSyllabus.value = ''
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
  display: flex;
  flex-direction: column;
  position: relative;
  cursor: default;
  transition: transform 0.1s ease-out;
}

.modal-content.dragging {
  cursor: move;
  transition: none;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  background: #ffffff;
  cursor: move;
  user-select: none;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-header::before {
  content: '⋮⋮';
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  font-size: 1rem;
  letter-spacing: -2px;
  opacity: 0.4;
}

.modal-header h3 {
  margin: 0;
  margin-left: 1.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  letter-spacing: 0.5px;
  flex: 1;
}

.btn-close-header {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: all 0.2s ease;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: -0.5rem;
}

.btn-close-header:hover:not(:disabled) {
  background: #f3f4f6;
  color: #374151;
}

.btn-close-header:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 选项卡样式 */
.tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  background: #ffffff;
  padding: 0 1.5rem;
  gap: 0.5rem;
}

.tab-item {
  padding: 0.75rem 1.25rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 0.9375rem;
  font-weight: 500;
  color: #6b7280;
  transition: all 0.2s ease;
  position: relative;
  margin-bottom: -1px;
  border-radius: 6px 6px 0 0;
}

.tab-item:hover {
  color: #374151;
  background: #f3f4f6;
}

.tab-item.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
  background: #ffffff;
  font-weight: 600;
}

.modal-body {
  padding: 1.75rem 2rem;
  flex: 1;
  overflow-y: auto;
  background: #ffffff;
}

.form-section {
  margin-bottom: 0;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.625rem;
  font-weight: 600;
  font-size: 0.9375rem;
  color: #1f2937;
}

.required {
  color: #ef4444;
  font-size: 0.875rem;
}

.optional {
  color: #6b7280;
  font-size: 0.8125rem;
  font-weight: 400;
  margin-left: 0.25rem;
}

.form-hint {
  margin: 0 0 0.875rem;
  font-size: 0.8125rem;
  color: #6b7280;
  line-height: 1.5;
}

/* 表单输入框样式 */
.form-input {
  width: 100%;
  padding: 0.75rem 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.9375rem;
  transition: all 0.2s ease;
  background: #ffffff;
  color: #1f2937;
  box-sizing: border-box;
  font-family: inherit;
  line-height: 1.5;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input::placeholder {
  color: #9ca3af;
}

.syllabus-input,
.instructions-input {
  width: 100%;
  padding: 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.9375rem;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  line-height: 1.6;
  resize: vertical;
  transition: all 0.2s ease;
  background: #ffffff;
  color: #1f2937;
  box-sizing: border-box;
}

.syllabus-input {
  min-height: 280px;
}

.instructions-input {
  min-height: 120px;
}

.syllabus-input:focus,
.instructions-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.syllabus-input::placeholder,
.instructions-input::placeholder {
  color: #9ca3af;
}

/* 生成状态样式 */
.generating-state {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 进度条样式 */
.progress-section {
  background: #f9fafb;
  border-radius: 8px;
  padding: 1.25rem;
  border: 1px solid #e5e7eb;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.progress-header h4 {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #1f2937;
}

.progress-percent {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #3b82f6;
}

.progress-bar-container {
  width: 100%;
  height: 12px;
  background: #e2e8f0;
  border-radius: 6px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: #3b82f6;
  border-radius: 6px;
  transition: width 0.3s ease;
}

/* 日志框样式 */
.log-section {
  background: #1f2937;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #374151;
  display: flex;
  flex-direction: column;
  min-height: 280px;
  max-height: 380px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #334155;
}

.log-header h4 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #cbd5e1;
}

.btn-clear-log {
  padding: 0.25rem 0.75rem;
  background: rgba(102, 126, 234, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 6px;
  color: #cbd5e1;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear-log:hover {
  background: rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.5);
}

.log-content {
  flex: 1;
  overflow-y: auto;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.85rem;
  line-height: 1.6;
}

.log-item {
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
  display: flex;
  gap: 0.75rem;
}

.log-item.info {
  background: rgba(59, 130, 246, 0.1);
  color: #93c5fd;
}

.log-item.content {
  background: rgba(34, 197, 94, 0.1);
  color: #86efac;
}

.log-item.error {
  background: rgba(239, 68, 68, 0.1);
  color: #fca5a5;
}

.log-item.success {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
  font-weight: 600;
}

.log-time {
  color: #64748b;
  font-size: 0.75rem;
  flex-shrink: 0;
  min-width: 70px;
}

.log-message {
  flex: 1;
  word-break: break-word;
}

.log-empty {
  color: #64748b;
  text-align: center;
  padding: 2rem;
  font-style: italic;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 2rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9375rem;
  font-weight: 500;
  transition: all 0.2s ease;
  min-width: 140px;
  flex: 0 0 auto;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #9ca3af;
}

/* 指令部分样式 */
.instructions-section {
  margin-top: 1.5rem;
}

/* 教学大纲结果展示样式 */
.syllabus-result {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.result-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.result-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-copy,
.btn-send {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-copy {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-copy:hover:not(:disabled) {
  background: #e5e7eb;
  border-color: #9ca3af;
}

.btn-copy:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-send {
  background: #3b82f6;
  color: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.btn-send:hover {
  background: #2563eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.syllabus-content {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.25rem;
  max-height: 480px;
  overflow-y: auto;
}

.syllabus-content pre {
  margin: 0;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
  color: #1f2937;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>

