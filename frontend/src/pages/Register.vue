<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  email: '',
  phone: '',
  student_id: '',
  nickname: '',
  password: '',
  confirmPassword: '',
})

const formErrors = ref<Record<string, string>>({})

const validate = () => {
  const errors: Record<string, string> = {}
  if (!form.email && !form.phone && !form.student_id) {
    errors.email = '邮箱、手机号或学号至少填写一项'
  }
  if (form.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email)) errors.email = '邮箱格式不正确'
  if (form.student_id && form.student_id.trim().length < 3) errors.student_id = '学号至少3个字符'
  if (!form.nickname.trim()) errors.nickname = '请输入昵称'
  if (form.password.length < 6) errors.password = '密码至少 6 位'
  if (form.password !== form.confirmPassword) errors.confirmPassword = '两次输入的密码不一致'
  formErrors.value = errors
  return Object.keys(errors).length === 0
}

const handleSubmit = async () => {
  if (!validate()) return
  try {
    await authStore.register({
      email: form.email || undefined,
      phone: form.phone || undefined,
      student_id: form.student_id || undefined,
      nickname: form.nickname,
      password: form.password,
    })
    await authStore.login({ 
      identifier: form.email || form.phone || form.student_id || '', 
      password: form.password 
    })
    // Redirect based on user role (students register as students)
    if (authStore.isStudent) {
      router.replace('/student/home')
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
    <h2>创建新账号</h2>
    <p>完成注册，即可开启你的闯关历程</p>

    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="email">邮箱（可选）</label>
        <input id="email" v-model="form.email" type="email" class="form-control" />
        <p v-if="formErrors.email" class="error-text">{{ formErrors.email }}</p>
      </div>

      <div class="form-group">
        <label for="phone">手机号（可选）</label>
        <input id="phone" v-model="form.phone" type="text" class="form-control" />
      </div>

      <div class="form-group">
        <label for="student_id">学号（可选）</label>
        <input id="student_id" v-model="form.student_id" type="text" class="form-control" />
        <p v-if="formErrors.student_id" class="error-text">{{ formErrors.student_id }}</p>
      </div>

      <div class="form-group">
        <label for="nickname">昵称</label>
        <input id="nickname" v-model="form.nickname" type="text" class="form-control" />
        <p v-if="formErrors.nickname" class="error-text">{{ formErrors.nickname }}</p>
      </div>

      <div class="form-group">
        <label for="password">密码</label>
        <input id="password" v-model="form.password" type="password" class="form-control" />
        <p v-if="formErrors.password" class="error-text">{{ formErrors.password }}</p>
      </div>

      <div class="form-group">
        <label for="confirmPassword">确认密码</label>
        <input id="confirmPassword" v-model="form.confirmPassword" type="password" class="form-control" />
        <p v-if="formErrors.confirmPassword" class="error-text">{{ formErrors.confirmPassword }}</p>
      </div>

      <button class="btn-primary" type="submit" :disabled="authStore.loading">
        {{ authStore.loading ? '正在提交...' : '完成注册' }}
      </button>

      <p v-if="authStore.error" class="error-text" style="text-align: center">{{ authStore.error }}</p>
      <p class="helper-text">
        已有账号？
        <RouterLink class="link" to="/login">直接登录</RouterLink>
      </p>
    </form>
  </section>
</template>

