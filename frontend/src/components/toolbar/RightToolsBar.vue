<template>
  <div class="right-tools">
    <button class="tool-btn" @click="togglePanel('outline')">
      <span class="icon">📚</span>
      <span class="text">任务大纲</span>
    </button>
    <button class="tool-btn" @click="togglePanel('score')">
      <span class="icon">🎯</span>
      <span class="text">我的进度</span>
    </button>
    <button class="tool-btn" @click="togglePanel('cards')">
      <span class="icon">💳</span>
      <span class="text">知识卡包</span>
    </button>
    <button class="tool-btn" @click="togglePanel('achievements')">
      <span class="icon">🏆</span>
      <span class="text">成就徽章</span>
    </button>

    <div v-if="activePanel" class="drawer-overlay" @click.self="close">
      <div class="drawer">
        <header class="drawer-header">
          <h3>{{ panelTitle }}</h3>
          <button class="close-btn" @click="close">✕</button>
        </header>
        <section class="drawer-body">
          <!-- 任务大纲 -->
          <div v-if="activePanel === 'outline'" class="outline-content">
            <div
              v-for="(step, idx) in courseData?.steps || []"
              :key="step.id"
              class="outline-step"
              :class="{
                current: idx === currentStepIndex,
                completed: idx < currentStepIndex,
              }"
              @click="jumpToStep && jumpToStep(idx)"
            >
              <div class="step-number">步骤 {{ idx + 1 }}</div>
              <div class="step-title">{{ step.title }}</div>
            </div>
          </div>

          <!-- 我的进度 -->
          <div v-if="activePanel === 'score'" class="progress-content">
            <div class="progress-circle-wrapper">
              <svg width="120" height="120" class="progress-circle">
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  class="circle-bg"
                  fill="none"
                  stroke="#e5e7eb"
                  stroke-width="8"
                />
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  class="circle-progress"
                  fill="none"
                  stroke="#3b82f6"
                  stroke-width="8"
                  :stroke-dasharray="circumference"
                  :stroke-dashoffset="progressOffset"
                  transform="rotate(-90 60 60)"
                />
              </svg>
              <div class="circle-text">{{ progressPercent }}%</div>
            </div>
            <div class="progress-stats">
              <div class="stat-row">
                <span class="stat-label">⏱️ 学习时长:</span>
                <span class="stat-data">{{ formattedTime }}</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">🎯 当前步骤:</span>
                <span class="stat-data">{{ currentStepIndex + 1 }}/{{ totalSteps }}</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">📝 已答题数:</span>
                <span class="stat-data">{{ answeredCount }}/{{ totalQuestions }}</span>
              </div>
              <div class="stat-row highlight">
                <span class="stat-label">💯 当前积分:</span>
                <span class="stat-data">{{ score }}分</span>
              </div>
            </div>
          </div>

          <!-- 知识卡包 -->
          <div v-if="activePanel === 'cards'" class="cards-content">
            <div class="cards-count">已收集: <span>{{ collectedCards.length }}</span>张</div>
            <div class="cards-grid">
              <div
                v-for="card in collectedCards"
                :key="card.title"
                class="card-item"
                @click="openCard && openCard(card)"
              >
                <div class="card-icon">{{ card.icon }}</div>
                <div class="card-title">{{ card.title }}</div>
              </div>
              <div v-if="collectedCards.length === 0" class="empty-hint">
                暂无知识卡片，完成步骤任务后可获得
              </div>
            </div>
          </div>

          <!-- 成就徽章 -->
          <div v-if="activePanel === 'achievements'" class="achievements-content">
            <div class="badges-count">已获得: <span>{{ badges.length }}</span>个</div>
            <div class="badges-grid">
              <div v-for="badge in badges" :key="badge.name" class="badge-item">
                <div class="badge-icon">{{ badge.icon }}</div>
                <div class="badge-name">{{ badge.name }}</div>
              </div>
              <div v-if="badges.length === 0" class="empty-hint">
                暂无成就徽章，继续学习解锁更多成就
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { CourseData, KnowledgeCard } from '../../types/coursePlayer'

type PanelType = 'outline' | 'score' | 'cards' | 'achievements' | ''

interface Props {
  courseData?: CourseData | null
  currentStepIndex?: number
  progressPercent?: number
  formattedTime?: string
  totalSteps?: number
  answeredCount?: number
  totalQuestions?: number
  score?: number
  collectedCards?: KnowledgeCard[]
  badges?: Array<{ name: string; icon: string }>
}

interface Emits {
  (e: 'jumpToStep', index: number): void
  (e: 'openCard', card: KnowledgeCard): void
}

const props = withDefaults(defineProps<Props>(), {
  courseData: null,
  currentStepIndex: 0,
  progressPercent: 0,
  formattedTime: '00:00',
  totalSteps: 0,
  answeredCount: 0,
  totalQuestions: 0,
  score: 0,
  collectedCards: () => [],
  badges: () => [],
})

const emit = defineEmits<Emits>()

const activePanel = ref<PanelType>('')

const togglePanel = (panel: PanelType) => {
  activePanel.value = activePanel.value === panel ? '' : panel
}

const close = () => {
  activePanel.value = ''
}

const panelTitle = computed(() => {
  switch (activePanel.value) {
    case 'outline':
      return '📚 任务大纲'
    case 'score':
      return '🎯 我的进度'
    case 'cards':
      return '💳 知识卡包'
    case 'achievements':
      return '🏆 成就徽章'
    default:
      return ''
  }
})

const circumference = 2 * Math.PI * 50
const progressOffset = computed(() => {
  return circumference - (props.progressPercent / 100) * circumference
})

const jumpToStep = (index: number) => {
  emit('jumpToStep', index)
  close()
}

const openCard = (card: KnowledgeCard) => {
  emit('openCard', card)
}
</script>

<style scoped>
.right-tools {
  position: fixed;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 998;
}

.tool-btn {
  width: 56px;
  height: 56px;
  background: white;
  border: none;
  border-radius: 8px 0 0 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.3s ease;
  position: relative;
}

.tool-btn:hover {
  width: 80px;
  background: #3b82f6;
  color: white;
}

.icon {
  font-size: 20px;
}

.text {
  font-size: 10px;
  font-weight: 600;
  white-space: nowrap;
}

.tool-btn:hover .text {
  color: white;
}

.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  justify-content: flex-end;
  align-items: stretch;
  z-index: 1001;
  animation: fadeIn 0.2s ease;
}

.drawer {
  width: 400px;
  max-width: 80vw;
  background: #ffffff;
  height: 100%;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s ease;
}

.drawer-header {
  padding: 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
</style>

