<template>
  <div class="interactive-preview">
    <header class="preview-toolbar">
      <span>交互式关卡预览</span>
      <div class="actions compact" aria-hidden="true"></div>
    </header>

    <main class="preview-body">
      <div v-if="!courseData" class="preview-empty">
        <div>
          <p>未获取到交互式课程数据。</p>
          <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
        </div>
      </div>
      <LevelInteractivePlayer
        v-else
        ref="playerRef"
        :course-data="courseData"
      />
    </main>

    <RightToolsBar
      v-if="courseData"
      :course-data="courseData"
      :current-step-index="playerData.currentStepIndex"
      :progress-percent="playerData.progressPercent"
      :formatted-time="playerData.formattedTime"
      :total-steps="playerData.totalSteps"
      :answered-count="playerData.answeredCount"
      :total-questions="playerData.totalQuestions"
      :score="playerData.score"
      :collected-cards="playerData.collectedCards"
      :badges="playerData.badges"
      @jump-to-step="handleJumpToStep"
      @open-card="handleOpenCard"
    />
  </div>
  <!-- bottom centered controls -->
  <div class="preview-controls" v-if="courseData">
    <button class="btn-icon" @click="refreshData" title="重新加载">⟳</button>
    <button class="btn-icon" @click="prevPage" :disabled="playerData.currentStepIndex <= 0" title="上一页">◀</button>
    <button class="btn-icon" @click="nextPage" :disabled="playerData.currentStepIndex >= (playerData.totalSteps - 1)" title="下一页">▶</button>
    <button class="btn-primary btn-small" @click="closeWindow" title="关闭预览">关闭</button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, reactive, watch } from 'vue'
import LevelInteractivePlayer from '../../components/player/LevelInteractivePlayer.vue'
import RightToolsBar from '../../components/toolbar/RightToolsBar.vue'
import type { CourseData, KnowledgeCard } from '../../types/coursePlayer'

const courseData = ref<CourseData | null>(null)
const errorMessage = ref('')
const playerRef = ref<InstanceType<typeof LevelInteractivePlayer> | null>(null)

const playerData = reactive({
  currentStepIndex: 0,
  progressPercent: 0,
  formattedTime: '00:00',
  totalSteps: 0,
  answeredCount: 0,
  totalQuestions: 0,
  score: 0,
  collectedCards: [] as KnowledgeCard[],
  badges: [] as Array<{ name: string; icon: string }>,
})

// 定期从 player 组件同步数据
const syncPlayerData = () => {
  if (!playerRef.value) return
  const exposed = playerRef.value as any
  if (exposed) {
    playerData.currentStepIndex = exposed.currentStepIndex ?? 0
    playerData.progressPercent = exposed.progressPercent ?? 0
    playerData.formattedTime = exposed.formattedTime ?? '00:00'
    playerData.totalSteps = exposed.totalSteps ?? 0
    playerData.answeredCount = exposed.answeredCount ?? 0
    playerData.totalQuestions = exposed.totalQuestions ?? 0
    playerData.score = exposed.score ?? 0
    playerData.collectedCards = exposed.collectedCards ?? []
    playerData.badges = exposed.badges ?? []
  }
}

let syncInterval: number | null = null

watch(
  () => courseData.value,
  () => {
    if (courseData.value && playerRef.value) {
      // 立即同步一次
      setTimeout(syncPlayerData, 100)
      // 定期同步（每500ms）
      if (syncInterval) clearInterval(syncInterval)
      syncInterval = window.setInterval(syncPlayerData, 500)
    }
  },
  { immediate: true }
)

const loadData = () => {
  const dataStr = localStorage.getItem('levelInteractivePreviewData')
  if (!dataStr) {
    courseData.value = null
    errorMessage.value = '本地未找到预览数据，请在关卡编辑器中先成功生成一次交互 JSON，并点击"预览交互式网页"。'
    return
  }
  try {
    courseData.value = JSON.parse(dataStr)
    errorMessage.value = ''
  } catch (err) {
    console.error('解析预览数据失败:', err)
    courseData.value = null
    errorMessage.value = '读取本地预览数据失败，请重新在关卡编辑器中生成交互 JSON 并再次预览。'
  }
}

const refreshData = () => {
  loadData()
}

const closeWindow = () => {
  if (syncInterval) clearInterval(syncInterval)
  window.close()
}

const handleJumpToStep = (index: number) => {
  if (playerRef.value && typeof (playerRef.value as any).jumpToStep === 'function') {
    ;(playerRef.value as any).jumpToStep(index)
  }
}

const handleOpenCard = (card: KnowledgeCard) => {
  if (playerRef.value && typeof (playerRef.value as any).openKnowledgeCard === 'function') {
    ;(playerRef.value as any).openKnowledgeCard(card)
  }
}

function prevPage() {
  const idx = Math.max(0, (playerData.currentStepIndex || 0) - 1)
  handleJumpToStep(idx)
}

function nextPage() {
  const max = Math.max(0, (playerData.totalSteps || 0) - 1)
  const idx = Math.min(max, (playerData.currentStepIndex || 0) + 1)
  handleJumpToStep(idx)
}

onMounted(() => {
  loadData()
})

onBeforeUnmount(() => {
  if (syncInterval) clearInterval(syncInterval)
})
</script>

<style scoped>
.interactive-preview {
  width: 100vw;
  height: 100vh;
  background: #050714;
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
}

.preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1rem;
  background: rgba(2, 6, 23, 0.92);
  border-bottom: 1px solid rgba(148, 163, 184, 0.06);
  font-weight: 600;
  letter-spacing: 0.02em;
  height: 56px;
}

.preview-toolbar .actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.actions.compact { gap: 0.5rem; align-items: center; }

.btn-icon {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  border: 1px solid rgba(226,232,240,0.08);
  background: transparent;
  color: #e2e8f0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.12s, transform 0.12s;
}
.btn-icon:hover:not(:disabled) { background: rgba(226,232,240,0.04); transform: translateY(-1px); }
.btn-icon:disabled { opacity: 0.45; cursor: not-allowed; }

.btn-small { padding: 0.35rem 0.75rem; border-radius: 8px; font-size: 0.95rem; }

.btn-primary,
.btn-secondary {
  padding: 0.45rem 1rem;
  border-radius: 999px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
}

.btn-primary {
  background: #38bdf8;
  color: #0f172a;
}

.btn-primary:hover {
  background: #0ea5e9;
}

.btn-secondary {
  background: transparent;
  border: 1px solid rgba(226, 232, 240, 0.4);
  color: #e2e8f0;
}

.btn-secondary:hover {
  background: rgba(226, 232, 240, 0.1);
}

.preview-body {
  flex: 1;
  width: 100%;
  height: 100%;
  padding: 0 1.5rem 1.5rem;
  box-sizing: border-box;
}

.preview-body :deep(.level-player) {
  width: 100%;
  height: 100%;
  border-radius: 16px;
  box-shadow: 0 30px 60px rgba(2, 6, 23, 0.6);
}

.preview-empty {
  flex: 1;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #475569;
  background: #f8fafc;
  border-radius: 12px;
}

.error-text {
  margin-top: 0.75rem;
  color: #b91c1c;
  font-size: 0.9rem;
}

.preview-controls {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom: 20px;
  display: flex;
  gap: 12px;
  align-items: center;
  z-index: 1200;
  background: rgba(2,6,23,0.6);
  padding: 8px 12px;
  border-radius: 999px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.4);
}
.preview-controls .btn-icon { background: rgba(255,255,255,0.04); border-color: rgba(255,255,255,0.08); }
.preview-controls .btn-primary { background: #06b6d4; color: white; border-radius: 6px; padding: 6px 10px; }
</style>


