export type StepType = 'content' | 'quiz' | 'operation' | 'summary'

export interface CourseOption {
  value: string
  text: string
}

export interface CourseQuestion {
  id: string
  text: string
  options: CourseOption[]
  correctAnswer: string
  explanation?: string
  points?: number
}

export interface CoursePractice {
  title: string
  tasks: string[]
}

export interface KnowledgeCard {
  icon: string
  title: string
  content: string
}

export interface SubmissionConfig {
  enable: boolean
  title?: string
  description?: string
  successMessage?: string
}

export interface CanvasConfig {
  width: number  // 画布宽度（像素）
  height: number  // 画布高度（像素）
  backgroundColor?: string  // 画布背景色
  backgroundImage?: string  // 画布背景图
}

export type InteractionType = 'code' | 'drag-drop' | 'quiz' | 'video' | 'simulation' | 'drawing' | 'text' | 'title' | 'image'

export interface CodeEditorConfig {
  language: string
  template: string
  testCases: Array<{ input: string; output: string }>
  runButton: boolean
}

export interface DragDropConfig {
  items: Array<{ id: string; content: string; category: string }>
  targetZones: Array<{ id: string; label: string; accepts: string[] }>
}

export interface VideoInteractiveConfig {
  url: string
  checkpoints: Array<{ time: number; question: string }>
  progressTracking: boolean
}

export interface DrawingCanvasConfig {
  backgroundImage?: string
  tools: string[]
  saveOnComplete: boolean
}

export interface ComponentStyle {
  // 字体样式
  fontFamily?: string
  fontSize?: number
  fontWeight?: string | number
  fontStyle?: 'normal' | 'italic'
  color?: string
  textAlign?: 'left' | 'center' | 'right' | 'justify'
  
  // 背景样式
  backgroundColor?: string
  backgroundImage?: string
  
  // 边框样式
  borderWidth?: number
  borderStyle?: 'solid' | 'dashed' | 'dotted' | 'none'
  borderColor?: string
  borderRadius?: number
  
  // 阴影样式
  boxShadow?: string
  
  // 间距
  padding?: string
  margin?: string
  
  // 其他
  opacity?: number
  transform?: string
  zIndex?: number
}

export interface ComponentPosition {
  x: number  // 相对于画布的x坐标（像素）
  y: number  // 相对于画布的y坐标（像素）
  width: number  // 组件宽度（像素）
  height: number  // 组件高度（像素）
  rotation?: number  // 旋转角度（度）
}

export interface StepComponent {
  id: string
  type: InteractionType
  config: CodeEditorConfig | DragDropConfig | VideoInteractiveConfig | DrawingCanvasConfig | any
  position?: ComponentPosition  // 新增：位置信息
  style?: ComponentStyle  // 新增：样式信息
}

export interface CourseStep {
  id: string
  type: StepType
  title: string
  subtitle?: string
  duration?: string
  content?: string
  contentHtml?: string
  questions?: CourseQuestion[]
  practice?: CoursePractice
  knowledgeCard?: KnowledgeCard
  submission?: SubmissionConfig
  components?: StepComponent[]
  difficulty?: number
  canvasConfig?: CanvasConfig  // 新增：画布配置
}

export interface GamificationConfig {
  theme?: string
  difficulty?: number
  timeLimit?: number
  rewards?: {
    completion?: { exp: number; coins: number }
    perfect?: { exp: number; coins: number; badge?: string }
  }
  achievements?: Array<{
    id: string
    name: string
    description: string
    icon: string
    condition: string
    reward: { exp: number; coins: number }
  }>
}

export interface StoryConfig {
  intro?: string
  milestones?: Array<{
    stepIndex: number
    trigger: string
    content: string
  }>
  outro?: string
}

export interface CourseData {
  meta?: {
    title?: string
    preparations?: string[]
    goals?: Array<{
      title: string
      items: string[]
    }>
    scoreConfig?: {
      perQuestion?: number
      perPractice?: number
      completeBonus?: number
    }
  }
  steps: CourseStep[]
  gamification?: GamificationConfig
  story?: StoryConfig
  interactions?: {
    codeEditor?: boolean
    dragDrop?: boolean
    video?: boolean
    drawing?: boolean
    simulation?: boolean
  }
}


