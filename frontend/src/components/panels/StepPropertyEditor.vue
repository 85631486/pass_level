<template>
  <div class="step-property-editor">
    <div class="form-group">
      <label>步骤标题</label>
      <input v-model="localStep.title" @input="onChange" />
    </div>

    <div class="form-group">
      <label>步骤类型</label>
      <select v-model="localStep.type" @change="onChange">
        <option value="content">内容</option>
        <option value="quiz">测验</option>
        <option value="operation">操作</option>
        <option value="summary">总结</option>
      </select>
    </div>

    <div class="form-group">
      <label>建议用时</label>
      <input v-model="localStep.duration" placeholder="如：10分钟" @input="onChange" />
    </div>

    <div class="form-group">
      <label>难度等级</label>
      <div class="star-rating">
        <span
          v-for="i in 5"
          :key="i"
          class="star"
          :class="{ active: i <= (localStep.difficulty || 1) }"
          @click="setDifficulty(i)"
        >
          ⭐
        </span>
      </div>
    </div>

    <div class="form-group">
      <label>步骤内容 (Markdown)</label>
      <textarea
        v-model="localStep.content"
        rows="6"
        placeholder="输入步骤内容..."
        @input="onChange"
      />
    </div>

    <div class="form-group">
      <label>知识卡片</label>
      <div v-if="localStep.knowledgeCard" class="knowledge-card-preview">
        <div class="card-header">
          <span>{{ localStep.knowledgeCard.icon }}</span>
          <span>{{ localStep.knowledgeCard.title }}</span>
          <button @click="removeKnowledgeCard">删除</button>
        </div>
      </div>
      <button v-else @click="addKnowledgeCard">添加知识卡片</button>
    </div>

    <div v-if="showKnowledgeCardEditor" class="knowledge-card-editor">
      <div class="form-group">
        <label>图标</label>
        <input v-model="knowledgeCardForm.icon" placeholder="如：📚" />
      </div>
      <div class="form-group">
        <label>标题</label>
        <input v-model="knowledgeCardForm.title" />
      </div>
      <div class="form-group">
        <label>内容</label>
        <textarea v-model="knowledgeCardForm.content" rows="4" />
      </div>
      <div class="form-actions">
        <button @click="saveKnowledgeCard">保存</button>
        <button @click="cancelKnowledgeCard">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { CourseStep, KnowledgeCard } from '../../types/coursePlayer'

const props = defineProps<{
  step: CourseStep
}>()

const emit = defineEmits<{
  (e: 'update', step: CourseStep): void
}>()

const localStep = ref<CourseStep>({ ...props.step })
const showKnowledgeCardEditor = ref(false)
const knowledgeCardForm = ref<Partial<KnowledgeCard>>({
  icon: '📚',
  title: '',
  content: ''
})

watch(() => props.step, (newStep) => {
  localStep.value = { ...newStep }
}, { deep: true })

function onChange() {
  emit('update', { ...localStep.value })
}

function setDifficulty(level: number) {
  localStep.value = { ...localStep.value, difficulty: level }
  onChange()
}

function addKnowledgeCard() {
  showKnowledgeCardEditor.value = true
  knowledgeCardForm.value = {
    icon: '📚',
    title: '',
    content: ''
  }
}

function removeKnowledgeCard() {
  localStep.value = { ...localStep.value, knowledgeCard: undefined }
  onChange()
}

function saveKnowledgeCard() {
  localStep.value = {
    ...localStep.value,
    knowledgeCard: {
      icon: knowledgeCardForm.value.icon || '📚',
      title: knowledgeCardForm.value.title || '',
      content: knowledgeCardForm.value.content || ''
    }
  }
  showKnowledgeCardEditor.value = false
  onChange()
}

function cancelKnowledgeCard() {
  showKnowledgeCardEditor.value = false
}
</script>

<style scoped>
.step-property-editor {
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

.star-rating {
  display: flex;
  gap: 0.25rem;
}

.star {
  font-size: 1.5rem;
  cursor: pointer;
  opacity: 0.3;
  transition: opacity 0.2s;
}

.star.active {
  opacity: 1;
}

.knowledge-card-preview {
  padding: 0.75rem;
  background: #f3f4f6;
  border-radius: 6px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
}

.form-actions button {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: #ffffff;
  cursor: pointer;
}
</style>

