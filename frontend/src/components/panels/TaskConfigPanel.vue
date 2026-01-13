<template>
  <section class="panel">
    <header class="panel-header">
      <h3>任务列表</h3>
      <button class="btn-primary" @click="startCreate">+ 新建任务</button>
    </header>
    <div class="panel-body">
      <div v-if="loading" class="placeholder">任务加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else>
        <ul class="task-list" v-if="tasks.length">
          <li
            v-for="task in tasks"
            :key="task.id"
            :class="['task-item', selectedTaskId === task.id ? 'selected' : '']"
            @click="select(task.id)"
          >
            <div class="task-main">
              <div class="task-title">{{ task.name }}</div>
              <div class="task-desc" v-if="task.description">{{ task.description }}</div>
              <div class="task-objective" v-if="task.objective">目标：{{ task.objective }}</div>
            </div>
            <div class="task-actions">
              <button class="link-btn" @click.stop="edit(task)">编辑</button>
              <button class="link-btn danger" @click.stop="remove(task.id)">删除</button>
            </div>
          </li>
        </ul>
        <div v-else class="placeholder">尚未创建任何任务，请点击右上角「新建任务」。</div>
      </div>
    </div>

    <!-- 任务编辑弹窗 -->
    <div v-if="showDialog" class="modal-overlay" @click.self="close">
      <div class="modal">
        <header class="modal-header">
          <h3>{{ editingTask?.id ? '编辑任务' : '新建任务' }}</h3>
          <button class="btn-close" @click="close">×</button>
        </header>
        <div class="modal-body">
          <div class="form-group">
            <label>任务名称</label>
            <input v-model="form.name" type="text" class="form-input" />
          </div>
          <div class="form-group">
            <label>任务描述</label>
            <textarea v-model="form.description" rows="3" class="form-textarea"></textarea>
          </div>
          <div class="form-group">
            <label>任务目标</label>
            <textarea v-model="form.objective" rows="2" class="form-textarea"></textarea>
          </div>
        </div>
        <footer class="modal-footer">
          <button class="btn-secondary" @click="close">取消</button>
          <button class="btn-primary" @click="save">保存</button>
        </footer>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import type { Task } from '../../api/tasks'
import { tasksApi } from '../../api/tasks'

interface Props {
  levelId: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'taskSelected', id: number | null): void
}>()

const tasks = ref<Task[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const selectedTaskId = ref<number | null>(null)

const showDialog = ref(false)
const editingTask = ref<Task | null>(null)
const form = ref({
  name: '',
  description: '',
  objective: '',
})

const loadTasks = async () => {
  loading.value = true
  error.value = null
  try {
    const resp = await tasksApi.getTasks(props.levelId)
    tasks.value = resp.data
    if (selectedTaskId.value) {
      const exists = tasks.value.some(t => t.id === selectedTaskId.value)
      if (!exists) {
        selectedTaskId.value = null
        emit('taskSelected', null)
      }
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '加载任务失败'
  } finally {
    loading.value = false
  }
}

const startCreate = () => {
  editingTask.value = null
  form.value = {
    name: '',
    description: '',
    objective: '',
  }
  showDialog.value = true
}

const edit = (task: Task) => {
  editingTask.value = task
  form.value = {
    name: task.name,
    description: task.description || '',
    objective: task.objective || '',
  }
  showDialog.value = true
}

const close = () => {
  showDialog.value = false
}

const save = async () => {
  if (!form.value.name.trim()) {
    alert('任务名称不能为空')
    return
  }
  try {
    if (editingTask.value) {
      await tasksApi.updateTask(editingTask.value.id, {
        name: form.value.name,
        description: form.value.description,
        objective: form.value.objective,
      })
    } else {
      await tasksApi.createTask(props.levelId, {
        name: form.value.name,
        description: form.value.description,
        objective: form.value.objective,
      })
    }
    showDialog.value = false
    await loadTasks()
  } catch (e: any) {
    alert(e?.response?.data?.detail || '保存任务失败')
  }
}

const remove = async (id: number) => {
  if (!confirm('确定要删除该任务吗？')) return
  try {
    await tasksApi.deleteTask(id)
    if (selectedTaskId.value === id) {
      selectedTaskId.value = null
      emit('taskSelected', null)
    }
    await loadTasks()
  } catch (e: any) {
    alert(e?.response?.data?.detail || '删除任务失败')
  }
}

const select = (id: number) => {
  selectedTaskId.value = id
  emit('taskSelected', id)
}

onMounted(loadTasks)

watch(
  () => props.levelId,
  () => {
    loadTasks()
  },
)
</script>

<style scoped>
/* keep original panel styles */
</style>


