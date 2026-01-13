<template>
  <section class="panel">
    <header class="panel-header">
      <h3>关卡考题</h3>
      <button class="btn-primary" @click="startCreate">+ 新建考题</button>
    </header>
    <div class="panel-body">
      <div v-if="loading" class="placeholder">考题加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else>
        <ul class="question-list" v-if="questions.length">
          <li v-for="q in questions" :key="q.id" class="question-item">
            <div class="question-main">
              <div class="question-title">[{{ q.question_type }}] {{ q.title }}</div>
              <div class="question-meta">
                难度：{{ q.difficulty }} ｜ 分值：{{ q.score }}
                <span v-if="q.knowledge_point">｜ 知识点：{{ q.knowledge_point }}</span>
              </div>
            </div>
            <div class="question-actions">
              <button class="link-btn" @click.stop="edit(q)">编辑</button>
              <button class="link-btn danger" @click.stop="remove(q.id)">删除</button>
            </div>
          </li>
        </ul>
        <div v-else class="placeholder">尚未为该关卡配置任何闯关考题。</div>
      </div>
    </div>

    <!-- 题目编辑弹窗 -->
    <div v-if="showDialog" class="modal-overlay" @click.self="close">
      <div class="modal large">
        <header class="modal-header">
          <h3>{{ editingQuestion?.id ? '编辑考题' : '新建考题' }}</h3>
          <button class="btn-close" @click="close">×</button>
        </header>
        <div class="modal-body">
          <div class="form-group">
            <label>题目类型</label>
            <select v-model="form.question_type" class="form-input">
              <option value="single_choice">单选题</option>
              <option value="multiple_choice">多选题</option>
              <option value="true_false">判断题</option>
              <option value="short_answer">简答题</option>
            </select>
          </div>
          <div class="form-group">
            <label>题目标题</label>
            <input v-model="form.title" type="text" class="form-input" />
          </div>
          <div class="form-group">
            <label>题目内容</label>
            <textarea v-model="form.content" rows="3" class="form-textarea"></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>难度</label>
              <select v-model="form.difficulty" class="form-input">
                <option value="easy">简单</option>
                <option value="medium">中等</option>
                <option value="hard">困难</option>
              </select>
            </div>
            <div class="form-group">
              <label>分值</label>
              <input v-model.number="form.score" type="number" min="0" class="form-input" />
            </div>
          </div>
          <div class="form-group">
            <label>知识点</label>
            <input v-model="form.knowledge_point" type="text" class="form-input" />
          </div>
        </div>
        <footer class="modal-footer">
          <button class="btn-secondary" @click="close">取消</button>
          <button class="btn-primary" @click="save">保存</button>
        </footer>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import type { Question } from '../../api/questions'
import { questionsApi } from '../../api/questions'

interface Props {
  levelId: number
}

const props = defineProps<Props>()

const questions = ref<Question[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const showDialog = ref(false)
const editingQuestion = ref<Question | null>(null)
const form = ref({
  question_type: 'single_choice',
  title: '',
  content: '',
  difficulty: 'medium',
  score: 10,
  knowledge_point: '',
})

const loadQuestions = async () => {
  loading.value = true
  error.value = null
  try {
    const resp = await questionsApi.getQuestions(props.levelId)
    questions.value = resp.data
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '加载考题失败'
  } finally {
    loading.value = false
  }
}

const startCreate = () => {
  editingQuestion.value = null
  form.value = {
    question_type: 'single_choice',
    title: '',
    content: '',
    difficulty: 'medium',
    score: 10,
    knowledge_point: '',
  }
  showDialog.value = true
}

const edit = (q: Question) => {
  editingQuestion.value = q
  form.value = {
    question_type: q.question_type,
    title: q.title,
    content: q.content || '',
    difficulty: q.difficulty,
    score: q.score,
    knowledge_point: q.knowledge_point || '',
  }
  showDialog.value = true
}

const close = () => {
  showDialog.value = false
}

const save = async () => {
  if (!form.value.title.trim()) {
    alert('题目标题不能为空')
    return
  }
  try {
    if (editingQuestion.value) {
      await questionsApi.updateQuestion(editingQuestion.value.id, {
        question_type: form.value.question_type,
        title: form.value.title,
        content: form.value.content,
        difficulty: form.value.difficulty,
        score: form.value.score,
        knowledge_point: form.value.knowledge_point,
      })
    } else {
      await questionsApi.createQuestion(props.levelId, {
        question_type: form.value.question_type,
        title: form.value.title,
        content: form.value.content,
        difficulty: form.value.difficulty,
        score: form.value.score,
        knowledge_point: form.value.knowledge_point,
      })
    }
    showDialog.value = false
    await loadQuestions()
  } catch (e: any) {
    alert(e?.response?.data?.detail || '保存考题失败')
  }
}

const remove = async (id: number) => {
  if (!confirm('确定要删除该考题吗？')) return
  try {
    await questionsApi.deleteQuestion(id)
    await loadQuestions()
  } catch (e: any) {
    alert(e?.response?.data?.detail || '删除考题失败')
  }
}

onMounted(loadQuestions)

watch(
  () => props.levelId,
  () => {
    loadQuestions()
  },
)
</script>

<style scoped>
/* keep original styles */
</style>


