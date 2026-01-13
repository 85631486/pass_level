<template>
  <div class="learning-page">
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <div class="nav-left">
        <el-button @click="backToList" icon="ArrowLeft" circle />
        <h2>{{ taskData?.task_name }}</h2>
      </div>
      <div class="nav-center">
        <el-progress
          :percentage="progressPercentage"
          :stroke-width="10"
          :text-inside="true"
          style="width: 400px"
        />
      </div>
      <div class="nav-right">
        <div class="points-display">
          <el-icon color="#ffa500"><Trophy /></el-icon>
          <span>{{ learningStore.currentProgress.total_points }} 积分</span>
        </div>
        <el-button type="primary" @click="openDrawer('summary')">
          学习进度
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <div class="content-area" v-if="currentOperation">
        <!-- 关卡标题 -->
        <div class="operation-header">
          <div class="level-badge">
            <el-icon><Star /></el-icon>
            <span>第 {{ currentOperation.operation_order }} 关</span>
          </div>
          <h1>{{ currentOperation.operation_name }}</h1>
        </div>

        <!-- 操作说明 -->
        <el-card class="operation-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>操作说明</span>
            </div>
          </template>
          <div class="operation-description" v-html="currentOperation.description"></div>
        </el-card>

        <!-- 操作步骤 -->
        <el-card class="operation-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><List /></el-icon>
              <span>详细步骤</span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(step, index) in currentOperation.steps"
              :key="index"
              :timestamp="`步骤 ${index + 1}`"
            >
              {{ step }}
            </el-timeline-item>
          </el-timeline>
        </el-card>

        <!-- 练习任务 -->
        <el-card class="operation-card practice-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><Pointer /></el-icon>
              <span>立即动手</span>
            </div>
          </template>
          <div class="practice-content">
            <p>{{ currentOperation.practice_task }}</p>
          </div>
        </el-card>

        <!-- 知识卡片展示区 -->
        <div v-if="displayedKnowledgeCards.length > 0" class="knowledge-cards-area">
          <transition-group name="card-slide">
            <el-card
              v-for="card in displayedKnowledgeCards"
              :key="card.id"
              class="knowledge-card"
              :class="`card-type-${card.card_type}`"
              shadow="hover"
            >
              <div class="knowledge-card-header">
                <el-icon><Memo /></el-icon>
                <span>{{ card.card_title }}</span>
                <el-button
                  size="small"
                  type="success"
                  @click="collectCard(card)"
                  icon="Collection"
                  circle
                />
              </div>
              <div class="knowledge-card-content">
                {{ card.card_content }}
              </div>
            </el-card>
          </transition-group>
        </div>

        <!-- 提交区域 -->
        <el-card class="submit-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><Upload /></el-icon>
              <span>提交操作结果</span>
            </div>
          </template>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".png,.jpg,.jpeg,.gif,.pdf,.docx"
          >
            <template #trigger>
              <el-button type="primary" icon="UploadFilled">
                选择文件（截图或文档）
              </el-button>
            </template>
            <template #tip>
              <div class="el-upload__tip">
                支持 PNG、JPG、PDF、DOCX 格式，文件大小不超过 16MB
              </div>
            </template>
          </el-upload>

          <el-button
            v-if="selectedFile"
            type="success"
            @click="submitOperation"
            :loading="submitting"
            style="margin-top: 16px"
          >
            提交此操作
          </el-button>
        </el-card>

        <!-- 底部操作栏 -->
        <div class="bottom-actions">
          <el-button
            @click="previousOperation"
            :disabled="currentOperationIndex === 0"
            size="large"
          >
            上一步
          </el-button>
          <el-button
            v-if="currentOperationIndex < operations.length - 1"
            type="primary"
            @click="nextOperation"
            size="large"
          >
            下一步
          </el-button>
          <el-button
            v-else
            type="success"
            @click="completeAllOperations"
            size="large"
          >
            完成所有操作
          </el-button>
        </div>
      </div>
    </div>

    <!-- 右侧抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="drawerTitle"
      direction="rtl"
      size="500px"
    >
      <!-- 学习目标 -->
      <div v-if="drawerType === 'goals'">
        <h3>📌 学习目标</h3>
        <el-collapse>
          <el-collapse-item title="知识目标" name="1">
            <p>• 认识Excel的界面布局</p>
            <p>• 掌握10个最常用Excel操作</p>
            <p>• 理解单元格引用的概念</p>
          </el-collapse-item>
          <el-collapse-item title="技能目标" name="2">
            <p>• 熟练使用基本操作</p>
            <p>• 能够对数据进行筛选和排序</p>
            <p>• 能够向AI快速学习Excel操作</p>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- 提交记录 -->
      <div v-if="drawerType === 'submissions'">
        <h3>📝 我的提交记录</h3>
        <el-timeline>
          <el-timeline-item
            v-for="(sub, index) in submissionsList"
            :key="index"
            :timestamp="sub.timestamp"
            :color="sub.status === 'submitted' ? '#67C23A' : '#909399'"
          >
            <p><strong>{{ sub.operation_name }}</strong></p>
            <p>积分：+{{ sub.points }}</p>
          </el-timeline-item>
        </el-timeline>
      </div>

      <!-- 知识卡片收集箱 -->
      <div v-if="drawerType === 'cards'">
        <h3>💡 知识卡片收集箱</h3>
        <div class="collected-cards">
          <el-card
            v-for="card in learningStore.collectedCards"
            :key="card.id"
            class="mini-card"
            shadow="hover"
          >
            <h4>{{ card.card_title }}</h4>
            <p>{{ card.card_content }}</p>
          </el-card>
        </div>
      </div>

      <!-- 测试题答题区 -->
      <div v-if="drawerType === 'test'">
        <h3>❓ 统一测试</h3>
        <div v-for="(question, index) in unifiedQuestions" :key="question.id">
          <div class="question-item">
            <p class="question-text">{{ index + 1 }}. {{ question.question_text }}</p>
            <el-radio-group v-model="testAnswers[question.id]">
              <el-radio label="A">{{ question.option_a }}</el-radio>
              <el-radio label="B">{{ question.option_b }}</el-radio>
              <el-radio label="C">{{ question.option_c }}</el-radio>
              <el-radio label="D">{{ question.option_d }}</el-radio>
            </el-radio-group>
          </div>
        </div>
        <el-button
          type="primary"
          @click="submitUnifiedTest"
          :disabled="Object.keys(testAnswers).length === 0"
          style="width: 100%; margin-top: 20px"
        >
          提交测试
        </el-button>
      </div>

      <!-- 学习进度总览 -->
      <div v-if="drawerType === 'summary'">
        <h3>📊 学习进度</h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="已完成操作">
            {{ learningStore.currentProgress.operations_completed }} / {{ operations.length }}
          </el-descriptions-item>
          <el-descriptions-item label="总积分">
            {{ learningStore.currentProgress.total_points }}
          </el-descriptions-item>
          <el-descriptions-item label="答对题数">
            {{ learningStore.currentProgress.questions_correct }}
          </el-descriptions-item>
          <el-descriptions-item label="收集卡片">
            {{ learningStore.collectedCards.length }}
          </el-descriptions-item>
        </el-descriptions>

        <el-button
          v-if="learningStore.currentProgress.operations_completed >= operations.length"
          type="success"
          @click="finishLearning"
          style="width: 100%; margin-top: 20px"
          size="large"
        >
          完成学习
        </el-button>
      </div>
    </el-drawer>

    <!-- 即时测试题弹窗 -->
    <el-dialog
      v-model="questionDialogVisible"
      title="课堂问答"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="currentQuestion">
        <p class="question-text">{{ currentQuestion.question_text }}</p>
        <el-radio-group v-model="currentAnswer" style="display: flex; flex-direction: column; gap: 12px">
          <el-radio label="A">{{ currentQuestion.option_a }}</el-radio>
          <el-radio label="B">{{ currentQuestion.option_b }}</el-radio>
          <el-radio label="C">{{ currentQuestion.option_c }}</el-radio>
          <el-radio label="D">{{ currentQuestion.option_d }}</el-radio>
        </el-radio-group>
      </div>
      <template #footer>
        <el-button @click="questionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitInstantAnswer" :disabled="!currentAnswer">
          提交答案
        </el-button>
      </template>
    </el-dialog>

    <!-- 答案结果弹窗 -->
    <el-dialog
      v-model="resultDialogVisible"
      :title="answerResult.is_correct ? '✅ 回答正确' : '❌ 回答错误'"
      width="500px"
    >
      <el-result
        :icon="answerResult.is_correct ? 'success' : 'error'"
        :title="answerResult.is_correct ? '恭喜你答对了！' : '很遗憾，答错了'"
      >
        <template #sub-title>
          <p>正确答案：{{ answerResult.correct_answer }}</p>
          <p style="margin-top: 10px">{{ answerResult.explanation }}</p>
          <p style="margin-top: 10px; color: #ffa500">
            获得积分：+{{ answerResult.points_earned }}
          </p>
        </template>
      </el-result>
    </el-dialog>

    <!-- 浮动按钮组 -->
    <div class="floating-buttons">
      <el-button
        circle
        size="large"
        @click="openDrawer('goals')"
        title="学习目标"
      >
        <el-icon><Flag /></el-icon>
      </el-button>
      <el-button
        circle
        size="large"
        @click="openDrawer('submissions')"
        title="提交记录"
      >
        <el-icon><Document /></el-icon>
      </el-button>
      <el-button
        circle
        size="large"
        @click="openDrawer('cards')"
        title="知识卡片"
      >
        <el-icon><Collection /></el-icon>
        <el-badge
          :value="learningStore.collectedCards.length"
          :max="99"
          v-if="learningStore.collectedCards.length > 0"
          class="card-badge"
        />
      </el-button>
      <el-button
        circle
        size="large"
        type="warning"
        @click="openDrawer('test')"
        title="统一测试"
      >
        <el-icon><EditPen /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useLearningStore } from '@/stores/learning'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const learningStore = useLearningStore()

const taskId = ref(parseInt(route.params.taskId))
const taskData = ref(null)
const operations = ref([])
const currentOperationIndex = ref(0)
const currentOperation = computed(() => operations.value[currentOperationIndex.value])

const displayedKnowledgeCards = ref([])
const selectedFile = ref(null)
const submitting = ref(false)

const drawerVisible = ref(false)
const drawerType = ref('')
const drawerTitle = ref('')

const questionDialogVisible = ref(false)
const currentQuestion = ref(null)
const currentAnswer = ref('')

const resultDialogVisible = ref(false)
const answerResult = ref({})

const unifiedQuestions = ref([])
const testAnswers = ref({})

const submissionsList = ref([])

const progressPercentage = computed(() => {
  if (operations.value.length === 0) return 0
  return Math.round((learningStore.currentProgress.operations_completed / operations.value.length) * 100)
})

onMounted(async () => {
  await loadTaskData()
  await loadProgress()
  await loadUnifiedQuestions()
})

watch(currentOperationIndex, async (newIndex) => {
  await loadOperationDetail(operations.value[newIndex].id)
})

const loadTaskData = async () => {
  try {
    const res = await api.getTaskDetail(taskId.value)
    if (res.success) {
      taskData.value = res.data
      operations.value = res.data.operations || []
      if (operations.value.length > 0) {
        await loadOperationDetail(operations.value[0].id)
      }
    }
  } catch (error) {
    console.error('加载任务数据失败', error)
  }
}

const loadProgress = async () => {
  try {
    const res = await api.getProgress(userStore.user.id, taskId.value)
    if (res.success) {
      learningStore.updateProgress(res.data)
      currentOperationIndex.value = res.data.current_operation || 0
    }
  } catch (error) {
    console.error('加载进度失败', error)
  }
}

const loadOperationDetail = async (operationId) => {
  try {
    const res = await api.getOperationDetail(operationId)
    if (res.success) {
      const operation = res.data
      // 更新当前操作详情
      Object.assign(currentOperation.value, operation)

      // 显示该操作的知识卡片
      displayedKnowledgeCards.value = operation.knowledge_cards || []

      // 如果有即时测试题，弹出
      if (operation.instant_questions && operation.instant_questions.length > 0) {
        setTimeout(() => {
          showInstantQuestion(operation.instant_questions[0])
        }, 1000)
      }
    }
  } catch (error) {
    console.error('加载操作详情失败', error)
  }
}

const handleFileChange = (file) => {
  selectedFile.value = file
}

const submitOperation = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value.raw)
    formData.append('student_id', userStore.user.id)
    formData.append('task_id', taskId.value)

    const res = await api.submitOperation(currentOperation.value.id, formData)
    if (res.success) {
      ElMessage.success(`提交成功！获得 ${res.data.points_earned} 积分`)
      learningStore.recordSubmission(currentOperation.value.id, res.data)

      // 更新进度
      await loadProgress()

      // 清空文件选择
      selectedFile.value = null
    }
  } catch (error) {
    console.error('提交失败', error)
  } finally {
    submitting.value = false
  }
}

const showInstantQuestion = (question) => {
  currentQuestion.value = question
  currentAnswer.value = ''
  questionDialogVisible.value = true
}

const submitInstantAnswer = async () => {
  try {
    const res = await api.answerInstantQuestion(currentQuestion.value.id, {
      student_id: userStore.user.id,
      operation_id: currentOperation.value.id,
      answer: currentAnswer.value
    })

    if (res.success) {
      answerResult.value = res.data
      questionDialogVisible.value = false
      resultDialogVisible.value = true

      if (res.data.is_correct) {
        learningStore.updateProgress({
          total_points: learningStore.currentProgress.total_points + res.data.points_earned,
          questions_correct: learningStore.currentProgress.questions_correct + 1
        })
      }
    }
  } catch (error) {
    console.error('提交答案失败', error)
  }
}

const collectCard = async (card) => {
  try {
    const res = await api.collectKnowledgeCard({
      student_id: userStore.user.id,
      card_id: card.id
    })
    if (res.success) {
      learningStore.collectCard(card)
      ElMessage.success('知识卡片已收集')
    }
  } catch (error) {
    console.error('收集卡片失败', error)
  }
}

const previousOperation = () => {
  if (currentOperationIndex.value > 0) {
    currentOperationIndex.value--
  }
}

const nextOperation = () => {
  if (currentOperationIndex.value < operations.value.length - 1) {
    currentOperationIndex.value++
  }
}

const completeAllOperations = async () => {
  await ElMessageBox.confirm(
    '确认已完成所有操作？完成后可以进行统一测试。',
    '提示',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'info'
    }
  )

  openDrawer('test')
}

const loadUnifiedQuestions = async () => {
  try {
    const res = await api.getUnifiedQuestions(taskId.value)
    if (res.success) {
      unifiedQuestions.value = res.data
    }
  } catch (error) {
    console.error('加载统一测试题失败', error)
  }
}

const submitUnifiedTest = async () => {
  try {
    const res = await api.submitUnifiedTest(taskId.value, {
      student_id: userStore.user.id,
      answers: testAnswers.value
    })

    if (res.success) {
      ElMessage.success(
        `测试完成！答对 ${res.data.correct_count}/${res.data.total_questions} 题，获得 ${res.data.total_points} 积分`
      )
      drawerVisible.value = false
    }
  } catch (error) {
    console.error('提交测试失败', error)
  }
}

const finishLearning = async () => {
  try {
    const res = await api.completeTask({
      student_id: userStore.user.id,
      task_id: taskId.value
    })

    if (res.success) {
      ElMessage.success('恭喜完成学习！')
      router.push(`/summary/${taskId.value}`)
    }
  } catch (error) {
    console.error('完成学习失败', error)
  }
}

const openDrawer = (type) => {
  drawerType.value = type
  const titles = {
    goals: '学习目标',
    submissions: '提交记录',
    cards: '知识卡片收集箱',
    test: '统一测试',
    summary: '学习进度'
  }
  drawerTitle.value = titles[type]
  drawerVisible.value = true
}

const backToList = () => {
  router.push('/tasks')
}
</script>

<style scoped>
.learning-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-left h2 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.points-display {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #ffa500;
  margin-right: 16px;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.operation-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.level-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 8px 20px;
  border-radius: 20px;
  font-weight: 600;
}

.operation-header h1 {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin: 0;
}

.operation-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.operation-description {
  line-height: 1.8;
  color: #606266;
}

.practice-card {
  background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
  border: none;
}

.practice-content {
  font-size: 16px;
  font-weight: 500;
  color: #2d3436;
}

.knowledge-cards-area {
  position: fixed;
  right: 540px;
  top: 120px;
  width: 320px;
  z-index: 99;
}

.knowledge-card {
  margin-bottom: 16px;
  border-left: 4px solid;
}

.card-type-tip {
  border-left-color: #409eff;
}

.card-type-warning {
  border-left-color: #ffa500;
}

.card-type-info {
  border-left-color: #909399;
}

.card-type-success {
  border-left-color: #67c23a;
}

.knowledge-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 600;
  color: #303133;
}

.knowledge-card-content {
  line-height: 1.6;
  color: #606266;
}

.submit-card {
  margin-top: 32px;
}

.bottom-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.floating-buttons {
  position: fixed;
  right: 32px;
  top: 120px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 1000;
}

.question-text {
  font-size: 16px;
  line-height: 1.8;
  margin-bottom: 16px;
  color: #303133;
}

.question-item {
  margin-bottom: 24px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.collected-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mini-card {
  cursor: default;
}

.mini-card h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #303133;
}

.mini-card p {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.card-slide-enter-active,
.card-slide-leave-active {
  transition: all 0.5s ease;
}

.card-slide-enter-from {
  transform: translateX(100px);
  opacity: 0;
}

.card-slide-leave-to {
  transform: translateX(-100px);
  opacity: 0;
}
</style>
