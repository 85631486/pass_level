export interface Achievement {
  id: string
  name: string
  description: string
  icon: string
  condition: (state: AchievementState) => boolean
  reward: {
    exp: number
    coins: number
    badge?: string
  }
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
}

export interface AchievementState {
  completedSteps: number
  correctAnswers: number
  totalQuestions: number
  collectedCards: number
  currentStepTime: number
  progressPercent: number
  correctRate: number
}

export class AchievementSystem {
  private achievements: Achievement[] = []
  private unlocked: Set<string> = new Set()
  private onUnlockCallback?: (achievement: Achievement) => void

  constructor(onUnlock?: (achievement: Achievement) => void) {
    this.onUnlockCallback = onUnlock
    this.initAchievements()
  }

  private initAchievements() {
    this.achievements = [
      {
        id: 'first-step',
        name: '初出茅庐',
        description: '完成第一个步骤',
        icon: '🌱',
        condition: (state) => state.completedSteps >= 1,
        reward: { exp: 10, coins: 5 },
        rarity: 'common'
      },
      {
        id: 'speed-demon',
        name: '速度之星',
        description: '在5分钟内完成一个步骤',
        icon: '⚡',
        condition: (state) => state.currentStepTime < 300,
        reward: { exp: 50, coins: 20 },
        rarity: 'rare'
      },
      {
        id: 'perfect-score',
        name: '完美通关',
        description: '所有题目全部答对',
        icon: '🏆',
        condition: (state) => state.correctRate === 1 && state.totalQuestions > 0,
        reward: { exp: 100, coins: 50, badge: 'perfect' },
        rarity: 'epic'
      },
      {
        id: 'knowledge-collector',
        name: '知识收集者',
        description: '收集5张知识卡片',
        icon: '📚',
        condition: (state) => state.collectedCards >= 5,
        reward: { exp: 30, coins: 15 },
        rarity: 'rare'
      },
      {
        id: 'question-master',
        name: '答题达人',
        description: '答对10道题目',
        icon: '🎯',
        condition: (state) => state.correctAnswers >= 10,
        reward: { exp: 40, coins: 20 },
        rarity: 'rare'
      },
      {
        id: 'completionist',
        name: '完美通关',
        description: '完成所有步骤',
        icon: '💯',
        condition: (state) => state.progressPercent === 100,
        reward: { exp: 80, coins: 40 },
        rarity: 'epic'
      }
    ]
  }

  checkAchievements(state: AchievementState) {
    this.achievements.forEach(achievement => {
      if (achievement.condition(state) && !this.unlocked.has(achievement.id)) {
        this.unlockAchievement(achievement)
      }
    })
  }

  unlockAchievement(achievement: Achievement) {
    this.unlocked.add(achievement.id)
    
    // 触发回调
    if (this.onUnlockCallback) {
      this.onUnlockCallback(achievement)
    }

    // 保存到本地存储
    this.saveUnlocked()
  }

  isUnlocked(achievementId: string): boolean {
    return this.unlocked.has(achievementId)
  }

  getUnlockedAchievements(): Achievement[] {
    return this.achievements.filter(a => this.unlocked.has(a.id))
  }

  getAllAchievements(): Achievement[] {
    return [...this.achievements]
  }

  private saveUnlocked() {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('unlocked_achievements', JSON.stringify(Array.from(this.unlocked)))
    }
  }

  loadUnlocked() {
    if (typeof localStorage !== 'undefined') {
      const saved = localStorage.getItem('unlocked_achievements')
      if (saved) {
        try {
          this.unlocked = new Set(JSON.parse(saved))
        } catch (error) {
          console.error('Failed to load unlocked achievements:', error)
        }
      }
    }
  }

  reset() {
    this.unlocked.clear()
    this.saveUnlocked()
  }
}

