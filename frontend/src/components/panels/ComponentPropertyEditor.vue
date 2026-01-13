<template>
  <div class="component-property-editor">
    <div class="form-group">
      <label>组件类型</label>
      <input :value="getComponentTypeName(component.type)" disabled />
    </div>

    <!-- 标签页 -->
    <div class="tabs">
      <button
        :class="{ active: activeTab === 'content' }"
        @click="activeTab = 'content'"
      >
        内容
      </button>
      <button
        :class="{ active: activeTab === 'style' }"
        @click="activeTab = 'style'"
      >
        样式
      </button>
    </div>

    <!-- 内容标签页 -->
    <div v-show="activeTab === 'content'" class="tab-content">

    <!-- 文本组件 -->
    <template v-if="component.type === 'text'">
      <div class="form-group">
        <label>文本内容</label>
        <textarea
          v-model="localConfig.content"
          rows="6"
          placeholder="输入文本内容..."
          @focus="isEditing = true"
          @blur="() => { isEditing = false; onChange() }"
          @input="onChange"
        />
      </div>
    </template>

    <!-- 代码编辑器组件 -->
    <template v-if="component.type === 'code'">
      <div class="form-group">
        <label>编程语言</label>
        <select v-model="localConfig.language" @change="onChange">
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="java">Java</option>
          <option value="cpp">C++</option>
          <option value="sql">SQL</option>
        </select>
      </div>
      <div class="form-group">
        <label>代码模板</label>
        <textarea
          v-model="localConfig.template"
          rows="8"
          placeholder="输入代码模板..."
          @input="onChange"
        />
      </div>
    </template>

    <!-- 题目组件 -->
    <template v-if="component.type === 'quiz'">
      <div class="form-group">
        <label>题目</label>
        <textarea
          v-model="localConfig.question"
          rows="3"
          placeholder="输入题目..."
          @input="onChange"
        />
      </div>
      <div class="form-group">
        <label>选项</label>
        <div v-if="!localConfig.options || localConfig.options.length === 0" class="empty-options">
          <p>暂无选项，请添加选项</p>
        </div>
        <div v-for="(option, idx) in (localConfig.options || [])" :key="idx" class="option-item">
          <input
            v-model="option.text"
            :placeholder="`选项 ${String.fromCharCode(65 + idx)}`"
            @input="onChange"
          />
          <input
            v-model="option.value"
            :placeholder="`值 (${String.fromCharCode(65 + idx)})`"
            class="option-value"
            @input="onChange"
          />
          <button @click="removeOption(idx)">删除</button>
        </div>
        <button @click="addOption">+ 添加选项</button>
      </div>
      <div class="form-group">
        <label>正确答案</label>
        <select v-model="localConfig.answer" @change="onChange">
          <option
            v-for="(option, idx) in (localConfig.options || [])"
            :key="idx"
            :value="option.value || String.fromCharCode(65 + idx)"
          >
            {{ option.text || `选项 ${String.fromCharCode(65 + idx)}` }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label>解析</label>
        <textarea
          v-model="localConfig.explanation"
          rows="3"
          placeholder="输入解析..."
          @input="onChange"
        />
      </div>
    </template>

    <!-- 视频组件 -->
    <template v-if="component.type === 'video'">
      <div class="form-group">
        <label>视频URL</label>
        <input
          v-model="localConfig.url"
          placeholder="输入视频URL..."
          @input="onChange"
        />
      </div>
    </template>

    <!-- 图片组件 -->
    <template v-if="component.type === 'image'">
      <div class="form-group">
        <label>图片URL</label>
        <input
          v-model="localConfig.url"
          placeholder="输入图片URL..."
          @input="onChange"
        />
      </div>
      <div class="form-group">
        <label>替代文本</label>
        <input
          v-model="localConfig.alt"
          placeholder="输入替代文本..."
          @input="onChange"
        />
      </div>
    </template>
    </div>

    <!-- 样式标签页 -->
    <div v-show="activeTab === 'style'" class="tab-content">
      <AdvancedStyleEditor
        :style="localStyle"
        @update:style="updateStyle"
      />
    </div>

    <div class="form-actions">
      <button @click="deleteComponent">删除组件</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { ComponentStyle } from '../../types/coursePlayer'
import AdvancedStyleEditor from './AdvancedStyleEditor.vue'

const props = defineProps<{
  component: any
}>()

const emit = defineEmits<{
  (e: 'update', component: any): void
  (e: 'delete'): void
}>()

const activeTab = ref<'content' | 'style'>('content')

// 初始化配置，确保所有字段都有默认值
function initConfig(config: any, type: string): any {
  const defaultConfigs: Record<string, any> = {
    text: { content: '' },
    code: { language: 'python', template: '', testCases: [] },
    quiz: { question: '', options: [], answer: '' },
    video: { url: '', checkpoints: [] },
    image: { url: '', alt: '' },
    drawing: { tools: ['pen'] },
    dragdrop: { items: [], targetZones: [] }
  }
  
  const defaultConfig = defaultConfigs[type] || {}
  return { ...defaultConfig, ...(config || {}) }
}

const localConfig = ref<any>(initConfig(props.component.config, props.component.type))
const localStyle = ref<ComponentStyle>({ ...(props.component.style || {}) })

// 标记当前是否处于编辑中（避免父组件更新覆盖正在编辑的本地内容）
const isEditing = ref(false)

watch(() => props.component, (newComponent) => {
  if (!newComponent) return
  if (!isEditing.value) {
    localConfig.value = initConfig(newComponent.config, newComponent.type)
    localStyle.value = { ...(newComponent.style || {}) }
  } else {
    console.debug('[ComponentPropertyEditor] parent component changed while editing, skip overwrite', newComponent?.id)
  }
}, { deep: true, immediate: true })

function onChange() {
  emit('update', {
    ...props.component,
    config: { ...localConfig.value },
    style: { ...localStyle.value }
  })
}

function updateStyle(style: ComponentStyle) {
  localStyle.value = style
  emit('update', {
    ...props.component,
    config: { ...localConfig.value },
    style: { ...localStyle.value }
  })
}

function getComponentTypeName(type: string): string {
  const names: Record<string, string> = {
    text: '文本',
    code: '代码编辑器',
    quiz: '题目',
    video: '视频',
    image: '图片',
    drawing: '绘图',
    dragdrop: '拖拽排序'
  }
  return names[type] || type
}

function addOption() {
  if (!localConfig.value.options) {
    localConfig.value.options = []
  }
  const index = localConfig.value.options.length
  localConfig.value.options.push({
    value: String.fromCharCode(65 + index),
    text: ''
  })
  onChange()
}

function removeOption(index: number) {
  if (localConfig.value.options) {
    localConfig.value.options.splice(index, 1)
    onChange()
  }
}

function deleteComponent() {
  if (confirm('确定要删除这个组件吗？')) {
    emit('delete')
  }
}
</script>

<style scoped>
.component-property-editor {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.875rem;
}

.empty-options {
  padding: 0.5rem;
  background: #f3f4f6;
  border-radius: 4px;
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.option-item {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.option-item input {
  flex: 1;
}

.option-item .option-value {
  flex: 0 0 80px;
}

.option-item button {
  padding: 0.5rem;
  border: 1px solid #dc2626;
  border-radius: 4px;
  background: #fee2e2;
  color: #dc2626;
  cursor: pointer;
}

.form-actions {
  margin-top: 1rem;
}

.form-actions button {
  padding: 0.5rem 1rem;
  border: 1px solid #dc2626;
  border-radius: 4px;
  background: #fee2e2;
  color: #dc2626;
  cursor: pointer;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 1rem;
}

.tabs button {
  padding: 0.5rem 1rem;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  cursor: pointer;
  font-size: 0.875rem;
  color: #6b7280;
}

.tabs button:hover {
  color: #374151;
}

.tabs button.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

.tab-content {
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}
</style>

