<template>
  <section class="panel">
    <header class="panel-header">
      <h3>任务操作环节与步骤</h3>
      <p class="hint" v-if="!taskId">请先在左侧选择一个任务，再配置环节和步骤。</p>
    </header>
    <div class="panel-body" v-if="taskId">
      <div class="phases-steps">
        <div class="phase-column">
          <div class="phase-header">
            <span>环节列表</span>
            <button class="btn-primary" @click="startCreatePhase">+ 新建环节</button>
          </div>
          <div v-if="phasesLoading" class="placeholder">环节加载中...</div>
          <div v-else-if="phasesError" class="error">{{ phasesError }}</div>
          <ul v-else class="phase-list">
            <li
              v-for="phase in phases"
              :key="phase.id"
              :class="['phase-item', selectedPhaseId === phase.id ? 'selected' : '']"
              @click="selectPhase(phase.id)"
            >
              <div>
                <div class="phase-name">{{ phase.phase_name }}</div>
                <div class="phase-meta">
                  顺序：{{ phase.order }} ｜ {{ phase.is_required ? '必做' : '选做' }}
                </div>
              </div>
              <div class="phase-actions">
                <button class="link-btn" @click.stop="editPhase(phase)">编辑</button>
                <button class="link-btn danger" @click.stop="removePhase(phase.id)">删除</button>
              </div>
            </li>
          </ul>
        </div>

        <div class="step-column">
          <div class="phase-header">
            <span>步骤列表</span>
            <button class="btn-primary" @click="startCreateStep" :disabled="!selectedPhaseId">+ 新建步骤</button>
          </div>
          <div v-if="!selectedPhaseId" class="placeholder">请先在左侧选择一个环节。</div>
          <template v-else>
            <div v-if="stepsLoading" class="placeholder">步骤加载中...</div>
            <div v-else-if="stepsError" class="error">{{ stepsError }}</div>
            <ul v-else class="step-list">
              <li v-for="step in steps" :key="step.id" class="step-item">
                <div>
                  <div class="step-name">{{ step.step_name }}</div>
                  <div class="step-meta">
                    顺序：{{ step.order }} ｜ 提交类型：{{ step.submission_type }}
                  </div>
                  <div class="step-desc" v-if="step.content">内容：{{ step.content }}</div>
                  <div class="step-desc" v-if="step.requirements">要求：{{ step.requirements }}</div>
                </div>
                <div class="phase-actions">
                  <button class="link-btn" @click.stop="editStep(step)">编辑</button>
                  <button class="link-btn danger" @click.stop="removeStep(step.id)">删除</button>
                </div>
              </li>
            </ul>
          </template>
        </div>
      </div>
    </div>

    <!-- 环节编辑弹窗 -->
    <div v-if="showPhaseDialog" class="modal-overlay" @click.self="closePhaseDialog">
      <div class="modal">
        <header class="modal-header">
          <h3>{{ editingPhase?.id ? '编辑环节' : '新建环节' }}</h3>
          <button class="btn-close" @click="closePhaseDialog">×</button>
        </header>
        <div class="modal-body">
          <div class="form-group">
            <label>环节名称</label>
            <input v-model="phaseForm.phase_name" type="text" class="form-input" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>顺序</label>
              <input v-model.number="phaseForm.order" type="number" class="form-input" />
            </div>
            <div class="form-group checkbox-group">
              <label>
                <input type="checkbox" v-model="phaseForm.is_required" />
                必做环节
              </label>
            </div>
          </div>
        </div>
        <footer class="modal-footer">
          <button class="btn-secondary" @click="closePhaseDialog">取消</button>
          <button class="btn-primary" @click="savePhase">保存</button>
        </footer>
      </div>
    </div>

    <!-- 步骤编辑弹窗 -->
    <div v-if="showStepDialog" class="modal-overlay" @click.self="closeStepDialog">
      <div class="modal large">
        <header class="modal-header">
          <h3>{{ editingStep?.id ? '编辑步骤' : '新建步骤' }}</h3>
          <button class="btn-close" @click="closeStepDialog">×</button>
        </header>
        <div class="modal-body">
          <div class="form-group">
            <label>步骤名称</label>
            <input v-model="stepForm.step_name" type="text" class="form-input" />
          </div>
          <div class="form-group">
            <label>步骤内容</label>
            <textarea v-model="stepForm.content" rows="3" class="form-textarea"></textarea>
          </div>
          <div class="form-group">
            <label>操作要求</label>
            <textarea v-model="stepForm.requirements" rows="2" class="form-textarea"></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>提交类型</label>
              <select v-model="stepForm.submission_type" class="form-input">
                <option value="text">文本</option>
                <option value="file">文件</option>
                <option value="link">链接</option>
                <option value="code">代码</option>
              </select>
            </div>
            <div class="form-group">
              <label>顺序</label>
              <input v-model.number="stepForm.order" type="number" class="form-input" />
            </div>
          </div>
        </div>
        <footer class="modal-footer">
          <button class="btn-secondary" @click="closeStepDialog">取消</button>
          <button class="btn-primary" @click="saveStep">保存</button>
        </footer>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { TaskPhase } from '../api/taskPhases'
import { taskPhasesApi } from '../api/taskPhases'
import type { TaskStep } from '../api/taskSteps'
import { taskStepsApi } from '../api/taskSteps'

interface Props {
  taskId: number | null
}

const props = defineProps<Props>()

const phases = ref<TaskPhase[]>([])
const phasesLoading = ref(false)
const phasesError = ref<string | null>(null)
const selectedPhaseId = ref<number | null>(null)

const steps = ref<TaskStep[]>([])
const stepsLoading = ref(false)
const stepsError = ref<string | null>(null)

const showPhaseDialog = ref(false)
const editingPhase = ref<TaskPhase | null>(null)
const phaseForm = ref({
  phase_name: '',
  order: 0,
  is_required: true,
})

const showStepDialog = ref(false)
const editingStep = ref<TaskStep | null>(null)
const stepForm = ref({
  step_name: '',
  content: '',
  requirements: '',
  submission_type: 'text',
  order: 0,
})

const loadPhases = async () => {
  if (!props.taskId) return
  phasesLoading.value = true
  phasesError.value = null
  try {
    const resp = await taskPhasesApi.getPhases(props.taskId)
    phases.value = resp.data
    if (selectedPhaseId.value) {
      const exists = phases.value.some(p => p.id === selectedPhaseId.value)
      if (!exists) {
        selectedPhaseId.value = null
        steps.value = []
      }
    }
  } catch (e: any) {
    phasesError.value = e?.response?.data?.detail || '加载环节失败'
  } finally {
    phasesLoading.value = false
  }
}

const loadSteps = async () => {
  if (!props.taskId || !selectedPhaseId.value) {
    steps.value = []
    return
  }
  stepsLoading.value = true
  stepsError.value = null
  try {
    const resp = await taskStepsApi.getSteps(props.taskId, selectedPhaseId.value)
    steps.value = resp.data
  } catch (e: any) {
    stepsError.value = e?.response?.data?.detail || '加载步骤失败'
  } finally {
    stepsLoading.value = false
  }
}

const selectPhase = (id: number) => {
  selectedPhaseId.value = id
  loadSteps()
}

const startCreatePhase = () => {
  if (!props.taskId) return
  editingPhase.value = null
  phaseForm.value = {
    phase_name: '',
    order: phases.value.length,
    is_required: true,
  }
  showPhaseDialog.value = true
}

const editPhase = (phase: TaskPhase) => {
  editingPhase.value = phase
  phaseForm.value = {
    phase_name: phase.phase_name,
    order: phase.order,
    is_required: phase.is_required,
  }
  showPhaseDialog.value = true
}

const closePhaseDialog = () => {
  showPhaseDialog.value = false
}

const savePhase = async () => {
  if (!props.taskId) return
  if (!phaseForm.value.phase_name.trim()) {
    alert('环节名称不能为空')
    return
  }
  try {
    if (editingPhase.value) {
      await taskPhasesApi.updatePhase(props.taskId, editingPhase.value.id, {
        phase_name: phaseForm.value.phase_name,
        order: phaseForm.value.order,
        is_required: phaseForm.value.is_required,
      })
    } else {
      await taskPhasesApi.createPhase(props.taskId, {
        phase_name: phaseForm.value.phase_name,
        order: phaseForm.value.order,
        is_required: phaseForm.value.is_required,
      })
    }
    showPhaseDialog.value = false
    await loadPhases()
  } catch (e: any) {
    alert(e?.response?.data?.detail || '保存环节失败')
  }
}

const removePhase = async (id: number) => {
  if (!props.taskId) return
  if (!confirm('确定要删除该环节吗？')) return
  try {
    await taskPhasesApi.deletePhase(props.taskId, id)
    if (selectedPhaseId.value === id) {
      selectedPhaseId.value = null
      steps.value = []
    }
    await loadPhases()
  } catch (e: any) {
    alert(e?.response?.data?.detail || '删除环节失败')
  }
}

const startCreateStep = () => {
  if (!props.taskId || !selectedPhaseId.value) return
  editingStep.value = null
  stepForm.value = {
    step_name: '',
    content: '',
    requirements: '',
    submission_type: 'text',
    order: steps.value.length,
  }
  showStepDialog.value = true
}

const editStep = (step: TaskStep) => {
  editingStep.value = step
  stepForm.value = {
    step_name: step.step_name,
    content: step.content || '',
    requirements: step.requirements || '',
    submission_type: step.submission_type,
    order: step.order,
  }
  showStepDialog.value = true
}

const closeStepDialog = () => {
  showStepDialog.value = false
}

const saveStep = async () => {
  if (!props.taskId || !selectedPhaseId.value) return
  if (!stepForm.value.step_name.trim()) {
    alert('步骤名称不能为空')
    return
  }
  try {
    if (editingStep.value) {
      await taskStepsApi.updateStep(props.taskId, selectedPhaseId.value, editingStep.value.id, {
        step_name: stepForm.value.step_name,
        content: stepForm.value.content,
        requirements: stepForm.value.requirements,
        submission_type: stepForm.value.submission_type,
        order: stepForm.value.order,
      })
    } else {
      await taskStepsApi.createStep(props.taskId, selectedPhaseId.value, {
        step_name: stepForm.value.step_name,
        content: stepForm.value.content,
        requirements: stepForm.value.requirements,
        submission_type: stepForm.value.submission_type,
        order: stepForm.value.order,
      })
    }
    showStepDialog.value = false
    await loadSteps()
  } catch (e: any) {
    alert(e?.response?.data?.detail || '保存步骤失败')
  }
}

const removeStep = async (id: number) => {
  if (!props.taskId || !selectedPhaseId.value) return
  if (!confirm('确定要删除该步骤吗？')) return
  try {
    await taskStepsApi.deleteStep(props.taskId, selectedPhaseId.value, id)
    await loadSteps()
  } catch (e: any) {
    alert(e?.response?.data?.detail || '删除步骤失败')
  }
}

watch(
  () => props.taskId,
  () => {
    phases.value = []
    steps.value = []
    selectedPhaseId.value = null
    if (props.taskId) {
      loadPhases()
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.panel {
  height: 100%;
}
.panel-header {
  margin-bottom: 0.75rem;
}
.hint {
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: #6b7280;
}
.panel-body {
  min-height: 260px;
}
.phases-steps {
  display: grid;
  grid-template-columns: 1.1fr 1.4fr;
  gap: 1rem;
}
.phase-column,
.step-column {
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  padding: 0.75rem;
  background: #f9fafb;
}
.phase-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.btn-primary {
  padding: 0.3rem 0.8rem;
  border-radius: 999px;
  border: none;
  background: #3b82f6;
  color: #ffffff;
  cursor: pointer;
  font-size: 0.8rem;
}
.placeholder {
  padding: 0.75rem;
  color: #9ca3af;
  font-size: 0.85rem;
}
.error {
  padding: 0.75rem;
  color: #b91c1c;
  font-size: 0.85rem;
}
.phase-list,
.step-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.phase-item,
.step-item {
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  padding: 0.5rem 0.6rem;
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  cursor: pointer;
  background: #ffffff;
}
.phase-item.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}
.phase-name {
  font-weight: 600;
  margin-bottom: 0.1rem;
}
.phase-meta,
.step-meta,
.step-desc {
  font-size: 0.8rem;
  color: #6b7280;
}
.step-name {
  font-weight: 600;
  margin-bottom: 0.1rem;
}
.phase-actions {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.link-btn {
  border: none;
  background: none;
  padding: 0;
  font-size: 0.78rem;
  color: #3b82f6;
  cursor: pointer;
}
.link-btn.danger {
  color: #dc2626;
}
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.modal {
  background: #ffffff;
  border-radius: 8px;
  width: 420px;
  max-width: 90vw;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.3);
}
.modal.large {
  width: 600px;
}
.modal-header {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-body {
  padding: 0.75rem 1rem;
}
.modal-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
.btn-secondary {
  padding: 0.4rem 0.9rem;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  cursor: pointer;
  font-size: 0.85rem;
}
.btn-close {
  border: none;
  background: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #6b7280;
}
.form-group {
  margin-bottom: 0.75rem;
}
label {
  display: block;
  font-size: 0.85rem;
  color: #4b5563;
  margin-bottom: 0.25rem;
}
.form-input,
.form-textarea {
  width: 100%;
  padding: 0.4rem 0.5rem;
  border-radius: 4px;
  border: 1px solid #d1d5db;
  font-size: 0.9rem;
}
.form-textarea {
  resize: vertical;
}
.form-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}
.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-bottom: 0;
}
</style>

