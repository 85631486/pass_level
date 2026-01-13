<template>
  <div class="teacher-layout">
    <!-- 侧边栏导航 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <h1 class="logo" v-show="!sidebarCollapsed">过关斩将</h1>
        <p class="logo-subtitle" v-show="!sidebarCollapsed">教学平台</p>
        <button class="sidebar-toggle" @click="toggleSidebar" :title="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'">
          <span v-if="sidebarCollapsed">▶</span>
          <span v-else>◀</span>
        </button>
      </div>
      
      <nav class="sidebar-nav">
        <router-link 
          to="/teacher/chapters" 
          class="nav-item"
          :class="{ active: $route.path.startsWith('/teacher/chapters') && !$route.path.includes('map-editor') }"
          :title="sidebarCollapsed ? '篇章管理' : ''"
        >
          <span class="nav-icon">📚</span>
          <span class="nav-text" v-show="!sidebarCollapsed">篇章管理</span>
        </router-link>
        
        <router-link 
          to="/teacher/dashboard" 
          class="nav-item"
          :class="{ active: $route.path === '/teacher/dashboard' }"
          :title="sidebarCollapsed ? '工作台' : ''"
        >
          <span class="nav-icon">📊</span>
          <span class="nav-text" v-show="!sidebarCollapsed">工作台</span>
        </router-link>
      </nav>
      
      <div class="sidebar-footer" v-show="!sidebarCollapsed">
        <div class="user-info">
          <div class="user-avatar">{{ userInitial }}</div>
          <div class="user-details">
            <div class="user-name">{{ authStore.currentUser?.nickname || '教师' }}</div>
            <div class="user-role">教师</div>
          </div>
        </div>
        <button class="btn-logout" @click="handleLogout">
          <span>退出登录</span>
        </button>
      </div>
      
      <!-- 收起状态下的用户信息 -->
      <div class="sidebar-footer-collapsed" v-show="sidebarCollapsed">
        <div class="user-avatar-small">{{ userInitial }}</div>
      </div>
    </aside>
    
    <!-- 主内容区 -->
    <main class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <div class="content-wrapper">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, RouterView } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const sidebarCollapsed = ref(false)

// 从 localStorage 读取侧边栏状态
onMounted(() => {
  const saved = localStorage.getItem('teacher-sidebar-collapsed')
  if (saved !== null) {
    sidebarCollapsed.value = saved === 'true'
  }
})

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
  // 保存状态到 localStorage
  localStorage.setItem('teacher-sidebar-collapsed', String(sidebarCollapsed.value))
}

const userInitial = computed(() => {
  const name = authStore.currentUser?.nickname || '教'
  return name.charAt(0).toUpperCase()
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.teacher-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
}

/* 侧边栏样式 */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
  z-index: 100;
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 70px;
}

.sidebar-header {
  padding: 2rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  transition: padding 0.3s ease;
}

.sidebar.collapsed .sidebar-header {
  padding: 2rem 0.5rem;
}

.sidebar-toggle {
  position: absolute;
  top: 1rem;
  right: 0.75rem;
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.sidebar-toggle:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.sidebar.collapsed .sidebar-toggle {
  right: 0.5rem;
}

.logo {
  margin: 0;
  font-size: 1.5rem;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-subtitle {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.875rem 1.5rem;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
  margin: 0.25rem 0.75rem;
  border-radius: 8px;
  justify-content: flex-start;
}

.sidebar.collapsed .nav-item {
  padding: 0.875rem;
  justify-content: center;
  margin: 0.25rem 0.5rem;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  transform: translateX(4px);
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: white;
  border-radius: 0 2px 2px 0;
}

.nav-icon {
  font-size: 1.25rem;
  margin-right: 0.75rem;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.sidebar.collapsed .nav-icon {
  margin-right: 0;
}

.nav-text {
  font-size: 0.95rem;
  font-weight: 500;
  white-space: nowrap;
  opacity: 1;
  transition: opacity 0.3s ease;
}

.sidebar.collapsed .nav-text {
  opacity: 0;
  width: 0;
  overflow: hidden;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  transition: opacity 0.3s ease;
}

.sidebar-footer-collapsed {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
}

.user-avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  cursor: pointer;
  transition: transform 0.2s ease;
}

.user-avatar-small:hover {
  transform: scale(1.1);
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
  margin-right: 0.75rem;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.user-role {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
}

.btn-logout {
  width: 100%;
  padding: 0.75rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.btn-logout:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.5);
  color: #f87171;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

/* 主内容区样式 */
.main-content {
  flex: 1;
  margin-left: 260px;
  min-height: 100vh;
  background: #f5f7fa;
  transition: margin-left 0.3s ease;
  width: calc(100% - 260px);
  box-sizing: border-box;
}

.main-content.sidebar-collapsed {
  margin-left: 70px;
  width: calc(100% - 70px);
}

.content-wrapper {
  padding: 0;
  width: 100%;
  margin: 0;
  box-sizing: border-box;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0;
  }
}
</style>

