import { marked } from 'marked'
import {
  parseTeachingGuide,
  type TeachingGuideParsed,
  type TeachingGuideStep,
  type TeachingGuideQuestion,
} from './teachingGuideParser'

export interface KnowledgeCard {
  icon: string
  title: string
  content: string
}

export interface InteractiveQuiz extends TeachingGuideQuestion {
  id: string
}

export interface InteractiveStep {
  id: string
  title: string
  subtitle?: string
  duration?: string
  type: 'content' | 'operation' | 'quiz'
  contentHtml: string
  practiceTasks: string[]
  quiz: InteractiveQuiz[]
  knowledgeCard?: KnowledgeCard
}

export interface InteractiveMeta {
  title: string
  duration?: string
  goals: TeachingGuideParsed['goals']
  preparations: string[]
  homework: string[]
  faq: TeachingGuideParsed['faq']
  tips: string[]
  checklist: string[]
}

export interface InteractiveCourse {
  meta: InteractiveMeta
  steps: InteractiveStep[]
}

const DEFAULT_KNOWLEDGE_ICONS = ['💡', '🔥', '📌', '🎯', '🧠', '⚡️']

marked.setOptions({
  breaks: true,
  gfm: true,
})

export function buildInteractiveCourse(md: string): InteractiveCourse | null {
  const parsed = parseTeachingGuide(md)
  if (!parsed) return null

  const steps = parsed.steps.map((step, index) =>
    convertStepToInteractive(step, index)
  )

  return {
    meta: {
      title: parsed.title,
      duration: parsed.duration,
      goals: parsed.goals,
      preparations: parsed.preparations,
      homework: parsed.homework,
      faq: parsed.faq,
      tips: parsed.tips,
      checklist: parsed.checklist,
    },
    steps,
  }
}

function convertStepToInteractive(
  step: TeachingGuideStep,
  index: number
): InteractiveStep {
  const html = renderSummary(step)
  const practice = step.practice || []
  const quiz = (step.quiz || []).map((question, idx) => ({
    ...question,
    id: `${step.title}-quiz-${idx + 1}`,
  }))

  return {
    id: `step-${index + 1}`,
    title: step.title,
    subtitle: step.duration
      ? `${step.title}（${step.duration}）`
      : step.title,
    duration: step.duration,
    type: quiz.length ? 'operation' : 'content',
    contentHtml: html,
    practiceTasks: practice,
    quiz,
    knowledgeCard: createKnowledgeCard(step, index),
  }
}

function renderSummary(step: TeachingGuideStep): string {
  const summary = step.summary?.join('\n\n').trim() || ''
  if (!summary) return ''
  return marked.parse(summary)
}

function createKnowledgeCard(
  step: TeachingGuideStep,
  index: number
): KnowledgeCard | undefined {
  const summary = step.summary || []
  if (!summary.length) return undefined
  return {
    icon: DEFAULT_KNOWLEDGE_ICONS[index % DEFAULT_KNOWLEDGE_ICONS.length],
    title: step.title,
    content: summary[0],
  }
}















