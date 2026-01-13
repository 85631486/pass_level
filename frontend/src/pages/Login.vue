<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = reactive({
  identifier: '',
  password: '',
})

const formErrors = ref<{ identifier?: string; password?: string }>({})

const validate = () => {
  const errors: typeof formErrors.value = {}
  if (!form.identifier.trim()) errors.identifier = '请输入邮箱、手机号或学号'
  if (!form.password.trim()) errors.password = '请输入密码'
  formErrors.value = errors
  return Object.keys(errors).length === 0
}

const handleSubmit = async () => {
  if (!validate()) return
  try {
    await authStore.login(form)
    // Wait a bit for user info to be set
    await new Promise(resolve => setTimeout(resolve, 100))
    // Redirect based on user role
    const redirect = (route.query.redirect as string)
    if (redirect) {
      router.replace(redirect)
    } else if (authStore.isAdmin) {
      // Admin goes directly to admin backend
      router.replace('/admin/users')
    } else if (authStore.isStudent) {
      router.replace('/student/home')
    } else if (authStore.isTeacher) {
      router.replace('/teacher/chapters')
    } else {
      router.replace('/dashboard')
    }
  } catch (error) {
    console.error(error)
  }
}
</script>

<template>
  <section>
    <h2>欢迎回来</h2>
    <p>使用账号密码登录，继续闯关进度</p>

    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="identifier">登录账号</label>
        <input
          id="identifier"
          v-model="form.identifier"
          type="text"
          placeholder="邮箱 / 手机号 / 学号"
          class="form-control"
        />
        <p v-if="formErrors.identifier" class="error-text">{{ formErrors.identifier }}</p>
      </div>

      <div class="form-group">
        <label for="password">密码</label>
        <input id="password" v-model="form.password" type="password" class="form-control" />
        <p v-if="formErrors.password" class="error-text">{{ formErrors.password }}</p>
      </div>

      <button class="btn-primary" type="submit" :disabled="authStore.loading">
        {{ authStore.loading ? '正在登录...' : '进入平台' }}
      </button>

      <p v-if="authStore.error" class="error-text" style="text-align: center">{{ authStore.error }}</p>
      <p class="helper-text">
        还没有账号？
        <RouterLink class="link" to="/register">立即注册</RouterLink>
      </p>
    </form>
  </section>
</template>

