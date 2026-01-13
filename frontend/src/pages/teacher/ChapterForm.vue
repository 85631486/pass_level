<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h3>{{ chapter ? '编辑篇章' : '创建篇章' }}</h3>
      </div>
      
      <form @submit.prevent="handleSubmit" class="form">
        <div class="form-group">
          <label for="name">篇章名称 <span class="required">*</span></label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            required
            placeholder="请输入篇章名称"
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label for="description">篇章描述</label>
          <textarea
            id="description"
            v-model="formData.description"
            rows="4"
            placeholder="请输入篇章描述（可选）"
            class="form-textarea"
          ></textarea>
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="handleClose">取消</button>
          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? '保存中...' : '保存' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { chaptersApi, type Chapter, type ChapterCreate, type ChapterUpdate } from '../../api/chapters'

interface Props {
  chapter?: Chapter | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  saved: []
}>()

const formData = ref<ChapterCreate | ChapterUpdate>({
  name: '',
  description: ''
})

const loading = ref(false)

watch(() => props.chapter, (newChapter) => {
  if (newChapter) {
    formData.value = {
      name: newChapter.name,
      description: newChapter.description || ''
    }
  } else {
    formData.value = {
      name: '',
      description: ''
    }
  }
}, { immediate: true })

const handleClose = () => {
  emit('close')
}

const handleSubmit = async () => {
  if (!formData.value.name || !formData.value.name.trim()) {
    alert('请输入篇章名称')
    return
  }
  
  loading.value = true
  try {
    if (props.chapter) {
      // 编辑
      await chaptersApi.updateChapter(props.chapter.id, formData.value as ChapterUpdate)
    } else {
      // 创建
      await chaptersApi.createChapter(formData.value as ChapterCreate)
    }
    emit('saved')
  } catch (err: any) {
    alert(err.response?.data?.detail || '保存失败')
    console.error('Error saving chapter:', err)
  } finally {
    loading.value = false
  }
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
  z-index: 1000;
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
  max-width: 520px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
  display: flex;
  flex-direction: column;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.75rem 2rem;
  border-bottom: 2px solid #f1f5f9;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.form {
  padding: 2rem;
  flex: 1;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 1.75rem;
}

.form-group:last-of-type {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 600;
  font-size: 0.95rem;
  color: #334155;
}

.required {
  color: #ef4444;
  margin-left: 2px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  font-family: inherit;
  transition: all 0.3s ease;
  background: #ffffff;
  color: #1e293b;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  background: #ffffff;
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: #94a3b8;
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
  line-height: 1.6;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2.5rem;
  padding-top: 1.5rem;
  border-top: 2px solid #f1f5f9;
}

.btn-primary,
.btn-cancel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.875rem 2rem;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  transition: all 0.3s ease;
  min-width: 100px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-cancel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  opacity: 0.85;
}

.btn-cancel:hover {
  opacity: 1;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-cancel:active {
  transform: translateY(0);
}
</style>
