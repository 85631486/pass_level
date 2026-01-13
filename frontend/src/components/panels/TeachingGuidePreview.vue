<template>
  <div class="guide-preview" v-if="parsedGuide">
    <header class="preview-header">
      <div>
        <h3>{{ parsedGuide.title }}</h3>
        <p class="subtitle">
          自动生成的交互式学习页面预览 · 共 {{ parsedGuide.steps.length }} 个学习步骤
        </p>
      </div>
      <div class="summary-cards">
        <div class="summary-card">
          <span class="label">学习步骤</span>
          <strong>{{ parsedGuide.steps.length }}</strong>
        </div>
        <div class="summary-card">
          <span class="label">练习任务</span>
          <strong>{{ totalPractice }}</strong>
        </div>
        <div class="summary-card">
          <span class="label">课堂问答</span>
          <strong>{{ totalQuestions }}</strong>
        </div>
      </div>
    </header>

    <section v-if="parsedGuide.goals.length" class="section">
      <div class="section-header">
        <h4>📌 学习目标</h4>
        <p>教案中的目标将转换为系统可追踪的任务清单</p>
      </div>
      <div class="goal-grid">
        <div
          v-for="group in parsedGuide.goals"
          :key="group.title"
          class="goal-card"
        >
          <div class="goal-title">{{ group.title }}</div>
          <ul>
            <li v-for="(item, idx) in group.items" :key="idx">
              {{ item }}
            </li>
          </ul>
        </div>
      </div>
    </section>

    <section v-if="parsedGuide.duration || parsedGuide.timeAllocations.length" class="section">
      <div class="section-header">
        <h4>⏰ 任务时间</h4>
        <p>用于控制关卡计时与步骤时长提示</p>
      </div>
      <div class="timeline-card">
        <div v-if="parsedGuide.duration" class="timeline-total">
          总时长：{{ parsedGuide.duration }}
        </div>
        <ul>
          <li v-for="(item, idx) in parsedGuide.timeAllocations" :key="idx">
            {{ item }}
          </li>
        </ul>
      </div>
    </section>

    <section v-if="parsedGuide.preparations.length" class="section">
      <div class="section-header">
        <h4>🛠️ 准备工作</h4>
        <p>这些内容将用于生成「必备工具」检查清单</p>
      </div>
      <ul class="checklist">
        <li v-for="(item, idx) in parsedGuide.preparations" :key="idx">
          <span class="checkbox">□</span>
          <span>{{ item }}</span>
        </li>
      </ul>
    </section>

    <section v-if="parsedGuide.steps.length" class="section">
      <div class="section-header">
        <h4>📋 操作步骤</h4>
        <p>每个步骤将被拆分为学习卡片，支持进度跟踪与作答记录</p>
      </div>
      <div class="steps-list">
        <article
          v-for="(step, index) in parsedGuide.steps"
          :key="step.title"
          class="step-card"
        >
          <header class="step-card-header">
            <div class="badge">步骤 {{ index + 1 }}</div>
            <div>
              <h5>{{ step.title }}</h5>
              <p v-if="step.duration" class="duration">建议耗时：{{ step.duration }}</p>
            </div>
          </header>
          <div class="step-content">
            <div
              v-for="(paragraph, idx) in step.summary"
              :key="idx"
              class="step-paragraph"
            >
              {{ paragraph }}
            </div>

            <div v-if="step.practice?.length" class="step-block practice-block">
              <div class="block-title">📝 立即动手练习</div>
              <ul>
                <li v-for="(task, idx) in step.practice" :key="idx">
                  {{ task }}
                </li>
              </ul>
            </div>

            <div v-if="step.quiz?.length" class="step-block quiz-block">
              <div class="block-title">🧠 课堂问答</div>
              <div
                v-for="(question, qIdx) in step.quiz"
                :key="qIdx"
                class="quiz-item"
              >
                <div class="quiz-question">{{ question.question }}</div>
                <ul class="quiz-options">
                  <li v-for="(option, oIdx) in question.options" :key="oIdx">
                    <span class="option-label">{{ String.fromCharCode(65 + oIdx) }}.</span>
                    <span>{{ option }}</span>
                  </li>
                </ul>
                <div v-if="question.answer" class="quiz-answer">
                  ✅ 正确答案：{{ question.answer }}
                </div>
                <div v-if="question.explanation" class="quiz-explanation">
                  解析：{{ question.explanation }}
                </div>
              </div>
            </div>
          </div>
        </article>
      </div>
    </section>

    <section v-if="parsedGuide.homework.length" class="section">
      <div class="section-header">
        <h4>📝 作业要求</h4>
        <p>将用于自动生成关卡结课作业提示</p>
      </div>
      <ul class="bullet-list">
        <li v-for="(item, idx) in parsedGuide.homework" :key="idx">{{ item }}</li>
      </ul>
    </section>

    <section v-if="parsedGuide.faq.length" class="section">
      <div class="section-header">
        <h4>❓ 常见问题</h4>
        <p>这些内容会作为关卡内的 AI 答疑知识库</p>
      </div>
      <div class="faq-list">
        <div v-for="(item, idx) in parsedGuide.faq" :key="idx" class="faq-item">
          <div class="faq-question">{{ item.question }}</div>
          <div class="faq-answer">{{ item.answer }}</div>
        </div>
      </div>
    </section>

    <section v-if="parsedGuide.tips.length" class="section">
      <div class="section-header">
        <h4>💡 学习提示</h4>
      </div>
      <ul class="bullet-list">
        <li v-for="(tip, idx) in parsedGuide.tips" :key="idx">{{ tip }}</li>
      </ul>
    </section>

    <section v-if="parsedGuide.checklist.length" class="section">
      <div class="section-header">
        <h4>🎯 自我检查</h4>
      </div>
      <ul class="checklist">
        <li v-for="(item, idx) in parsedGuide.checklist" :key="idx">
          <span class="checkbox">□</span>
          <span>{{ item }}</span>
        </li>
      </ul>
    </section>
  </div>
  <div v-else class="preview-empty">
    暂无可解析的教案内容，请先在左侧编写 Markdown 教案。
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  parseTeachingGuide,
  type TeachingGuideParsed,
} from '../utils/teachingGuideParser'

const props = defineProps<{
  guideMd: string
}>()

const parsedGuide = computed<TeachingGuideParsed | null>(() =>
  parseTeachingGuide(props.guideMd)
)

const totalPractice = computed(() => {
  if (!parsedGuide.value) return 0
  return parsedGuide.value.steps.reduce(
    (sum, step) => sum + (step.practice?.length || 0),
    0
  )
})

const totalQuestions = computed(() => {
  if (!parsedGuide.value) return 0
  return parsedGuide.value.steps.reduce(
    (sum, step) => sum + (step.quiz?.length || 0),
    0
  )
})
</script>

<style scoped>
.guide-preview {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #eef2ff, #eff6ff);
  border-radius: 12px;
  border: 1px solid #e0e7ff;
}

.preview-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: #312e81;
}

.subtitle {
  margin: 0.25rem 0 0;
  color: #4c1d95;
  font-size: 0.95rem;
}

.summary-cards {
  display: flex;
  gap: 1rem;
}

.summary-card {
  padding: 0.75rem 1rem;
  background: #ffffff;
  border-radius: 8px;
  min-width: 110px;
  text-align: center;
  border: 1px solid #e0e7ff;
}

.summary-card .label {
  font-size: 0.75rem;
  color: #6b7280;
}

.summary-card strong {
  display: block;
  font-size: 1.5rem;
  color: #312e81;
}

.section {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
}

.section-header h4 {
  margin: 0;
  font-size: 1.1rem;
  color: #111827;
}

.section-header p {
  margin: 0.25rem 0 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.goal-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.goal-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 1rem;
  background: #f9fafb;
}

.goal-title {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

.goal-card ul {
  margin: 0;
  padding-left: 1.2rem;
  color: #4b5563;
  font-size: 0.92rem;
}

.timeline-card {
  margin-top: 1rem;
  border: 1px dashed #c7d2fe;
  border-radius: 10px;
  padding: 1rem;
  background: #f5f3ff;
}

.timeline-total {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #4c1d95;
}

.timeline-card ul {
  margin: 0;
  padding-left: 1.2rem;
}

.checklist {
  list-style: none;
  padding: 0;
  margin: 1rem 0 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.checklist li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
}

.checkbox {
  font-weight: 600;
  color: #6b7280;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.step-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.step-card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.badge {
  background: #e0e7ff;
  color: #3730a3;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
}

.step-card-header h5 {
  margin: 0;
  font-size: 1.05rem;
  color: #111827;
}

.duration {
  margin: 0.25rem 0 0;
  color: #6b7280;
  font-size: 0.85rem;
}

.step-content {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.step-paragraph {
  color: #4b5563;
  line-height: 1.6;
}

.step-block {
  border-radius: 10px;
  padding: 1rem;
  border: 1px solid;
}

.practice-block {
  border-color: #bfdbfe;
  background: #eff6ff;
}

.quiz-block {
  border-color: #fcd34d;
  background: #fffbeb;
}

.block-title {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

.step-block ul {
  margin: 0;
  padding-left: 1.25rem;
  color: #4b5563;
}

.quiz-item {
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 0.75rem;
  background: white;
  margin-top: 0.75rem;
}

.quiz-item:first-of-type {
  margin-top: 0;
}

.quiz-question {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.quiz-options {
  list-style: none;
  padding: 0;
  margin: 0 0 0.5rem;
}

.quiz-options li {
  display: flex;
  gap: 0.5rem;
  padding: 0.25rem 0;
  color: #374151;
}

.option-label {
  font-weight: 600;
  color: #6b7280;
}

.quiz-answer,
.quiz-explanation {
  font-size: 0.85rem;
  color: #92400e;
}

.bullet-list {
  margin: 1rem 0 0;
  padding-left: 1.2rem;
  color: #374151;
}

.faq-list {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.faq-item {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 1rem;
  background: #f9fafb;
}

.faq-question {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #111827;
}

.faq-answer {
  color: #4b5563;
  line-height: 1.6;
  white-space: pre-line;
}

.preview-empty {
  padding: 2rem;
  text-align: center;
  border: 1px dashed #d1d5db;
  border-radius: 12px;
  color: #6b7280;
  background: #f9fafb;
}

@media (max-width: 768px) {
  .preview-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .summary-cards {
    width: 100%;
    justify-content: space-between;
  }
}
</style>

