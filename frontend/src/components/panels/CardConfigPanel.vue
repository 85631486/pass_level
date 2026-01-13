<template>
  <section class="panel">
    <!-- AI 生成面板 -->
    <AIGeneratePanel
      ref="aiPanel"
      :show-prompt-input="false"
      @generate="handleAIGenerate"
      @accept="handleAIAccept"
      @reject="handleAIReject"
      @regenerate="handleAIGenerate"
    >
      <template #result="{ data }">
        <div class="ai-cards-preview">
          <div v-if="data?.knowledge_cards?.length" class="card-group">
            <h5>知识卡片 ({{ data.knowledge_cards.length }})</h5>
            <div v-for="(card, idx) in data.knowledge_cards" :key="idx" class="preview-card">
              <strong>{{ card.title }}</strong>
              <p>{{ card.content }}</p>
            </div>
          </div>
          <div v-if="data?.skill_cards?.length" class="card-group">
            <h5>技能卡片 ({{ data.skill_cards.length }})</h5>
            <div v-for="(card, idx) in data.skill_cards" :key="idx" class="preview-card">
              <strong>{{ card.name }}</strong>
              <p>{{ card.description }}</p>
            </div>
          </div>
        </div>
      </template>
    </AIGeneratePanel>

    <header class="panel-header">
      <h3>知识与技能卡片</h3>
      <div class="header-actions">
        <button class="btn-secondary" @click="activeCardType = 'knowledge'">知识卡片</button>
        <button class="btn-secondary" @click="activeCardType = 'skill'">技能卡片</button>
      </div>
    </header>

    <p class="hint" v-if="!taskId">请先选择一个任务，再配置卡片。</p>

    <div class="panel-body" v-else>
      <div class="cards-tabs">
        <button
          :class="['tab-btn', activeCardType === 'knowledge' ? 'active' : '']"
          @click="activeCardType = 'knowledge'"
        >
          📚 知识卡片
        </button>
        <button
          :class="['tab-btn', activeCardType === 'skill' ? 'active' : '']"
          @click="activeCardType = 'skill'"
        >
          ⚡ 技能卡片
        </button>
      </div>

      <!-- 知识卡片列表 -->
      <div v-if="activeCardType === 'knowledge'" class="card-list-section">
        <div class="list-header">
          <span>已添加 {{ knowledgeCards.length }} 个知识卡片</span>
          <button class="btn-primary" @click="addKnowledgeCard">+ 添加知识卡片</button>
        </div>
        <div v-if="knowledgeCards.length === 0" class="placeholder">
          尚未添加知识卡片，点击上方按钮添加或使用 AI 生成。
        </div>
        <ul v-else class="card-list">
          <li v-for="(card, idx) in knowledgeCards" :key="idx" class="card-item">
            <div class="card-content">
              <div class="card-title">{{ card.title }}</div>
              <div class="card-desc">{{ card.content }}</div>
            </div>
            <div class="card-actions">
              <button class="link-btn" @click="editKnowledgeCard(idx)">编辑</button>
              <button class="link-btn danger" @click="removeKnowledgeCard(idx)">删除</button>
            </div>
          </li>
        </ul>
      </div>

      <!-- 技能卡片列表 -->
      <div v-if="activeCardType === 'skill'" class="card-list-section">
        <div class="list-header">
          <span>已添加 {{ skillCards.length }} 个技能卡片</span>
          <button class="btn-primary" @click="addSkillCard">+ 添加技能卡片</button>
        </div>
        <div v-if="skillCards.length === 0" class="placeholder">
          尚未添加技能卡片，点击上方按钮添加或使用 AI 生成。
        </div>
        <ul v-else class="card-list">
          <li v-for="(card, idx) in skillCards" :key="idx" class="card-item">
            <div class="card-content">
              <div class="card-title">{{ card.name }}</div>
              <div class="card-desc">{{ card.description }}</div>
            </div>
            <div class="card-actions">
              <button class="link-btn" @click="editSkillCard(idx)">编辑</button>
              <button class="link-btn danger" @click="removeSkillCard(idx)">删除</button>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- 知识卡片编辑弹窗 -->
    <div v-if="showKnowledgeDialog" class="modal-overlay" @click.self="closeKnowledgeDialog">
      <div class="modal">
        <header class="modal-header">
          <h3>{{ editingKnowledgeIndex !== null ? '编辑知识卡片' : '添加知识卡片' }}</h3>
          <button class="btn-close" @click="closeKnowledgeDialog">×</button>
        </header>
        <div class="modal-body">
          <div class="form-group">
            <label>卡片标题</label>
            <input v-model="knowledgeForm.title" type="text" class="form-input" />
          </div>
          <div class="form-group">
            <label>卡片内容</label>
            <textarea v-model="knowledgeForm.content" rows="5" class="form-textarea"></textarea>
          </div>
          <div class="form-group">
            <label>卡片类型</label>
            <select v-model="knowledgeForm.card_type" class="form-input">
              <option value="text">文本</option>
              <option value="image">图片</option>
              <option value="video">视频</option>
            </select>
          </div>
        </div>
        <footer class="modal-footer">
          <button class="btn-secondary" @click="closeKnowledgeDialog">取消</button>
          <button class="btn-primary" @click="saveKnowledgeCard">保存</button>
        </footer>
      </div>
    </div>

    <!-- 技能卡片编辑弹窗 -->
    <div v-if="showSkillDialog" class="modal-overlay" @click.self="closeSkillDialog">
      <div class="modal">
        <header class="modal-header">
          <h3>{{ editingSkillIndex !== null ? '编辑技能卡片' : '添加技能卡片' }}</h3>
          <button class="btn-close" @click="closeSkillDialog">×</button>
        </header>
        <div class="modal-body">
          <div class="form-group">
            <label>技能名称</label>
            <input v-model="skillForm.name" type="text" class="form-input" />
          </div>
          <div class="form-group">
            <label>技能描述</label>
            <textarea v-model="skillForm.description" rows="4" class="form-textarea"></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>技能等级</label>
              <input v-model.number="skillForm.level" type="number" min="1" class="form-input" />
            </div>
            <div class="form-group">
              <label>技能图标</label>
              <input v-model="skillForm.icon" type="text" class="form-input" placeholder="emoji或图标" />
            </div>
          </div>
        </div>
        <footer class="modal-footer">
          <button class="btn-secondary" @click="closeSkillDialog">取消</button>
          <button class="btn-primary" @click="saveSkillCard">保存</button>
        </footer>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { aiAssistantApi } from '../../api/aiAssistant'
import { tasksApi } from '../../api/tasks'
import AIGeneratePanel from './AIGeneratePanel.vue'

interface Props {
  taskId: number | null
}

interface KnowledgeCard {
  title: string
  content: string
  card_type: string
}

interface SkillCard {
  name: string
  description: string
  level: number
  icon: string
}

const props = defineProps<Props>()
const aiPanel = ref<InstanceType<typeof AIGeneratePanel> | null>(null)

const activeCardType = ref<'knowledge' | 'skill'>('knowledge')

const knowledgeCards = ref<KnowledgeCard[]>([])
const skillCards = ref<SkillCard[]>([])

const showKnowledgeDialog = ref(false)
const editingKnowledgeIndex = ref<number | null>(null)
const knowledgeForm = ref({
  title: '',
  content: '',
  card_type: 'text',
})

const showSkillDialog = ref(false)
const editingSkillIndex = ref<number | null>(null)
const skillForm = ref({
  name: '',
  description: '',
  level: 1,
  icon: '⚡',
})

const handleAIGenerate = async () => {
  if (!props.taskId) {
    alert('请先选择任务')
    return
  }

  aiPanel.value?.setGenerating(true)
  try {
    const taskResp = await tasksApi.getTask(props.taskId)
    const task = taskResp.data

    const resp = await aiAssistantApi.generateCards({
      task_name: task.name,
      task_description: task.description || '',
    })

    aiPanel.value?.setResult(resp.data)
  } catch (e: any) {
    aiPanel.value?.setError(e?.response?.data?.detail || 'AI 生成失败，请重试')
  }
}

const handleAIAccept = (result: any) => {
  if (result.knowledge_cards) {
    knowledgeCards.value.push(...result.knowledge_cards)
  }
  if (result.skill_cards) {
    skillCards.value.push(...result.skill_cards)
  }
  aiPanel.value?.clear()
}

const handleAIReject = () => {
  // 清空结果即可
}

const addKnowledgeCard = () => {
  editingKnowledgeIndex.value = null
  knowledgeForm.value = {
    title: '',
    content: '',
    card_type: 'text',
  }
  showKnowledgeDialog.value = true
}

const editKnowledgeCard = (idx: number) => {
  editingKnowledgeIndex.value = idx
  const card = knowledgeCards.value[idx]
  if (!card) return

  knowledgeForm.value = {
    title: card.title || '',
    content: card.content || '',
    card_type: card.card_type || 'text'
  }
  showKnowledgeDialog.value = true
}

const saveKnowledgeCard = () => {
  if (!knowledgeForm.value.title.trim()) {
    alert('卡片标题不能为空')
    return
  }

  if (editingKnowledgeIndex.value !== null) {
    knowledgeCards.value[editingKnowledgeIndex.value] = { ...knowledgeForm.value }
  } else {
    knowledgeCards.value.push({ ...knowledgeForm.value })
  }

  closeKnowledgeDialog()
}

const removeKnowledgeCard = (idx: number) => {
  if (confirm('确定要删除该知识卡片吗？')) {
    knowledgeCards.value.splice(idx, 1)
  }
}

const closeKnowledgeDialog = () => {
  showKnowledgeDialog.value = false
}

const addSkillCard = () => {
  editingSkillIndex.value = null
  skillForm.value = {
    name: '',
    description: '',
    level: 1,
    icon: '⚡',
  }
  showSkillDialog.value = true
}

const editSkillCard = (idx: number) => {
  editingSkillIndex.value = idx
  const card = skillCards.value[idx]
  if (!card) return

  skillForm.value = {
    name: card.name || '',
    description: card.description || '',
    level: card.level || 1,
    icon: card.icon || '🎯'
  }
  showSkillDialog.value = true
}

const saveSkillCard = () => {
  if (!skillForm.value.name.trim()) {
    alert('技能名称不能为空')
    return
  }

  if (editingSkillIndex.value !== null) {
    skillCards.value[editingSkillIndex.value] = { ...skillForm.value }
  } else {
    skillCards.value.push({ ...skillForm.value })
  }

  closeSkillDialog()
}

const removeSkillCard = (idx: number) => {
  if (confirm('确定要删除该技能卡片吗？')) {
    skillCards.value.splice(idx, 1)
  }
}

const closeSkillDialog = () => {
  showSkillDialog.value = false
}

watch(
  () => props.taskId,
  () => {
    knowledgeCards.value = []
    skillCards.value = []
  },
)
</script>

<style scoped>
/* keep original panel styles */
</style>


