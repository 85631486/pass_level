<template>
  <div class="summary-page">
    <div class="summary-container">
      <div class="summary-header">
        <el-icon :size="80" color="#67c23a"><CircleCheck /></el-icon>
        <h1>🎉 恭喜完成学习！</h1>
        <p>{{ summary.student_name }}同学，你已完成《{{ summary.task_name }}》的学习</p>
      </div>

      <el-card class="summary-card" shadow="always">
        <h2>📊 学习数据统计</h2>
        <el-row :gutter="24" style="margin-top: 24px">
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-value">{{ summary.total_points }}</div>
              <div class="stat-label">总积分</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-value">{{ summary.operations_completed }}</div>
              <div class="stat-label">完成操作</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-value">{{ summary.time_spent_minutes }}分钟</div>
              <div class="stat-label">学习时长</div>
            </div>
          </el-col>
        </el-row>

        <el-divider />

        <h3>📝 答题情况</h3>
        <el-row :gutter="24" style="margin-top: 16px">
          <el-col :span="12">
            <el-statistic title="即时测试题">
              <template #suffix>
                / {{ summary.instant_questions_total }}
              </template>
              {{ summary.instant_questions_correct }}
            </el-statistic>
            <el-progress
              :percentage="
                Math.round((summary.instant_questions_correct / summary.instant_questions_total) * 100)
              "
              :stroke-width="12"
              style="margin-top: 8px"
            />
          </el-col>
          <el-col :span="12">
            <el-statistic title="统一测试题">
              <template #suffix>
                / {{ summary.unified_questions_total }}
              </template>
              {{ summary.unified_questions_correct }}
            </el-statistic>
            <el-progress
              :percentage="
                Math.round((summary.unified_questions_correct / summary.unified_questions_total) * 100)
              "
              :stroke-width="12"
              style="margin-top: 8px"
            />
          </el-col>
        </el-row>

        <el-divider />

        <h3>🏆 获得的徽章</h3>
        <div class="badges-area">
          <el-empty v-if="summary.badges?.length === 0" description="暂无徽章" />
          <div v-else class="badges-grid">
            <div
              v-for="badge in summary.badges"
              :key="badge.id"
              class="badge-item"
            >
              <el-icon :size="60" color="#ffa500"><Medal /></el-icon>
              <div class="badge-name">{{ badge.badge_name }}</div>
              <div class="badge-desc">{{ badge.badge_description }}</div>
            </div>
          </div>
        </div>

        <el-divider />

        <h3>📚 知识卡片收集</h3>
        <el-statistic
          title="已收集知识卡片"
          :value="summary.knowledge_cards_collected"
        />

        <el-divider />

        <h3>🎯 完成度评价</h3>
        <el-progress
          :percentage="summary.completion_rate"
          :stroke-width="20"
          :text-inside="true"
          status="success"
        />
        <div class="evaluation-text">
          <p v-if="summary.completion_rate === 100">
            <strong>优秀！</strong>你已完成所有操作任务，表现非常出色！
          </p>
          <p v-else-if="summary.completion_rate >= 80">
            <strong>良好！</strong>你完成了大部分操作，继续加油！
          </p>
          <p v-else>
            <strong>需要努力！</strong>还有一些操作未完成，建议继续学习。
          </p>
        </div>
      </el-card>

      <div class="actions">
        <el-button size="large" @click="backToTasks">返回任务列表</el-button>
        <el-button type="primary" size="large" @click="downloadReport">
          下载学习报告
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const taskId = ref(parseInt(route.params.taskId))
const summary = ref({
  student_name: '',
  task_name: '',
  total_points: 0,
  operations_completed: 0,
  total_operations: 0,
  instant_questions_correct: 0,
  instant_questions_total: 0,
  unified_questions_correct: 0,
  unified_questions_total: 0,
  knowledge_cards_collected: 0,
  badges_earned: 0,
  badges: [],
  time_spent_minutes: 0,
  completion_rate: 0,
  status: ''
})

onMounted(async () => {
  await loadSummary()
})

const loadSummary = async () => {
  try {
    const res = await api.getLearningSummary(userStore.user.id, taskId.value)
    if (res.success) {
      summary.value = res.data
    }
  } catch (error) {
    console.error('加载学习总结失败', error)
  }
}

const backToTasks = () => {
  router.push('/tasks')
}

const downloadReport = () => {
  ElMessage.info('下载功能开发中...')
  // TODO: 实现PDF报告生成和下载
}
</script>

<style scoped>
.summary-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.summary-container {
  max-width: 900px;
  margin: 0 auto;
}

.summary-header {
  text-align: center;
  color: white;
  margin-bottom: 40px;
}

.summary-header h1 {
  font-size: 36px;
  margin: 20px 0 10px 0;
}

.summary-header p {
  font-size: 18px;
  opacity: 0.9;
}

.summary-card {
  padding: 20px;
  border-radius: 16px;
}

.summary-card h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 20px;
}

.summary-card h3 {
  font-size: 18px;
  color: #606266;
  margin: 16px 0;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 12px;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.badges-area {
  margin-top: 16px;
}

.badges-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 20px;
  margin-top: 16px;
}

.badge-item {
  text-align: center;
  padding: 20px;
  background: #fff9e6;
  border-radius: 12px;
  border: 2px solid #ffd666;
}

.badge-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 12px 0 8px 0;
}

.badge-desc {
  font-size: 13px;
  color: #909399;
}

.evaluation-text {
  margin-top: 16px;
  padding: 16px;
  background: #f0f9ff;
  border-radius: 8px;
}

.evaluation-text p {
  margin: 0;
  font-size: 15px;
  color: #606266;
  line-height: 1.6;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 32px;
}
</style>
