import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../pages/Dashboard.vue'
import Login from '../pages/Login.vue'
import Register from '../pages/Register.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import TeacherLayout from '../layouts/TeacherLayout.vue'
import UserManagement from '../pages/admin/UserManagement.vue'
// Teacher pages
import ChapterList from '../pages/teacher/ChapterList.vue'
import ChapterDetail from '../pages/teacher/ChapterDetail.vue'
import LevelMapEditor from '../pages/teacher/LevelMapEditor.vue'
import LevelEditor from '../pages/teacher/LevelEditor.vue'
// Student pages
import StudentHome from '../pages/student/Home.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'login', component: Login },
    { path: '/register', name: 'register', component: Register },
    { path: '/dashboard', name: 'dashboard', component: Dashboard, meta: { requiresAuth: true } },
    // Student routes
    { path: '/student/home', name: 'student-home', component: StudentHome, meta: { requiresAuth: true, role: 'student' } },
    // Teacher routes
    {
      path: '/teacher',
      component: TeacherLayout,
      meta: { requiresAuth: true, role: 'teacher' },
      children: [
        { path: 'dashboard', name: 'teacher-dashboard', component: () => import('../pages/teacher/Dashboard.vue') },
        { path: 'chapters', name: 'teacher-chapters', component: ChapterList },
        { path: 'chapters/:id', name: 'teacher-chapter-detail', component: ChapterDetail },
        { path: 'chapters/:id/map-editor', name: 'teacher-map-editor', component: LevelMapEditor },
        { path: 'levels/:levelId/editor', name: 'teacher-level-editor', component: LevelEditor },
        { path: 'levels/:levelId/visual-editor', name: 'teacher-visual-editor', component: () => import('../pages/teacher/VisualEditorPage.vue') },
      ],
    },
    {
      path: '/preview/interactive',
      name: 'level-interactive-preview',
      component: () => import('../pages/teacher/LevelInteractivePreview.vue'),
    },
    // Admin routes
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, role: 'admin' },
      redirect: '/admin/users',
      children: [
        { path: 'users', name: 'admin-users', component: UserManagement },
      ],
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  
  // If admin tries to access dashboard, redirect to admin backend
  if (to.name === 'dashboard' && authStore.isAdmin) {
    next({ name: 'admin-users' })
    return
  }
  
  // Check role-based access
  if (to.meta.requiresAuth && to.meta.role) {
    const requiredRole = to.meta.role as string
    if (requiredRole === 'admin' && !authStore.isAdmin) {
      next({ name: 'dashboard' })
      return
    }
    if (requiredRole === 'teacher' && !authStore.isTeacher && !authStore.isAdmin) {
      next({ name: 'dashboard' })
      return
    }
    if (requiredRole === 'student' && !authStore.isStudent) {
      next({ name: 'dashboard' })
      return
    }
  }
  
  if ((to.name === 'login' || to.name === 'register') && authStore.isAuthenticated) {
    // Redirect based on user role
    if (authStore.isAdmin) {
      next({ name: 'admin-users' })
    } else if (authStore.isStudent) {
      next({ name: 'student-home' })
    } else if (authStore.isTeacher) {
      next({ name: 'teacher-chapters' })
    } else {
      next({ name: 'dashboard' })
    }
    return
  }
  next()
})

export default router

