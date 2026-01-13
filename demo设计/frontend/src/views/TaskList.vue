<template>
  <div class="task-list-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h1>过关斩将 - 游戏教学平台</h1>
        </div>
        <div class="header-right">
          <span class="username">{{ userStore.user?.name }}</span>
          <el-button @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>

      <el-main>
        <div class="task-grid">
          <el-card
            v-for="task in tasks"
            :key="task.id"
            class="task-card"
            shadow="hover"
            @click="startTask(task)"
          >
            <div class="task-header">
              <el-icon :size="40" color="#409eff"><Document /></el-icon>
              <span class="task-order">任务 {{ task.task_order }}</span>
            </div>
            <h3 class="task-name">{{ task.task_name }}</h3>
            <div class="task-info">
              <div class="info-item">
                <el-icon><Timer /></el-icon>
                <span>{{ task.time_limit }} 分钟</span>
              </div>
              <div class="info-item">
                <el-icon><Files /></el-icon>
                <span>{{ task.total_operations }} 个操作</span>
              </div>
              <div class="info-item">
                <el-icon><EditPen /></el-icon>
                <span>{{ task.total_questions }} 道题</span>
              </div>
            </div>
            <el-button type="primary" style="width: 100%; margin-top: 15px">
              开始学习
            </el-button>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()

const tasks = ref([])

onMounted(async () => {
  await loadTasks()
})

const loadTasks = async () => {
  try {
    const res = await api.getTasks()
    if (res.success) {
      tasks.value = res.data
    }
  } catch (error) {
    console.error('加载任务列表失败', error)
  }
}

const startTask = async (task) => {
  try {
    const res = await api.startTask({
      student_id: userStore.user.id,
      task_id: task.id
    })
    if (res.success) {
      router.push(`/learning/${task.id}`)
    }
  } catch (error) {
    console.error('开始任务失败', error)
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
  ElMessage.success('已退出登录')
}
</script>

<style scoped>
.task-list-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 0 40px;
}

.header-left h1 {
  font-size: 22px;
  color: #333;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.username {
  font-size: 16px;
  color: #606266;
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.task-card {
  cursor: pointer;
  transition: all 0.3s;
}

.task-card:hover {
  transform: translateY(-4px);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.task-order {
  background: #e6f7ff;
  color: #1890ff;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
}

.task-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 14px;
}
</style>
