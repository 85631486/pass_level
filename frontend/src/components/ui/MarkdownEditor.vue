<template>
  <div class="markdown-editor" :class="{ fullscreen: isFullscreen }">
    <div class="editor-toolbar">
      <div class="toolbar-group">
        <button class="toolbar-btn" @click="insertMarkdown('# ', '')" title="标题">
          <span class="icon">H1</span>
        </button>
        <button class="toolbar-btn" @click="insertMarkdown('## ', '')" title="二级标题">
          <span class="icon">H2</span>
        </button>
        <button class="toolbar-btn" @click="insertMarkdown('**', '**')" title="粗体">
          <span class="icon">B</span>
        </button>
        <button class="toolbar-btn" @click="insertMarkdown('*', '*')" title="斜体">
          <span class="icon">I</span>
        </button>
        <button class="toolbar-btn" @click="insertMarkdown('`', '`')" title="行内代码">
          <span class="icon">&lt;/&gt;</span>
        </button>
      </div>

      <div class="toolbar-divider"></div>

      <div class="toolbar-group">
        <button class="toolbar-btn" @click="insertMarkdown('- ', '')" title="无序列表">
          <span class="icon">•••</span>
        </button>
        <button class="toolbar-btn" @click="insertMarkdown('1. ', '')" title="有序列表">
          <span class="icon">123</span>
        </button>
        <button class="toolbar-btn" @click="insertMarkdown('> ', '')" title="引用">
          <span class="icon">❝</span>
        </button>
        <button class="toolbar-btn" @click="insertCodeBlock" title="代码块">
          <span class="icon">{ }</span>
        </button>
      </div>

      <div class="toolbar-divider"></div>

      <div class="toolbar-group">
        <button class="toolbar-btn" @click="insertMarkdown('[', '](url)')" title="链接">
          <span class="icon">🔗</span>
        </button>
        <button class="toolbar-btn" @click="insertMarkdown('![', '](url)')" title="图片">
          <span class="icon">🖼️</span>
        </button>
        <button class="toolbar-btn" @click="insertTable" title="表格">
          <span class="icon">⊞</span>
        </button>
      </div>

      <div class="toolbar-spacer"></div>

      <div class="toolbar-group">
        <button
          class="toolbar-btn"
          :class="{ active: mode === 'edit' }"
          @click="mode = 'edit'"
          title="编辑模式"
        >
          <span class="icon">✏️</span>
        </button>
        <button
          class="toolbar-btn"
          :class="{ active: mode === 'split' }"
          @click="mode = 'split'"
          title="分屏模式"
        >
          <span class="icon">⚏</span>
        </button>
        <button
          class="toolbar-btn"
          :class="{ active: mode === 'preview' }"
          @click="mode = 'preview'"
          title="预览模式"
        >
          <span class="icon">👁️</span>
        </button>
      </div>

      <div class="toolbar-divider"></div>

      <div class="toolbar-group">
        <button class="toolbar-btn" @click="toggleFullscreen" :title="isFullscreen ? '退出全屏' : '全屏'">
          <span class="icon">{{ isFullscreen ? '⛶' : '⛶' }}</span>
        </button>
      </div>
    </div>

    <div class="editor-container" :class="`mode-${mode}`">
      <div v-show="mode !== 'preview'" class="editor-pane">
        <textarea
          ref="textareaRef"
          v-model="content"
          class="editor-textarea"
          :placeholder="placeholder"
          @input="handleInput"
          @keydown="handleKeydown"
          @scroll="handleEditorScroll"
        ></textarea>
        <div class="editor-info">
          <span>{{ content.length }} 字符</span>
          <span>{{ lineCount }} 行</span>
        </div>
      </div>

      <div v-show="mode !== 'edit'" class="preview-pane">
        <div
          class="markdown-preview"
          v-html="renderedHtml"
          ref="previewRef"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'

interface Props {
  modelValue: string
  placeholder?: string
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '支持 Markdown 格式...',
  height: '400px',
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const textareaRef = ref<HTMLTextAreaElement | null>(null)
const previewRef = ref<HTMLDivElement | null>(null)
const content = ref(props.modelValue)
const mode = ref<'edit' | 'split' | 'preview'>('split')
const isFullscreen = ref(false)

// 简单的 Markdown 渲染（不依赖外部库）
const renderedHtml = computed(() => {
  let html = content.value

  // 转义 HTML 特殊字符
  html = html.replace(/&/g, '&amp;')
           .replace(/</g, '&lt;')
           .replace(/>/g, '&gt;')

  // 代码块（必须在其他规则之前处理）
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
    return `<pre><code class="language-${lang}">${code.trim()}</code></pre>`
  })

  // 行内代码
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')

  // 标题
  html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>')
  html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>')
  html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>')

  // 粗体和斜体
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  html = html.replace(/___(.+?)___/g, '<strong><em>$1</em></strong>')
  html = html.replace(/__(.+?)__/g, '<strong>$1</strong>')
  html = html.replace(/_(.+?)_/g, '<em>$1</em>')

  // 链接
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')

  // 图片
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" />')

  // 引用
  html = html.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')

  // 有序列表
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>)/s, '<ol>$1</ol>')

  // 无序列表
  html = html.replace(/^[\-\*\+] (.+)$/gm, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')

  // 水平线
  html = html.replace(/^---$/gm, '<hr>')
  html = html.replace(/^\*\*\*$/gm, '<hr>')

  // 段落（将连续的非 HTML 行包装在 <p> 标签中）
  html = html.split('\n\n').map(para => {
    if (!para.match(/^<[^>]+>/)) {
      return `<p>${para}</p>`
    }
    return para
  }).join('\n')

  // 换行
  html = html.replace(/\n/g, '<br>')

  return html
})

const lineCount = computed(() => {
  return content.value.split('\n').length
})

watch(() => props.modelValue, (newVal) => {
  if (newVal !== content.value) {
    content.value = newVal
  }
})

watch(content, (newVal) => {
  emit('update:modelValue', newVal)
})

const handleInput = () => {
  // 输入已通过 v-model 处理
}

const handleKeydown = (e: KeyboardEvent) => {
  // Tab 键插入空格
  if (e.key === 'Tab') {
    e.preventDefault()
    insertAtCursor('  ')
  }

  // Ctrl/Cmd + B 加粗
  if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
    e.preventDefault()
    insertMarkdown('**', '**')
  }

  // Ctrl/Cmd + I 斜体
  if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
    e.preventDefault()
    insertMarkdown('*', '*')
  }
}

const insertAtCursor = (text: string) => {
  const textarea = textareaRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const value = content.value

  content.value = value.substring(0, start) + text + value.substring(end)

  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(start + text.length, start + text.length)
  })
}

const insertMarkdown = (prefix: string, suffix: string) => {
  const textarea = textareaRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = content.value.substring(start, end)
  const value = content.value

  if (selectedText) {
    content.value = value.substring(0, start) + prefix + selectedText + suffix + value.substring(end)
    nextTick(() => {
      textarea.focus()
      textarea.setSelectionRange(start, start + prefix.length + selectedText.length + suffix.length)
    })
  } else {
    content.value = value.substring(0, start) + prefix + suffix + value.substring(end)
    nextTick(() => {
      textarea.focus()
      textarea.setSelectionRange(start + prefix.length, start + prefix.length)
    })
  }
}

const insertCodeBlock = () => {
  insertMarkdown('```\n', '\n```')
}

const insertTable = () => {
  const table = `
| 列1 | 列2 | 列3 |
| --- | --- | --- |
| 内容1 | 内容2 | 内容3 |
| 内容4 | 内容5 | 内容6 |
`
  insertAtCursor(table)
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

const handleEditorScroll = () => {
  // 同步预览滚动（可选）
  if (mode.value === 'split' && textareaRef.value && previewRef.value) {
    const percentage = textareaRef.value.scrollTop /
      (textareaRef.value.scrollHeight - textareaRef.value.clientHeight)
    previewRef.value.scrollTop = percentage *
      (previewRef.value.scrollHeight - previewRef.value.clientHeight)
  }
}
</script>

<style scoped>
.markdown-editor {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
}

.markdown-editor.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  border-radius: 0;
  margin: 0;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
  border-radius: 8px 8px 0 0;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.toolbar-group {
  display: flex;
  gap: 0.25rem;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: #d1d5db;
  margin: 0 0.5rem;
}

.toolbar-spacer {
  flex: 1;
}

.toolbar-btn {
  padding: 0.4rem 0.6rem;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
}

.toolbar-btn:hover {
  background: #e5e7eb;
}

.toolbar-btn.active {
  background: #dbeafe;
  color: #3b82f6;
}

.toolbar-btn .icon {
  font-size: 0.9rem;
  font-weight: 600;
}

.editor-container {
  display: grid;
  flex: 1;
  overflow: hidden;
  min-height: v-bind(height);
}

.editor-container.mode-edit {
  grid-template-columns: 1fr;
}

.editor-container.mode-split {
  grid-template-columns: 1fr 1fr;
}

.editor-container.mode-preview {
  grid-template-columns: 1fr;
}

.editor-pane,
.preview-pane {
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.editor-pane {
  border-right: 1px solid #e5e7eb;
  position: relative;
}

.editor-textarea {
  flex: 1;
  padding: 1rem;
  border: none;
  outline: none;
  resize: none;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
  overflow-y: auto;
  background: #ffffff;
}

.editor-info {
  display: flex;
  gap: 1rem;
  padding: 0.5rem 1rem;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  font-size: 0.75rem;
  color: #6b7280;
}

.preview-pane {
  background: #ffffff;
}

.markdown-preview {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  font-size: 0.95rem;
  line-height: 1.7;
  color: #1f2937;
}

/* Markdown 样式 */
.markdown-preview :deep(h1) {
  font-size: 2rem;
  font-weight: 700;
  margin: 1.5rem 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e5e7eb;
  color: #111827;
}

.markdown-preview :deep(h2) {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 1.25rem 0 0.75rem;
  color: #1f2937;
}

.markdown-preview :deep(h3) {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 1rem 0 0.5rem;
  color: #374151;
}

.markdown-preview :deep(p) {
  margin: 0.75rem 0;
  line-height: 1.7;
}

.markdown-preview :deep(code) {
  background: #f3f4f6;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.85em;
  color: #e11d48;
}

.markdown-preview :deep(pre) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
  margin: 1rem 0;
}

.markdown-preview :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
  font-size: 0.875rem;
}

.markdown-preview :deep(blockquote) {
  border-left: 4px solid #3b82f6;
  padding-left: 1rem;
  margin: 1rem 0;
  color: #6b7280;
  font-style: italic;
}

.markdown-preview :deep(ul),
.markdown-preview :deep(ol) {
  margin: 0.75rem 0;
  padding-left: 2rem;
}

.markdown-preview :deep(li) {
  margin: 0.25rem 0;
}

.markdown-preview :deep(a) {
  color: #3b82f6;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s;
}

.markdown-preview :deep(a:hover) {
  border-bottom-color: #3b82f6;
}

.markdown-preview :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  margin: 1rem 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.markdown-preview :deep(hr) {
  border: none;
  border-top: 2px solid #e5e7eb;
  margin: 2rem 0;
}

.markdown-preview :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.markdown-preview :deep(th),
.markdown-preview :deep(td) {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e5e7eb;
  text-align: left;
}

.markdown-preview :deep(th) {
  background: #f9fafb;
  font-weight: 600;
}

.markdown-preview :deep(tr:hover) {
  background: #f9fafb;
}

/* 响应式 */
@media (max-width: 768px) {
  .editor-container.mode-split {
    grid-template-columns: 1fr;
  }

  .editor-pane {
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
  }

  .toolbar-group {
    flex-wrap: wrap;
  }
}
</style>

