<template>
  <div v-if="courseData" class="level-player">
    <header class="player-header">
      <div class="header-top">
        <div class="title-block">
          <h2>{{ headerTitle }}</h2>
          <p class="subtitle">交互式学习页面 · 当前步骤 {{ currentStepIndex + 1 }} / {{ totalSteps }}</p>
        </div>
      </div>
      <div class="progress-row">
        <div class="progress-bar-wrap">
          <EnhancedProgressBar :progress="progressPercent" />
        </div>
        <div class="progress-meta">
          <span class="progress-value">{{ progressPercent }}%</span>
          <span class="meta-sep">·</span>
          <span class="inline-stats">学习时长 {{ formattedTime }} · 积分 {{ score }}分 · 答题 {{ answeredCount }}/{{ totalQuestions }}</span>
        </div>
      </div>
    </header>

    <div class="player-body">
      <transition name="step-enter" mode="out-in">
        <main class="step-panel" v-if="currentStep" :key="currentStepIndex">
        <!-- PPT风格画布布局（所有步骤都使用） -->
        <div class="ppt-canvas-container">
          <div
            class="ppt-canvas"
            :style="canvasSectionStyle"
          >
            <!-- 步骤标题（作为画布内的组件） -->
            <div
              v-if="currentStep.title && !hasTitleComponent"
              class="canvas-title-component"
              :style="titleComponentStyle"
            >
              <h2>{{ currentStep.title }}</h2>
            </div>

            <!-- 步骤内容（作为画布内的组件） -->
            <div
              v-if="currentStepContent && !hasContentComponent"
              class="canvas-content-component"
              :style="contentComponentStyle"
              v-html="currentStepContent"
            />

            <!-- 交互组件渲染 -->
            <StepComponentRenderer
              v-for="component in (currentStep.components || [])"
              :key="component.id"
              :component="component"
            />

            <!-- 练习部分（画布内） -->
            <div
              v-if="currentStep.practice"
              class="canvas-practice-component"
              :style="practiceComponentStyle"
            >
              <div class="section-title">
                <span>📝 {{ currentStep.practice.title || '立即动手练习' }}</span>
                <small>完成练习可巩固操作步骤</small>
              </div>
              <ul class="practice-list">
                <li
                  v-for="(task, idx) in currentStep.practice.tasks"
                  :key="idx"
                  :class="{ done: practiceCompletion[currentStep.id]?.[idx] }"
                >
                  <label>
                    <input
                      type="checkbox"
                      :checked="practiceCompletion[currentStep.id]?.[idx] || false"
                      @change="togglePractice(currentStep.id, idx, $event)"
                    />
                    <span>{{ task }}</span>
                  </label>
                </li>
              </ul>
            </div>

            <!-- 问答部分（画布内） -->
            <div
              v-if="currentStep.questions && currentStep.questions.length"
              class="canvas-quiz-component"
              :style="quizComponentStyle"
            >
              <div class="section-title">
                <span>🧠 课堂问答</span>
                <small>答题可获得积分</small>
              </div>
              <div
                v-for="question in currentStep.questions"
                :key="question.id"
                class="quiz-item"
              >
                <p class="quiz-question">{{ question.question }}</p>
                <ul class="quiz-options">
                  <li
                    v-for="(option, idx) in question.options"
                    :key="idx"
                    :class="optionClass(question.id, option)"
                    @click="handleSelectOption(question, option)"
                  >
                    <span class="option-label">{{ optionLabel(idx) }}</span>
                    <span class="option-text">{{ option }}</span>
                  </li>
                </ul>
                <div v-if="answeredMap[question.id]" class="quiz-feedback">
                  <span v-if="correctMap[question.id]" class="correct">✅ 回答正确！</span>
                  <span v-else class="incorrect">❌ 回答错误</span>
                  <div v-if="question.explanation" class="explanation">
                    解析：{{ question.explanation }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 提交部分（画布外，因为需要交互） -->
        <section v-if="currentStep.submission?.enable" class="step-section submission-section">
          <div class="section-title">
            <span>📝 {{ currentStep.practice.title || '立即动手练习' }}</span>
            <small>完成练习可巩固操作步骤</small>
          </div>
          <ul class="practice-list">
            <li
              v-for="(task, idx) in currentStep.practice.tasks"
              :key="idx"
              :class="{ done: practiceCompletion[currentStep.id]?.[idx] }"
            >
              <label>
                <input
                  type="checkbox"
                  :checked="practiceCompletion[currentStep.id]?.[idx] || false"
                  @change="togglePractice(currentStep.id, idx, $event)"
                />
                <span>{{ task }}</span>
              </label>
            </li>
          </ul>
        </section>
        </main>
      </transition>

      <aside class="context-panel" v-if="courseData">
        <section class="context-card">
          <h4>📚 步骤大纲</h4>
          <ul class="outline-list">
            <li
              v-for="(step, idx) in courseData.steps"
              :key="step.id"
              :class="{ active: idx === currentStepIndex }"
              @click="jumpToStep(idx)"
            >
              <span>步骤 {{ idx + 1 }}</span>
              <p>{{ step.title }}</p>
            </li>
          </ul>
        </section>

        <section v-if="preparations.length" class="context-card">
          <h4>🛠️ 准备工作</h4>
          <ul class="simple-list">
            <li v-for="(item, idx) in preparations" :key="idx">
              {{ item }}
            </li>
          </ul>
        </section>

        <section v-if="goals.length" class="context-card">
          <h4>🎯 学习目标</h4>
          <div class="goal-groups">
            <div v-for="group in goals" :key="group.title" class="goal-group">
              <p class="goal-title">{{ group.title }}</p>
              <ul>
                <li v-for="(item, idx) in group.items" :key="idx">{{ item }}</li>
              </ul>
            </div>
          </div>
        </section>
      </aside>
    </div>

    <footer class="player-actions">
      <button class="btn-secondary" :disabled="currentStepIndex === 0" @click="prevStep">
        ◀ 上一步
      </button>
      <div class="action-right">
        <button
          v-if="currentStep && showSubmitButton(currentStep)"
          class="btn-primary"
          @click="handleSubmit"
        >
          提交任务
        </button>
        <button
          v-if="!currentStep || (!showSubmitButton(currentStep) && isLastStep)"
          class="btn-success"
          @click="completeCourse"
        >
          🎉 完成学习
        </button>
        <button
          v-else-if="!showSubmitButton(currentStep as any)"
          class="btn-primary"
          @click="nextStep"
        >
          下一步 ▶
        </button>
      </div>
    </footer>

    <div v-if="showCard && activeCard" class="modal-overlay">
      <div class="modal-card">
        <button class="modal-close" @click="closeKnowledgeCard">×</button>
        <div class="modal-icon">{{ activeCard.icon }}</div>
        <h4>{{ activeCard.title }}</h4>
        <p>{{ activeCard.content }}</p>
      </div>
    </div>

    <div v-if="showCompletion" class="completion-overlay">
      <div class="completion-modal">
        <div class="emoji">🎊</div>
        <h3>恭喜完成本关卡！</h3>
        <p>总用时 {{ formattedTime }} · 积分 {{ score }} · 答题 {{ answeredCount }}/{{ totalQuestions }}</p>
        <button class="btn-primary" @click="closeCompletion">继续学习</button>
      </div>
    </div>
  </div>
  <div v-else class="player-empty">
    暂无可解析的教案内容
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import StepComponentRenderer from '../canvas/StepComponentRenderer.vue'
import EnhancedProgressBar from '../ui/EnhancedProgressBar.vue'
import { getFeedbackSystem } from '../../utils/feedbackSystem'
import { AchievementSystem, type AchievementState } from '../../utils/achievementSystem'
import { ComboSystem } from '../../utils/comboSystem'
import type {
  CourseData,
  CourseStep,
  CourseQuestion,
  KnowledgeCard,
} from '../../types/coursePlayer'

const DEFAULT_QUESTION_POINTS = 5
const DEFAULT_PRACTICE_POINTS = 10
const DEFAULT_COMPLETE_BONUS = 20

const props = defineProps<{
  courseData: CourseData | null
}>()

const currentStepIndex = ref(0)
const score = ref(0)
const timeSpent = ref(0)
const answeredMap = ref<Record<string, string>>({})
const correctMap = ref<Record<string, boolean>>({})
const practiceCompletion = ref<Record<string, boolean[]>>({})
const submissions = ref<Record<string, { fileName?: string; text?: string }>>({})
const submissionTexts = ref<Record<string, string>>({})
const submissionFiles = ref<Record<string, string>>({})
const submissionStatuses = ref<Record<string, string>>({})
const showCard = ref(false)
const activeCard = ref<KnowledgeCard | null>(null)
const showCompletion = ref(false)
const collectedCards = ref<KnowledgeCard[]>([])
const badges = ref<Array<{ name: string; icon: string }>>([])

const timer = ref<number | null>(null)
const stepStartTime = ref<number>(Date.now())

// 游戏化系统
const feedbackSystem = getFeedbackSystem()
const achievementSystem = new AchievementSystem((achievement) => {
  feedbackSystem.showParticleEffect('achievement')
  feedbackSystem.showToast(`🏆 解锁成就：${achievement.name}！`, 'success')
  badges.value.push({ name: achievement.name, icon: achievement.icon })
})
const comboSystem = new ComboSystem(
  (count) => {
    // 连击回调
  },
  (count, bonus) => {
    score.value += bonus
    feedbackSystem.showToast(`🔥 ${count}连击！额外获得${bonus}分`, 'success')
  }
)

const totalSteps = computed(() => props.courseData?.steps.length ?? 0)
// 画布区域样式（所有步骤都使用PPT风格）
const canvasSectionStyle = computed(() => {
  const config = currentStep.value?.canvasConfig || {
    width: 1920,
    height: 1080,
    backgroundColor: '#ffffff',
  }
  const viewportWidth = window.innerWidth - 400
  const viewportHeight = window.innerHeight - 200
  const scaleX = viewportWidth / config.width
  const scaleY = viewportHeight / config.height
  const scale = Math.min(scaleX, scaleY, 1)
  return {
    position: 'relative' as const,
    width: `${config.width}px`,
    height: `${config.height}px`,
    backgroundColor: config.backgroundColor || '#ffffff',
    backgroundImage: config.backgroundImage ? `url(${config.backgroundImage})` : 'none',
    transform: `scale(${scale})`,
    transformOrigin: 'top center' as const,
    margin: '0 auto',
    overflow: 'hidden' as const,
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  }
})

const hasTitleComponent = computed(() => {
  if (!currentStep.value?.components) return false
  const titleComponent = currentStep.value.components.find(
    c => c.type === 'text' && c.config?.content?.includes(currentStep.value?.title || '')
  )
  return !!titleComponent?.position
})

const hasContentComponent = computed(() => {
  if (!currentStep.value?.components) return false
  const contentComponents = currentStep.value.components.filter(c => c.type === 'text')
  return contentComponents.length > 0 && contentComponents.some(c => c.position)
})

const practiceComponentStyle = computed(() => {
  return {
    position: 'absolute',
    bottom: '100px',
    left: '100px',
    right: '100px',
    zIndex: 5,
    maxHeight: '300px',
    overflow: 'auto',
  }
})

const quizComponentStyle = computed(() => {
  return {
    position: 'absolute',
    bottom: '100px',
    left: '100px',
    right: '100px',
    zIndex: 5,
    maxHeight: '400px',
    overflow: 'auto',
  }
})

const titleComponentStyle = computed(() => {
  const titleComponent = currentStep.value?.components?.find(c => c.type === 'text' && c.config?.content?.includes(currentStep.value?.title || ''))
  if (titleComponent?.position) {
    return {} as const
  }
  return {
    position: 'absolute' as const,
    top: '80px',
    left: '100px',
    right: '100px',
    zIndex: 10,
  }
})

const contentComponentStyle = computed(() => {
  const contentComponents = currentStep.value?.components?.filter(c => c.type === 'text')
  if (contentComponents && contentComponents.length > 0) {
    return {}
  }
  return {
    position: 'absolute',
    top: '200px',
    left: '100px',
    right: '100px',
    bottom: '100px',
    zIndex: 5,
    overflow: 'auto',
  }
})

const currentStep = computed<CourseStep | null>(() => {
  if (!props.courseData) return null
  return props.courseData.steps[currentStepIndex.value] ?? null
})

const currentStepContent = computed(() => {
  if (!currentStep.value) return ''
  return currentStep.value.contentHtml || currentStep.value.content || ''
})

const totalQuestions = computed(() =>
  props.courseData?.steps.reduce(
    (sum, step) => sum + (step.questions?.length || 0),
    0
  ) ?? 0
)
const answeredCount = computed(
  () => Object.keys(answeredMap.value).length
)
const progressPercent = computed(() =>
  totalSteps.value ? Math.round(((currentStepIndex.value + 1) / totalSteps.value) * 100) : 0
)
const formattedTime = computed(() => {
  const minutes = Math.floor(timeSpent.value / 60)
  const seconds = timeSpent.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})
const isLastStep = computed(() => currentStepIndex.value === totalSteps.value - 1)

const headerTitle = computed(() => props.courseData?.meta?.title || '交互式关卡预览')
const preparations = computed(() => props.courseData?.meta?.preparations ?? [])
const goals = computed(
  () =>
    props.courseData?.meta?.goals ??
    []
)

const scoreConfig = computed(() => {
  const cfg = props.courseData?.meta?.scoreConfig || {}
  return {
    perQuestion: cfg.perQuestion ?? DEFAULT_QUESTION_POINTS,
    perPractice: cfg.perPractice ?? DEFAULT_PRACTICE_POINTS,
    completeBonus: cfg.completeBonus ?? DEFAULT_COMPLETE_BONUS,
  }
})

watch(
  () => props.courseData,
  () => {
    resetState()
  },
  { immediate: true }
)

onMounted(() => {
  startTimer()
  achievementSystem.loadUnlocked()
  stepStartTime.value = Date.now()
  loadProgress()
})

onBeforeUnmount(() => {
  stopTimer()
})

function resetState() {
  currentStepIndex.value = 0
  score.value = 0
  timeSpent.value = 0
  stepStartTime.value = Date.now()
  answeredMap.value = {}
  correctMap.value = {}
  practiceCompletion.value = {}
  submissions.value = {}
  submissionTexts.value = {}
  submissionFiles.value = {}
  submissionStatuses.value = {}
  showCard.value = false
  activeCard.value = null
  showCompletion.value = false
  comboSystem.reset()
  achievementSystem.loadUnlocked()
  stopTimer()
  startTimer()
}

function startTimer() {
  stopTimer()
  timer.value = window.setInterval(() => {
    timeSpent.value += 1
  }, 1000)
}

function stopTimer() {
  if (timer.value) {
    clearInterval(timer.value)
    timer.value = null
  }
}

function nextStep() {
  if (currentStepIndex.value < totalSteps.value - 1) {
    const stepTime = Math.floor((Date.now() - stepStartTime.value) / 1000)
    stepStartTime.value = Date.now()
    currentStepIndex.value += 1
    checkAchievements()
  }
}

function prevStep() {
  if (currentStepIndex.value > 0) {
    currentStepIndex.value -= 1
  }
}

function jumpToStep(index: number) {
  if (index >= 0 && index < totalSteps.value) {
    currentStepIndex.value = index
  }
}

function optionLabel(index: number) {
  return String.fromCharCode(65 + index)
}

function isAnswered(questionId: string) {
  return Boolean(answeredMap.value[questionId])
}

function isCorrect(question: CourseQuestion) {
  return correctMap.value[question.id]
}

function optionClass(questionId: string, option: string) {
  const answer = answeredMap.value[questionId]
  return {
    selected: answer === option,
    correct:
      !!props.courseData &&
      (answer === option && option === findQuestionAnswer(questionId)),
    incorrect: answer === option && option !== findQuestionAnswer(questionId),
  }
}

function findQuestionAnswer(questionId: string): string | undefined {
  for (const step of props.courseData?.steps || []) {
    const found = step.questions?.find((q) => q.id === questionId)
    if (found) return found.answer
  }
  return undefined
}

function handleSelectOption(question: CourseQuestion, option: string) {
  answeredMap.value = { ...answeredMap.value, [question.id]: option }
  const correct = option === question.answer
  if (correctMap.value[question.id] && !correct) {
    score.value = Math.max(0, score.value - scoreConfig.value.perQuestion)
  }
  if (!correctMap.value[question.id] && correct) {
    const points = scoreConfig.value.perQuestion
    score.value += points
    feedbackSystem.showAnswerFeedback(true, points)
    comboSystem.addCombo()
  } else if (!correct) {
    feedbackSystem.showAnswerFeedback(false, 0)
    comboSystem.reset()
  }
  correctMap.value = { ...correctMap.value, [question.id]: correct }
  checkAchievements()
}

function togglePractice(stepId: string, index: number, event: Event) {
  const checked = (event.target as HTMLInputElement).checked
  const current = practiceCompletion.value[stepId] || []
  current[index] = checked
  practiceCompletion.value = {
    ...practiceCompletion.value,
    [stepId]: [...current],
  }
}

function onSubmissionFileChange(stepId: string, event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  submissionFiles.value = {
    ...submissionFiles.value,
    [stepId]: file ? file.name : '',
  }
}

function onSubmissionTextInput(stepId: string, value: string) {
  submissionTexts.value = {
    ...submissionTexts.value,
    [stepId]: value,
  }
}

function openKnowledgeCard(card: KnowledgeCard) {
  activeCard.value = card
  showCard.value = true
  if (!collectedCards.value.find((c) => c.title === card.title)) {
    collectedCards.value.push(card)
  }
}

function closeKnowledgeCard() {
  showCard.value = false
  activeCard.value = null
}

function completeCourse() {
  const bonus = scoreConfig.value.completeBonus
  score.value += bonus
  feedbackSystem.showParticleEffect('levelup')
  feedbackSystem.showToast(`🎉 完成学习！获得${bonus}分奖励！`, 'success')
  checkAchievements()
  showCompletion.value = true
  stopTimer()
}

function saveProgress() {
  if (typeof localStorage !== 'undefined') {
    const progressData = {
      levelId: props.courseData?.meta?.title,
      currentStepIndex: currentStepIndex.value,
      score: score.value,
      timeSpent: timeSpent.value,
      answeredMap: answeredMap.value,
      correctMap: correctMap.value,
      practiceCompletion: practiceCompletion.value,
      collectedCards: collectedCards.value,
      badges: badges.value,
      timestamp: Date.now()
    }
    localStorage.setItem('learning_progress', JSON.stringify(progressData))
  }
}

function loadProgress() {
  if (typeof localStorage !== 'undefined') {
    const saved = localStorage.getItem('learning_progress')
    if (saved) {
      try {
        const progressData = JSON.parse(saved)
      } catch (error) {
        console.error('Failed to load progress:', error)
      }
    }
  }
}

watch([currentStepIndex, score], () => {
  saveProgress()
}, { deep: true })

defineExpose({
  currentStepIndex,
  progressPercent,
  formattedTime,
  totalSteps,
  answeredCount,
  totalQuestions,
  score,
  collectedCards,
  badges,
  jumpToStep,
  openKnowledgeCard,
})

function closeCompletion() {
  showCompletion.value = false
  startTimer()
}

function showSubmitButton(step: CourseStep): boolean {
  return Boolean(step.practice || (step.questions && step.questions.length) || step.submission?.enable)
}

function handleSubmit() {
  const step = currentStep.value
  if (!step) return
  if (step.practice) {
    const existing = practiceCompletion.value[step.id] || []
    const updated = step.practice.tasks.map((_t, idx) => existing[idx] || true)
    practiceCompletion.value = {
      ...practiceCompletion.value,
      [step.id]: updated,
    }
    submissions.value[step.id] = {
      text: '已完成本步骤练习',
    }
    score.value += scoreConfig.value.perPractice
    if (step.knowledgeCard) {
      openKnowledgeCard(step.knowledgeCard)
    }
  }
  if (step.submission?.enable) {
    const text = submissionTexts.value[step.id] || ''
    const fileName = submissionFiles.value[step.id] || ''
    if (!text && !fileName) {
      alert('请上传附件或填写说明后再提交')
      return
    }
    submissions.value[step.id] = {
      ...submissions.value[step.id],
      text,
      fileName,
    }
    submissionStatuses.value[step.id] =
      step.submission.successMessage || '提交成功，等待教师评阅'
    score.value += scoreConfig.value.perPractice
  }
  checkAchievements()
  if (!isLastStep.value) {
    nextStep()
  } else {
    score.value += scoreConfig.value.completeBonus
    completeCourse()
  }
}

function checkAchievements() {
  const correctCount = Object.values(correctMap.value).filter((v) => v).length
  const stepTime = Math.floor((Date.now() - stepStartTime.value) / 1000)
  const state: AchievementState = {
    completedSteps: currentStepIndex.value + 1,
    correctAnswers: correctCount,
    totalQuestions: totalQuestions.value,
    collectedCards: collectedCards.value.length,
    currentStepTime: stepTime,
    progressPercent: progressPercent.value,
    correctRate: totalQuestions.value > 0 ? correctCount / totalQuestions.value : 0
  }
  achievementSystem.checkAchievements(state)
}
</script>

<style scoped>
.player-header{
  padding: 12px 24px;
  background: rgba(2,6,23,0.92);
  color: #e6eefc;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}
.header-top{
  display:flex;
  justify-content:space-between;
  align-items:flex-end;
  gap:16px;
}
.title-block h2{
  margin:0;
  font-size:20px;
  color:#e6eefc;
}
.subtitle{
  margin:4px 0 0;
  color:#9aa4b2;
  font-size:13px;
}
.inline-stats{
  color:#cbd5e1;
  font-size:13px;
  white-space:nowrap;
}
.progress-row{
  display:flex;
  align-items:center;
  gap:12px;
  margin-top:8px;
  padding-bottom:6px;
}
.progress-bar-wrap{ flex:1; min-width:200px; }
.progress-meta{ display:flex; align-items:center; gap:8px; white-space:nowrap; margin-left:12px; color:#cbd5e1; }
.progress-value{ color:#cbd5e1; font-weight:600; min-width:40px; text-align:right; }
.meta-sep{ color:#6b7280; opacity:0.6; }
.inline-stats{ color:#cbd5e1; font-size:13px; }

/* reduce spacing above canvas */
.player-body{ padding-top:8px; }

/* reduce top/bottom margins of ppt-canvas container */
.ppt-canvas-container{ padding: 8px 0 16px; }
.ppt-canvas{ margin-top:8px; }

/* Compact context panel spacing */
.context-panel{ width:300px; }

/* footer actions compact */
.player-actions{ padding:12px 24px; display:flex; justify-content:space-between; align-items:center; gap:12px; }
.player-actions .btn-secondary, .player-actions .btn-primary { padding:6px 12px; }
</style>


