<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, RouterView } from 'vue-router'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const authStore = useAuthStore()
const isAdminRoute = computed(() => route.path.startsWith('/admin'))
const isStandaloneRoute = computed(() => route.path.startsWith('/preview'))
const isAuthenticatedRoute = computed(() => {
  return authStore.isAuthenticated && (
    route.path.startsWith('/teacher') || 
    route.path.startsWith('/student') ||
    route.path.startsWith('/dashboard')
  )
})
</script>

<template>
  <RouterView v-if="isAdminRoute" />
  <RouterView v-else-if="isStandaloneRoute" />
  <main v-else class="app-shell">
    <section v-if="!isAuthenticatedRoute" class="app-brand">
      <h1>过关斩将教学平台</h1>
      <p>登入平台，开始你的闯关旅程</p>
    </section>
    <section :class="['app-content', { 'app-content-full': isAuthenticatedRoute }]">
      <RouterView />
    </section>
  </main>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
  padding: 4rem 6vw;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.app-shell:has(.app-content-full) {
  padding: 0;
  gap: 0;
  grid-template-columns: 1fr;
}

[data-theme='dark'] .app-shell {
  background: radial-gradient(circle at top, #1d1f3a, #0b0c1f);
}

[data-theme='light'] .app-shell {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.app-brand {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1rem;
}

.app-brand h1 {
  font-size: clamp(2rem, 4vw, 3rem);
  margin: 0;
}

.app-brand p {
  color: var(--text-secondary);
  margin: 0;
}

.app-content {
  background: var(--bg-card);
  border-radius: 1.25rem;
  padding: 2.5rem;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-color);
  min-height: 420px;
  transition: background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

.app-content-full {
  grid-column: 1 / -1;
  border-radius: 0;
  box-shadow: none;
  border: none;
  background: transparent;
  padding: 0;
  min-height: 100vh;
  width: 100%;
  box-sizing: border-box;
}

[data-theme='dark'] .app-content {
  backdrop-filter: blur(10px);
}

@media (max-width: 768px) {
  .app-shell {
    padding: 2rem;
  }

  .app-content {
    padding: 2rem 1.5rem;
  }
}
</style>
