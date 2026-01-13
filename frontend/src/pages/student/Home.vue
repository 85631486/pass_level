<template>
  <div class="student-home">
    <div class="page-header">
      <h2>我的学习</h2>
    </div>
    
    <div class="profile-section">
      <div class="profile-card">
        <h3>等级信息</h3>
        <div class="level-info">
          <div class="level-badge">Lv.{{ profile?.level || 1 }}</div>
          <div class="experience-bar">
            <div class="experience-fill" :style="{ width: experiencePercent + '%' }"></div>
          </div>
          <div class="experience-text">
            经验值: {{ profile?.experience || 0 }} / {{ nextLevelExp }}
          </div>
        </div>
        <div class="total-score">
          总得分: <strong>{{ profile?.total_score || 0 }}</strong>
        </div>
      </div>
    </div>
    
    <div class="skill-tree-section">
      <h3>技能树</h3>
      <div class="skill-tree-content">
        <SkillTree v-if="profile" :skills="profile.skills" />
        <p v-else class="loading-text">加载中...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { studentsApi, type StudentProfile } from '../../api/students'
import SkillTree from '../../components/ui/SkillTree.vue'

const authStore = useAuthStore()
const profile = ref<StudentProfile | null>(null)

const nextLevelExp = computed(() => {
  // 根据等级计算下一级所需经验值（每级递增）
  if (!profile.value) return 1000
  return profile.value.level * 1000
})

const experiencePercent = computed(() => {
  if (!profile.value) return 0
  return (profile.value.experience / nextLevelExp.value) * 100
})

onMounted(async () => {
  // 确保用户信息已加载
  if (!authStore.currentUser && authStore.token) {
    try {
      await authStore.fetchProfile()
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return
    }
  }
  
  if (authStore.currentUser) {
    try {
      const response = await studentsApi.getProfile(authStore.currentUser.id)
      profile.value = response.data
    } catch (error) {
      console.error('获取学生档案失败:', error)
    }
  }
})
</script>

<style scoped>
.student-home {
  padding: 2rem;
  width: 100%;
}

.page-header {
  margin-bottom: 2rem;
}

.profile-section {
  margin-bottom: 2rem;
}

.profile-card {
  background: var(--bg-card, white);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  color: var(--text-primary, #333);
}

.profile-card h3 {
  margin-top: 0;
  color: var(--text-primary, #333);
}

.level-info {
  margin: 1rem 0;
}

.level-badge {
  font-size: 2rem;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 0.5rem;
}

.experience-bar {
  width: 100%;
  height: 20px;
  background: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  margin: 0.5rem 0;
}

.experience-fill {
  height: 100%;
  background: linear-gradient(90deg, #007bff, #0056b3);
  transition: width 0.3s ease;
}

.experience-text {
  font-size: 0.9rem;
  color: #666;
}

.total-score {
  margin-top: 1rem;
  font-size: 1.1rem;
}

.skill-tree-section {
  background: var(--bg-card, white);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  color: var(--text-primary, #333);
}

.skill-tree-section h3 {
  margin-top: 0;
  color: var(--text-primary, #333);
}

.skill-tree-content {
  margin-top: 1rem;
  min-height: 200px;
}

.loading-text {
  text-align: center;
  color: #999;
  padding: 2rem;
}
</style>

