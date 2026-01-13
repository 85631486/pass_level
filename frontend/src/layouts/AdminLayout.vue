<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const handleLogout = () => {
  authStore.logout()
  router.replace('/login')
}

const menuItems = [
  { path: '/admin/users', label: '账号管理', icon: '👥' },
  // 可以添加更多菜单项
]

const isActive = (path: string) => {
  return route.path === path
}
</script>

<template>
  <div class="admin-layout">
    <!-- Top Navigation Bar -->
    <header class="admin-header">
      <div class="header-left">
        <h1 class="logo">过关斩将</h1>
        <span class="logo-subtitle">管理后台</span>
      </div>
      <div class="header-right">
        <button class="btn-theme-toggle" @click="themeStore.toggleTheme" :title="themeStore.theme === 'dark' ? '切换到明亮模式' : '切换到暗色模式'">
          <span v-if="themeStore.theme === 'dark'">☀️</span>
          <span v-else>🌙</span>
        </button>
        <div class="user-info">
          <span class="user-name">{{ authStore.currentUser?.nickname }}</span>
          <span class="user-role">{{ authStore.currentUser?.role === 'admin' ? '管理员' : '教师' }}</span>
        </div>
        <button class="btn-logout" @click="handleLogout">退出</button>
      </div>
    </header>

    <div class="admin-body">
      <!-- Sidebar -->
      <aside class="admin-sidebar">
        <nav class="sidebar-nav">
          <router-link
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            :class="['nav-item', { active: isActive(item.path) }]"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
          </router-link>
        </nav>
      </aside>

      <!-- Main Content -->
      <main class="admin-main">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Header */
.admin-header {
  height: 64px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-sm);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(120deg, #7087ff, #8e6bff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-subtitle {
  font-size: 0.875rem;
  color: var(--text-tertiary);
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
}

.user-role {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.btn-theme-toggle {
  width: 40px;
  height: 40px;
  padding: 0;
  background: var(--bg-hover);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  margin-right: 1rem;
}

.btn-theme-toggle:hover {
  background: var(--bg-active);
  border-color: var(--accent-color);
  transform: scale(1.05);
}

.btn-logout {
  padding: 0.5rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  color: var(--error-color);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.3);
}

/* Body */
.admin-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Sidebar */
.admin-sidebar {
  width: 240px;
  background: var(--bg-tertiary);
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
  flex-shrink: 0;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.sidebar-nav {
  padding: 1rem 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--bg-active);
  color: var(--accent-color);
  border-left-color: var(--accent-color);
}

.nav-icon {
  font-size: 1.25rem;
}

.nav-label {
  font-size: 0.9375rem;
  font-weight: 500;
}

/* Main Content */
.admin-main {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  background: var(--bg-primary);
  transition: background-color 0.3s ease;
}

@media (max-width: 768px) {
  .admin-header {
    padding: 0 1rem;
  }

  .admin-sidebar {
    width: 200px;
  }

  .admin-main {
    padding: 1.5rem;
  }
}
</style>

