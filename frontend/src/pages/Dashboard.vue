<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { RouterLink } from 'vue-router'
import router from '../router'

const authStore = useAuthStore()

onMounted(() => {
  if (!authStore.currentUser && authStore.token) {
    authStore.fetchProfile().catch(() => router.replace('/login'))
  }
})

const handleLogout = () => {
  authStore.logout()
  router.replace('/login')
}
</script>

<template>
  <section>
    <h2>课程看板</h2>
    
    <div v-if="authStore.isStudent" class="dashboard-card">
      <h3>学生端</h3>
      <p>当前账号：<strong>{{ authStore.currentUser?.nickname }}</strong></p>
      <p>角色：学生</p>
      <p>注册时间：{{ authStore.currentUser?.created_at?.slice(0, 10) }}</p>
      <div style="margin-top: 1.5rem; display: flex; gap: 1rem; flex-wrap: wrap;">
        <RouterLink to="/student/home" class="btn-primary">进入学习</RouterLink>
        <button class="btn-secondary" @click="handleLogout">退出登录</button>
      </div>
    </div>

    <div v-else-if="authStore.isTeacher" class="dashboard-card">
      <h3>教师端</h3>
      <p>当前账号：<strong>{{ authStore.currentUser?.nickname }}</strong></p>
      <p>角色：教师</p>
      <p>注册时间：{{ authStore.currentUser?.created_at?.slice(0, 10) }}</p>
      <div style="margin-top: 1.5rem; display: flex; gap: 1rem; flex-wrap: wrap;">
        <RouterLink to="/teacher/chapters" class="btn-primary">篇章管理</RouterLink>
        <button class="btn-secondary" @click="handleLogout">退出登录</button>
      </div>
    </div>

    <div v-else-if="authStore.isAdmin" class="dashboard-card">
      <h3>管理员端</h3>
      <p>当前账号：<strong>{{ authStore.currentUser?.nickname }}</strong></p>
      <p>角色：管理员</p>
      <p>注册时间：{{ authStore.currentUser?.created_at?.slice(0, 10) }}</p>
      <div style="margin-top: 1.5rem; display: flex; gap: 1rem; flex-wrap: wrap;">
        <RouterLink to="/admin/users" class="btn-primary">进入管理后台</RouterLink>
        <button class="btn-secondary" @click="handleLogout">退出登录</button>
      </div>
    </div>

    <div v-else class="dashboard-card">
      <p>当前账号：<strong>{{ authStore.currentUser?.nickname }}</strong></p>
      <p>注册时间：{{ authStore.currentUser?.created_at?.slice(0, 10) }}</p>
      <button class="btn-primary" style="margin-top: 1.5rem" @click="handleLogout">退出登录</button>
    </div>
  </section>
</template>

<style scoped>
.dashboard-card {
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 1.5rem;
  margin-top: 2rem;
  background: rgba(255, 255, 255, 0.04);
}

.btn-secondary {
  padding: 0.9rem 1rem;
  border: none;
  border-radius: 0.9rem;
  font-weight: 600;
  background: #6c757d;
  color: #fff;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(108, 117, 125, 0.3);
}

.btn-primary {
  text-decoration: none;
  display: inline-block;
  text-align: center;
}
</style>

