export interface TeachingGuideGoalGroup {
  title: string
  items: string[]
}

export interface TeachingGuideQuestion {
  question: string
  options: string[]
  answer?: string
  explanation?: string
}

export interface TeachingGuideStep {
  title: string
  duration?: string
  summary: string[]
  practice?: string[]
  quiz?: TeachingGuideQuestion[]
  raw?: string
}

export interface TeachingGuideFAQ {
  question: string
  answer: string
}

export interface TeachingGuideParsed {
  title: string
  sections: Record<string, string>
  goals: TeachingGuideGoalGroup[]
  duration?: string
  timeAllocations: string[]
  preparations: string[]
  steps: TeachingGuideStep[]
  homework: string[]
  faq: TeachingGuideFAQ[]
  tips: string[]
  checklist: string[]
}

const SECTION_TITLE_REGEX = /^##\s+(.+)$/gm
const STEP_TITLE_REGEX = /^###\s+(.+)$/m

export function parseTeachingGuide(md: string): TeachingGuideParsed | null {
  if (!md || !md.trim()) {
    return null
  }

  const lines = md.split('\n')
  let title = ''
  const sections: Record<string, string> = {}
  let currentSection: string | null = null
  let buffer: string[] = []

  const flushSection = () => {
    if (currentSection) {
      sections[currentSection] = buffer.join('\n').trim()
    }
    buffer = []
  }

  for (const line of lines) {
    if (line.startsWith('# ')) {
      if (!title) {
        title = line.replace(/^#\s+/, '').trim()
        continue
      }
    }
    const sectionMatch = line.match(/^##\s+(.+)/)
    if (sectionMatch) {
      flushSection()
      currentSection = sectionMatch[1].trim()
      continue
    }
    buffer.push(line)
  }
  flushSection()

  const goals = parseGoals(sections)
  const { duration, timeAllocations } = parseDuration(sections)
  const preparations = parsePreparations(sections)
  const steps = parseSteps(sections)
  const homework = parseHomework(sections)
  const faq = parseFAQ(sections)
  const tips = parseTips(sections)
  const checklist = parseChecklist(sections)

  return {
    title: title || '未命名任务',
    sections,
    goals,
    duration,
    timeAllocations,
    preparations,
    steps,
    homework,
    faq,
    tips,
    checklist,
  }
}

function parseGoals(sections: Record<string, string>): TeachingGuideGoalGroup[] {
  const sectionKey = Object.keys(sections).find((key) => key.includes('学习目标'))
  if (!sectionKey) return []
  const text = sections[sectionKey]
  const lines = text.split('\n')
  const result: TeachingGuideGoalGroup[] = []
  let currentGroup: TeachingGuideGoalGroup | null = null

  for (const rawLine of lines) {
    const line = rawLine.trim()
    if (!line) continue

    const groupMatch = line.match(/^\d+\.\s*\*\*(.+?)\*\*/)
    if (groupMatch) {
      if (currentGroup) result.push(currentGroup)
      currentGroup = {
        title: groupMatch[1],
        items: [],
      }
      continue
    }

    if (/^[-*]\s+/.test(line)) {
      if (!currentGroup) {
        currentGroup = { title: '目标', items: [] }
      }
      currentGroup.items.push(line.replace(/^[-*]\s+/, ''))
    }
  }

  if (currentGroup) result.push(currentGroup)
  return result
}

function parseDuration(sections: Record<string, string>): { duration?: string; timeAllocations: string[] } {
  const sectionKey = Object.keys(sections).find((key) => key.includes('任务时间'))
  if (!sectionKey) return { timeAllocations: [] }
  const text = sections[sectionKey]
  const lines = text.split('\n').map((line) => line.trim()).filter(Boolean)
  let duration: string | undefined
  const allocations: string[] = []

  lines.forEach((line) => {
    if (line.startsWith('-')) {
      const cleaned = line.replace(/^-+\s*/, '')
      if (!duration && cleaned.includes('总时长')) {
        duration = cleaned.replace(/\*\*/g, '')
      } else {
        allocations.push(cleaned.replace(/\*\*/g, ''))
      }
    }
  })

  return { duration, timeAllocations: allocations }
}

function parsePreparations(sections: Record<string, string>): string[] {
  const sectionKey = Object.keys(sections).find((key) => key.includes('准备工作'))
  if (!sectionKey) return []
  const text = sections[sectionKey]
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => /^[-*]\s+/.test(line))
    .map((line) => line.replace(/^[-*]\s+/, '').replace(/\[ \]/g, '').trim())
}

function parseSteps(sections: Record<string, string>): TeachingGuideStep[] {
  const sectionKey = Object.keys(sections).find((key) => key.includes('操作步骤'))
  if (!sectionKey) return []
  const text = sections[sectionKey]
  const blocks = text.split(/\n(?=###\s+)/).map((block) => block.trim()).filter(Boolean)

  return blocks.map((block) => {
    const lines = block.split('\n')
    const titleLine = lines.shift() || ''
    const titleMatch = titleLine.match(/^###\s+(.+)/)
    const title = titleMatch ? titleMatch[1].trim() : titleLine
    const durationMatch = title.match(/（(.+?)）/)
    const duration = durationMatch ? durationMatch[1] : undefined

    const summary: string[] = []
    const practice: string[] = []
    const quiz: TeachingGuideQuestion[] = []

    let currentBuffer: string[] = []
    let currentMode: 'summary' | 'practice' | 'quiz' = 'summary'

    const flushBuffer = () => {
      if (!currentBuffer.length) return
      const content = currentBuffer.join('\n').trim()
      if (!content) {
        currentBuffer = []
        return
      }
      if (currentMode === 'summary') {
        summary.push(...splitParagraphs(content))
      } else if (currentMode === 'practice') {
        practice.push(...extractListItems(content))
      } else if (currentMode === 'quiz') {
        quiz.push(...parseQuiz(content))
      }
      currentBuffer = []
    }

    for (const rawLine of lines) {
      const line = rawLine.trim()
      if (line.startsWith('####')) {
        flushBuffer()
        if (line.includes('课堂问答')) {
          currentMode = 'quiz'
        } else if (line.includes('立即动手') || line.includes('练习')) {
          currentMode = 'practice'
        } else {
          currentMode = 'summary'
        }
        continue
      }
      currentBuffer.push(rawLine)
    }
    flushBuffer()

    return {
      title,
      duration,
      summary,
      practice,
      quiz,
      raw: block,
    }
  })
}

function splitParagraphs(text: string): string[] {
  return text
    .split(/\n{2,}/)
    .map((para) => para.replace(/\s+/g, ' ').trim())
    .filter(Boolean)
}

function extractListItems(text: string): string[] {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => /^([-*]|\d+\.)\s+/.test(line))
    .map((line) => line.replace(/^([-*]|\d+\.)\s+/, '').trim())
}

function parseQuiz(text: string): TeachingGuideQuestion[] {
  const lines = text.split('\n')
  const questions: TeachingGuideQuestion[] = []
  let current: TeachingGuideQuestion | null = null

  const pushCurrent = () => {
    if (current) questions.push(current)
    current = null
  }

  for (const rawLine of lines) {
    const line = rawLine.trim()
    if (!line) continue

    const questionMatch = line.match(/^\*\*问题\d+：\s*\*\*(.+)$/)
    if (questionMatch) {
      pushCurrent()
      current = {
        question: questionMatch[1].trim(),
        options: [],
      }
      continue
    }

    const optionMatch = line.match(/^[A-D]\.\s*(.+)$/)
    if (optionMatch && current) {
      current.options.push(optionMatch[1].trim())
      continue
    }

    const answerMatch = line.match(/^\*\*正确答案[:：]\s*([A-D])\*\*/)
    if (answerMatch && current) {
      current.answer = answerMatch[1]
      continue
    }

    const explanationMatch = line.match(/^\*\*解析[:：]\s*(.+)$/)
    if (explanationMatch && current) {
      current.explanation = explanationMatch[1].trim()
      continue
    }
  }
  pushCurrent()
  return questions
}

function parseHomework(sections: Record<string, string>): string[] {
  const sectionKey = Object.keys(sections).find((key) => key.includes('作业要求'))
  if (!sectionKey) return []
  return extractListItems(sections[sectionKey])
}

function parseFAQ(sections: Record<string, string>): TeachingGuideFAQ[] {
  const sectionKey = Object.keys(sections).find((key) => key.includes('常见问题'))
  if (!sectionKey) return []
  const text = sections[sectionKey]
  const lines = text.split('\n')
  const faq: TeachingGuideFAQ[] = []
  let current: TeachingGuideFAQ | null = null

  for (const rawLine of lines) {
    const line = rawLine.trim()
    if (!line) continue
    if (line.startsWith('###')) {
      if (current) faq.push(current)
      current = { question: line.replace(/^###\s*/, ''), answer: '' }
    } else if (line.startsWith('**A:**')) {
      if (current) current.answer = line.replace('**A:**', '').trim()
    } else if (current) {
      current.answer += (current.answer ? '\n' : '') + line
    }
  }
  if (current) faq.push(current)
  return faq
}

function parseTips(sections: Record<string, string>): string[] {
  const sectionKey = Object.keys(sections).find((key) => key.includes('学习提示'))
  if (!sectionKey) return []
  return extractListItems(sections[sectionKey])
}

function parseChecklist(sections: Record<string, string>): string[] {
  const sectionKey = Object.keys(sections).find((key) => key.includes('自我检查'))
  if (!sectionKey) return []
  return sections[sectionKey]
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.startsWith('- ['))
    .map((line) => line.replace(/- \[(x| )\]\s*/i, '').trim())
}















