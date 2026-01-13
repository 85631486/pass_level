import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLearningStore = defineStore('learning', () => {
  // 当前任务进度
  const currentProgress = ref({
    task_id: null,
    current_operation: 0,
    operations_completed: 0,
    total_points: 0,
    questions_correct: 0,
    status: 'not_started'
  })

  // 收集的知识卡片
  const collectedCards = ref([])

  // 获得的徽章
  const badges = ref([])

  // 操作提交记录
  const submissions = ref({})

  // 更新进度
  function updateProgress(progress) {
    currentProgress.value = { ...currentProgress.value, ...progress }
  }

  // 收集知识卡片
  function collectCard(card) {
    if (!collectedCards.value.find(c => c.id === card.id)) {
      collectedCards.value.push(card)
    }
  }

  // 添加徽章
  function addBadge(badge) {
    if (!badges.value.find(b => b.id === badge.id)) {
      badges.value.push(badge)
    }
  }

  // 记录提交
  function recordSubmission(operationId, data) {
    submissions.value[operationId] = data
  }

  // 重置学习数据
  function reset() {
    currentProgress.value = {
      task_id: null,
      current_operation: 0,
      operations_completed: 0,
      total_points: 0,
      questions_correct: 0,
      status: 'not_started'
    }
    collectedCards.value = []
    submissions.value = {}
  }

  return {
    currentProgress,
    collectedCards,
    badges,
    submissions,
    updateProgress,
    collectCard,
    addBadge,
    recordSubmission,
    reset
  }
})
