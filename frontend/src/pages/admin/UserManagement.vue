<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { userApi, type User, type CreateUserPayload, type UpdateUserPayload } from '../../api/users'

const users = ref<User[]>([])
const total = ref(0)
const loading = ref(false)
const error = ref<string | null>(null)

// Filters
const roleFilter = ref<string>('')
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// Create user form
const showCreateModal = ref(false)
const accountType = ref<'email' | 'phone' | 'student_id'>('email') // 登录账号类型选项卡
const createForm = ref<CreateUserPayload>({
  email: '',
  phone: '',
  student_id: '',
  nickname: '',
  password: '',
  role: 'student',
  class_name: '',
  notes: '',
})
const createFormErrors = ref<Record<string, string>>({})
const creating = ref(false)

// Edit user form
const showEditModal = ref(false)
const editAccountType = ref<'email' | 'phone' | 'student_id'>('email') // 编辑时登录账号类型选项卡
const editingUserId = ref<number | null>(null)
const editForm = ref<UpdateUserPayload>({
  email: '',
  phone: '',
  student_id: '',
  nickname: '',
  password: '',
  role: 'student',
  is_active: true,
})
const editFormErrors = ref<Record<string, string>>({})
const updating = ref(false)

// 切换账号类型选项卡（创建）
const switchAccountType = (type: 'email' | 'phone' | 'student_id') => {
  accountType.value = type
  // 清空其他输入框
  if (type !== 'email') createForm.value.email = ''
  if (type !== 'phone') createForm.value.phone = ''
  if (type !== 'student_id') createForm.value.student_id = ''
  // 清空相关错误
  delete createFormErrors.value.email
  delete createFormErrors.value.phone
  delete createFormErrors.value.student_id
}

// 切换账号类型选项卡（编辑）
const switchEditAccountType = (type: 'email' | 'phone' | 'student_id') => {
  editAccountType.value = type
  // 清空相关错误
  delete editFormErrors.value.email
  delete editFormErrors.value.phone
  delete editFormErrors.value.student_id
}

// Load users
const loadUsers = async () => {
  loading.value = true
  error.value = null
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const params: any = {
      skip,
      limit: pageSize.value,
    }
    if (roleFilter.value) {
      params.role = roleFilter.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    console.log('Loading users with params:', params)
    const { data } = await userApi.getUsers(params)
    console.log('Users loaded:', data)
    users.value = data.items
    total.value = data.total
  } catch (err: any) {
    console.error('Error loading users:', err)
    error.value = err.response?.data?.detail || err.message || '加载用户列表失败'
  } finally {
    loading.value = false
  }
}

// Create user
const validateCreateForm = () => {
  const errors: Record<string, string> = {}
  
  // 根据选中的选项卡验证对应的字段
  if (accountType.value === 'email') {
    if (!createForm.value.email || !createForm.value.email.trim()) {
      errors.email = '请输入邮箱地址'
    } else if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(createForm.value.email)) {
      errors.email = '邮箱格式不正确'
    }
  } else if (accountType.value === 'phone') {
    if (!createForm.value.phone || !createForm.value.phone.trim()) {
      errors.phone = '请输入手机号'
    }
  } else if (accountType.value === 'student_id') {
    if (!createForm.value.student_id || !createForm.value.student_id.trim()) {
      errors.student_id = '请输入学号'
    } else if (createForm.value.student_id.trim().length < 3) {
      errors.student_id = '学号至少3个字符'
    }
  }
  
  if (!createForm.value.nickname.trim()) {
    errors.nickname = '请输入显示名称'
  }
  if (createForm.value.password.length < 6) {
    errors.password = '密码至少 6 位'
  }
  createFormErrors.value = errors
  return Object.keys(errors).length === 0
}

const handleCreateUser = async () => {
  if (!validateCreateForm()) return

  creating.value = true
  error.value = null
  try {
    const payload: CreateUserPayload = {
      email: createForm.value.email || undefined,
      phone: createForm.value.phone || undefined,
      student_id: createForm.value.student_id || undefined,
      nickname: createForm.value.nickname,
      password: createForm.value.password,
      role: createForm.value.role,
      class_name: createForm.value.class_name?.trim() || undefined,
      notes: createForm.value.notes?.trim() || undefined,
    }
    await userApi.createUser(payload)
    handleCloseModal()
    // Reload users
    await loadUsers()
  } catch (err: any) {
    error.value = err.response?.data?.detail || '创建用户失败'
  } finally {
    creating.value = false
  }
}

// Edit user
const handleEditUser = async (user: User) => {
  editingUserId.value = user.id
  // 根据用户现有的登录账号确定选项卡类型
  if (user.email) {
    editAccountType.value = 'email'
  } else if (user.phone) {
    editAccountType.value = 'phone'
  } else if (user.student_id) {
    editAccountType.value = 'student_id'
  } else {
    editAccountType.value = 'email' // 默认
  }
  
  // 填充表单数据
  editForm.value = {
    email: user.email || '',
    phone: user.phone || '',
    student_id: user.student_id || '',
    nickname: user.nickname,
    password: '', // 密码留空，不修改则不发送
    role: user.role,
    is_active: user.is_active,
    class_name: user.class_name || '',
    notes: user.notes || '',
  }
  editFormErrors.value = {}
  showEditModal.value = true
}

const validateEditForm = () => {
  const errors: Record<string, string> = {}
  
  // 根据选中的选项卡验证对应的字段
  if (editAccountType.value === 'email') {
    if (!editForm.value.email || !editForm.value.email.trim()) {
      errors.email = '请输入邮箱地址'
    } else if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(editForm.value.email)) {
      errors.email = '邮箱格式不正确'
    }
  } else if (editAccountType.value === 'phone') {
    if (!editForm.value.phone || !editForm.value.phone.trim()) {
      errors.phone = '请输入手机号'
    }
  } else if (editAccountType.value === 'student_id') {
    if (!editForm.value.student_id || !editForm.value.student_id.trim()) {
      errors.student_id = '请输入学号'
    } else if (editForm.value.student_id.trim().length < 3) {
      errors.student_id = '学号至少3个字符'
    }
  }
  
  if (!editForm.value.nickname || !editForm.value.nickname.trim()) {
    errors.nickname = '请输入显示名称'
  }
  
  // 如果填写了密码，则验证密码
  if (editForm.value.password && editForm.value.password.trim()) {
    if (editForm.value.password.trim().length < 6) {
      errors.password = '密码至少6个字符'
    }
  }
  
  editFormErrors.value = errors
  return Object.keys(errors).length === 0
}

const handleUpdateUser = async () => {
  if (!validateEditForm() || !editingUserId.value) return

  updating.value = true
  error.value = null
  try {
    // 根据选中的选项卡，只保留对应的登录账号字段
    const payload: UpdateUserPayload = {
      nickname: editForm.value.nickname,
      role: editForm.value.role,
      is_active: editForm.value.is_active,
    }
    
    // 根据选项卡类型设置对应的登录账号字段
    if (editAccountType.value === 'email') {
      payload.email = editForm.value.email || undefined
      payload.phone = undefined
      payload.student_id = undefined
    } else if (editAccountType.value === 'phone') {
      payload.phone = editForm.value.phone || undefined
      payload.email = undefined
      payload.student_id = undefined
    } else if (editAccountType.value === 'student_id') {
      payload.student_id = editForm.value.student_id || undefined
      payload.email = undefined
      payload.phone = undefined
    }
    
    // 如果填写了密码，则添加到 payload 中
    if (editForm.value.password && editForm.value.password.trim()) {
      payload.password = editForm.value.password.trim()
    }
    
    // 添加班级和备注字段
    payload.class_name = editForm.value.class_name?.trim() || undefined
    payload.notes = editForm.value.notes?.trim() || undefined
    
    await userApi.updateUser(editingUserId.value, payload)
    handleCloseEditModal()
    await loadUsers()
  } catch (err: any) {
    error.value = err.response?.data?.detail || '更新用户失败'
  } finally {
    updating.value = false
  }
}

// Delete user
const handleDeleteUser = async (userId: number) => {
  if (!confirm('确定要删除该用户吗？')) return

  try {
    await userApi.deleteUser(userId)
    await loadUsers()
  } catch (err: any) {
    error.value = err.response?.data?.detail || '删除用户失败'
  }
}

// Role label
const getRoleLabel = (role: string) => {
  const labels: Record<string, string> = {
    student: '学生',
    teacher: '教师',
    admin: '管理员',
  }
  return labels[role] || role
}

// Format date
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

// Pagination
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// Debounce helper
let debounceTimer: ReturnType<typeof setTimeout> | null = null
const debouncedLoadUsers = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    currentPage.value = 1 // Reset to first page when searching
    loadUsers()
  }, 500)
}

// Close modal and reset form
const handleCloseModal = () => {
  showCreateModal.value = false
  accountType.value = 'email'
  createForm.value = {
    email: '',
    phone: '',
    student_id: '',
    nickname: '',
    password: '',
    role: 'student',
  }
  createFormErrors.value = {}
}

// Close edit modal and reset form
const handleCloseEditModal = () => {
  showEditModal.value = false
  editingUserId.value = null
  editAccountType.value = 'email'
  editForm.value = {
    email: '',
    phone: '',
    student_id: '',
    nickname: '',
    password: '',
    role: 'student',
    is_active: true,
    class_name: '',
    notes: '',
  }
  editFormErrors.value = {}
}

onMounted(() => {
  console.log('UserManagement component mounted')
  loadUsers()
})
</script>

<template>
  <div class="user-management">
    <div class="page-header">
      <div>
        <h1 class="page-title">账号管理</h1>
        <p class="page-description">管理系统中的所有用户账号，包括学生、教师和管理员</p>
      </div>
      <button class="btn-primary btn-add" @click="showCreateModal = true">
        <span>➕</span>
        添加账号
      </button>
    </div>

    <!-- Filters -->
    <div class="filters-card">
      <div class="filter-group">
        <label class="filter-label">角色筛选</label>
        <select v-model="roleFilter" @change="currentPage = 1; loadUsers()" class="filter-select">
          <option value="">全部角色</option>
          <option value="student">学生</option>
          <option value="teacher">教师</option>
          <option value="admin">管理员</option>
        </select>
      </div>
      <div class="filter-group">
        <label class="filter-label">搜索</label>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="输入邮箱、手机号、学号或昵称..."
              @input="debouncedLoadUsers"
              class="filter-input"
            />
      </div>
      <div class="filter-stats">
        <span class="stats-text">共 {{ total }} 个账号</span>
      </div>
    </div>

    <!-- Error message -->
    <div v-if="error" class="alert alert-error">
      <span>⚠️</span>
      <span>{{ error }}</span>
    </div>

    <!-- User list -->
    <div class="table-card">
      <div class="table-wrapper">
        <table class="user-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>昵称</th>
            <th>邮箱</th>
            <th>手机号</th>
            <th>学号</th>
            <th>角色</th>
            <th>状态</th>
            <th>班级</th>
            <th>备注</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="11" class="table-empty">
              <div class="empty-state">
                <span class="empty-icon">⏳</span>
                <span>加载中...</span>
              </div>
            </td>
          </tr>
          <tr v-else-if="!loading && users.length === 0">
            <td colspan="11" class="table-empty">
              <div class="empty-state">
                <span class="empty-icon">📭</span>
                <span>暂无数据</span>
              </div>
            </td>
          </tr>
          <tr v-else v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.nickname }}</td>
            <td>{{ user.email || '-' }}</td>
            <td>{{ user.phone || '-' }}</td>
            <td>{{ user.student_id || '-' }}</td>
            <td>
              <span :class="`role-badge role-${user.role}`">{{ getRoleLabel(user.role) }}</span>
            </td>
            <td>
              <span :class="user.is_active ? 'status-active' : 'status-inactive'">
                {{ user.is_active ? '启用' : '禁用' }}
              </span>
            </td>
            <td>{{ user.class_name || '-' }}</td>
            <td class="notes-cell">{{ user.notes || '-' }}</td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>
              <div class="action-buttons">
                <button class="btn-primary btn-sm" @click="handleEditUser(user)">编辑</button>
                <button class="btn-danger btn-sm" @click="handleDeleteUser(user.id)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-wrapper" v-if="totalPages > 1">
      <div class="pagination">
        <button 
          class="pagination-btn" 
          :disabled="currentPage === 1" 
          @click="currentPage--; loadUsers()"
        >
          ← 上一页
        </button>
        <div class="pagination-info">
          <span>第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
          <span class="pagination-total">（共 {{ total }} 条记录）</span>
        </div>
        <button 
          class="pagination-btn" 
          :disabled="currentPage === totalPages" 
          @click="currentPage++; loadUsers()"
        >
          下一页 →
        </button>
      </div>
    </div>

    <!-- Create user modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="handleCloseModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>添加账号</h3>
          <button class="modal-close" @click="handleCloseModal">×</button>
        </div>
        <form @submit.prevent="handleCreateUser">
          <div class="form-group">
            <label>登录账号 <span class="required">*</span></label>
            <p class="field-hint">选择一种登录方式并填写</p>
            
            <!-- 选项卡 -->
            <div class="account-type-tabs">
              <button
                type="button"
                :class="['tab-button', { active: accountType === 'email' }]"
                @click="switchAccountType('email')"
              >
                邮箱
              </button>
              <button
                type="button"
                :class="['tab-button', { active: accountType === 'phone' }]"
                @click="switchAccountType('phone')"
              >
                手机号
              </button>
              <button
                type="button"
                :class="['tab-button', { active: accountType === 'student_id' }]"
                @click="switchAccountType('student_id')"
              >
                学号
              </button>
            </div>

            <!-- 邮箱输入 -->
            <div v-if="accountType === 'email'" class="tab-content">
              <input 
                v-model="createForm.email" 
                type="email" 
                class="form-control" 
                placeholder="请输入邮箱地址"
              />
              <p v-if="createFormErrors.email" class="error-text">{{ createFormErrors.email }}</p>
            </div>

            <!-- 手机号输入 -->
            <div v-if="accountType === 'phone'" class="tab-content">
              <input 
                v-model="createForm.phone" 
                type="text" 
                class="form-control" 
                placeholder="请输入手机号"
              />
              <p v-if="createFormErrors.phone" class="error-text">{{ createFormErrors.phone }}</p>
            </div>

            <!-- 学号输入 -->
            <div v-if="accountType === 'student_id'" class="tab-content">
              <input 
                v-model="createForm.student_id" 
                type="text" 
                class="form-control" 
                placeholder="请输入学号"
              />
              <p v-if="createFormErrors.student_id" class="error-text">{{ createFormErrors.student_id }}</p>
            </div>
          </div>

          <div class="form-group">
            <label>显示名称 <span class="required">*</span></label>
            <p class="field-hint">用户在系统中显示的名称</p>
            <input 
              v-model="createForm.nickname" 
              type="text" 
              class="form-control" 
              placeholder="请输入显示名称"
              required 
            />
            <p v-if="createFormErrors.nickname" class="error-text">{{ createFormErrors.nickname }}</p>
          </div>

          <div class="form-group">
            <label>密码 <span class="required">*</span></label>
            <input 
              v-model="createForm.password" 
              type="password" 
              class="form-control" 
              placeholder="至少6位字符"
              required 
            />
            <p v-if="createFormErrors.password" class="error-text">{{ createFormErrors.password }}</p>
          </div>

          <div class="form-group">
            <label>角色 <span class="required">*</span></label>
            <select v-model="createForm.role" class="form-control" required>
              <option value="student">学生</option>
              <option value="teacher">教师</option>
              <option value="admin">管理员</option>
            </select>
          </div>

          <div class="form-group">
            <label>班级</label>
            <p class="field-hint">用户所属班级（可选）</p>
            <input 
              v-model="createForm.class_name" 
              type="text" 
              class="form-control" 
              placeholder="请输入班级名称"
            />
          </div>

          <div class="form-group">
            <label>备注</label>
            <p class="field-hint">用户备注信息（可选）</p>
            <textarea 
              v-model="createForm.notes" 
              class="form-control" 
              placeholder="请输入备注信息"
              rows="3"
            ></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="handleCloseModal">取消</button>
            <button type="submit" class="btn-primary" :disabled="creating">
              {{ creating ? '创建中...' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit user modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="handleCloseEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>编辑账号</h3>
          <button class="modal-close" @click="handleCloseEditModal">×</button>
        </div>
        <form @submit.prevent="handleUpdateUser">
          <div class="form-group">
            <label>登录账号 <span class="required">*</span></label>
            <p class="field-hint">选择一种登录方式并填写</p>
            
            <!-- 选项卡 -->
            <div class="account-type-tabs">
              <button
                type="button"
                :class="['tab-button', { active: editAccountType === 'email' }]"
                @click="switchEditAccountType('email')"
              >
                邮箱
              </button>
              <button
                type="button"
                :class="['tab-button', { active: editAccountType === 'phone' }]"
                @click="switchEditAccountType('phone')"
              >
                手机号
              </button>
              <button
                type="button"
                :class="['tab-button', { active: editAccountType === 'student_id' }]"
                @click="switchEditAccountType('student_id')"
              >
                学号
              </button>
            </div>

            <!-- 邮箱输入 -->
            <div v-if="editAccountType === 'email'" class="tab-content">
              <input 
                v-model="editForm.email" 
                type="email" 
                class="form-control" 
                placeholder="请输入邮箱地址"
              />
              <p v-if="editFormErrors.email" class="error-text">{{ editFormErrors.email }}</p>
            </div>

            <!-- 手机号输入 -->
            <div v-if="editAccountType === 'phone'" class="tab-content">
              <input 
                v-model="editForm.phone" 
                type="text" 
                class="form-control" 
                placeholder="请输入手机号"
              />
              <p v-if="editFormErrors.phone" class="error-text">{{ editFormErrors.phone }}</p>
            </div>

            <!-- 学号输入 -->
            <div v-if="editAccountType === 'student_id'" class="tab-content">
              <input 
                v-model="editForm.student_id" 
                type="text" 
                class="form-control" 
                placeholder="请输入学号"
              />
              <p v-if="editFormErrors.student_id" class="error-text">{{ editFormErrors.student_id }}</p>
            </div>
          </div>

          <div class="form-group">
            <label>显示名称 <span class="required">*</span></label>
            <p class="field-hint">用户在系统中显示的名称</p>
            <input 
              v-model="editForm.nickname" 
              type="text" 
              class="form-control" 
              placeholder="请输入显示名称"
              required 
            />
            <p v-if="editFormErrors.nickname" class="error-text">{{ editFormErrors.nickname }}</p>
          </div>

          <div class="form-group">
            <label>密码</label>
            <p class="field-hint">留空则不修改密码，填写新密码将更新用户密码</p>
            <input 
              v-model="editForm.password" 
              type="password" 
              class="form-control" 
              placeholder="留空则不修改，至少6位字符"
            />
            <p v-if="editFormErrors.password" class="error-text">{{ editFormErrors.password }}</p>
          </div>

          <div class="form-group">
            <label>角色 <span class="required">*</span></label>
            <select v-model="editForm.role" class="form-control" required>
              <option value="student">学生</option>
              <option value="teacher">教师</option>
              <option value="admin">管理员</option>
            </select>
          </div>

          <div class="form-group">
            <label>状态 <span class="required">*</span></label>
            <select v-model="editForm.is_active" class="form-control" required>
              <option :value="true">启用</option>
              <option :value="false">禁用</option>
            </select>
          </div>

          <div class="form-group">
            <label>班级</label>
            <p class="field-hint">用户所属班级（可选）</p>
            <input 
              v-model="editForm.class_name" 
              type="text" 
              class="form-control" 
              placeholder="请输入班级名称"
            />
          </div>

          <div class="form-group">
            <label>备注</label>
            <p class="field-hint">用户备注信息（可选）</p>
            <textarea 
              v-model="editForm.notes" 
              class="form-control" 
              placeholder="请输入备注信息"
              rows="3"
            ></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="handleCloseEditModal">取消</button>
            <button type="submit" class="btn-primary" :disabled="updating">
              {{ updating ? '更新中...' : '更新' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-management {
  max-width: 100%;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  gap: 2rem;
}

.page-title {
  font-size: 1.875rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: #e4e4e7;
}

.page-description {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9375rem;
  margin: 0;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  white-space: nowrap;
  width: auto;
}

.btn-add span {
  font-size: 1.125rem;
}

/* Filters */
.filters-card {
  display: flex;
  gap: 1.5rem;
  align-items: flex-end;
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 0.75rem;
  flex-wrap: wrap;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 200px;
}

.filter-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.filter-select,
.filter-input {
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--border-color-light);
  border-radius: 0.5rem;
  background: var(--bg-input);
  color: var(--text-primary);
  font-size: 0.9375rem;
  transition: all 0.2s;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
}

.filter-select {
  background-color: var(--bg-input);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23e4e4e7' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 12px;
  padding-right: 2.5rem;
}

[data-theme='light'] .filter-select {
  background-color: var(--bg-input);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%231a1d29' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: var(--accent-color);
  background-color: var(--bg-input);
  box-shadow: 0 0 0 3px var(--accent-light);
}

.filter-select:focus {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%237087ff' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
}

.filter-select:focus {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%237087ff' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
}

/* Select dropdown options */
.filter-select option {
  background: var(--bg-input) !important;
  color: var(--text-primary) !important;
  padding: 0.5rem;
}

.filter-select option:hover {
  background: var(--bg-hover) !important;
}

.filter-select option:checked {
  background: var(--accent-color) !important;
  color: #fff !important;
}

.filter-stats {
  margin-left: auto;
  display: flex;
  align-items: center;
}

.stats-text {
  color: var(--text-tertiary);
  font-size: 0.875rem;
}

/* Alert */
.alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

.alert-error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: var(--error-color);
}

/* Table Card */
.table-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 0.75rem;
  overflow: hidden;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.table-wrapper {
  overflow-x: auto;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.user-table thead {
  background: var(--bg-hover);
}

.user-table th {
  padding: 1rem 1.25rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border-color);
}

.user-table th:last-child {
  text-align: center;
}

.user-table td {
  padding: 1rem 1.25rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  font-size: 0.9375rem;
}

.user-table td:last-child {
  text-align: center;
}

.notes-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  position: relative;
}

.notes-cell:hover {
  white-space: normal;
  word-break: break-word;
  z-index: 10;
  background: var(--bg-card);
  box-shadow: var(--shadow-md);
}

.user-table tbody tr {
  transition: background 0.2s;
}

.user-table tbody tr:hover {
  background: var(--bg-hover);
}

.user-table tbody tr:last-child td {
  border-bottom: none;
}

.role-badge {
  display: inline-block;
  padding: 0.375rem 0.875rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0.025em;
}

.role-student {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.role-teacher {
  background: rgba(168, 85, 247, 0.15);
  color: #a78bfa;
  border: 1px solid rgba(168, 85, 247, 0.2);
}

.role-admin {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.status-active {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  color: var(--success-color);
  font-weight: 500;
}

.status-active::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success-color);
}

.status-inactive {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  color: var(--error-color);
  font-weight: 500;
}

.status-inactive::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--error-color);
}

.action-buttons {
  display: flex;
  gap: 0.625rem;
  align-items: center;
  justify-content: center;
  flex-direction: row;
  flex-wrap: nowrap;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  width: 64px;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.btn-primary.btn-sm {
  background: linear-gradient(135deg, #7087ff 0%, #5b6ee8 100%);
  color: #ffffff;
  box-shadow: 0 2px 4px rgba(112, 135, 255, 0.2);
}

.btn-primary.btn-sm:hover {
  background: linear-gradient(135deg, #5b6ee8 0%, #4a5bd4 100%);
  box-shadow: 0 4px 8px rgba(112, 135, 255, 0.3);
  transform: translateY(-1px);
}

.btn-primary.btn-sm:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(112, 135, 255, 0.2);
}

.btn-danger.btn-sm {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.btn-danger.btn-sm:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
  color: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
}

.btn-danger.btn-sm:active {
  transform: translateY(0);
  box-shadow: none;
}

.pagination-wrapper {
  margin-top: 2rem;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
  padding: 1.25rem 1.5rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 0.75rem;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.pagination-btn {
  padding: 0.625rem 1.25rem;
  border: 1px solid var(--border-color-light);
  border-radius: 0.5rem;
  background: var(--bg-hover);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 0.9375rem;
  font-weight: 500;
  transition: all 0.2s;
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--bg-active);
  border-color: var(--accent-color);
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9375rem;
}

.pagination-total {
  color: var(--text-tertiary);
  font-size: 0.875rem;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-card);
  border-radius: 1rem;
  padding: 0;
  width: 90%;
  max-width: 560px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-lg);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  font-size: 1.5rem;
  cursor: pointer;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.modal-content form {
  padding: 2rem;
  overflow-y: auto;
  flex: 1;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.modal-actions .btn-primary {
  width: auto;
  min-width: 100px;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color-light);
  cursor: pointer;
  font-size: 0.9375rem;
  font-weight: 500;
  transition: all 0.2s;
  min-width: 80px;
}

.btn-secondary:hover {
  background: var(--bg-hover);
  border-color: var(--border-color-hover);
  transform: translateY(-1px);
}

.required {
  color: var(--error-color);
}

/* Empty state */
.table-empty {
  padding: 3rem 1rem !important;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--text-tertiary);
  font-size: 0.9375rem;
}

.empty-icon {
  font-size: 2rem;
  opacity: 0.6;
}

/* Form field hints */
.field-hint {
  font-size: 0.8125rem;
  color: var(--text-tertiary);
  margin: 0.25rem 0 0.5rem 0;
  line-height: 1.4;
}

.label-empty {
  visibility: hidden;
  height: 0;
  margin: 0;
  padding: 0;
}

/* Account type tabs */
.account-type-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.tab-button {
  padding: 0.625rem 1.25rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary);
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  bottom: -1px;
}

.tab-button:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.tab-button.active {
  color: var(--accent-color);
  border-bottom-color: var(--accent-color);
  background: transparent;
}

.tab-content {
  margin-top: 0.5rem;
}
</style>

