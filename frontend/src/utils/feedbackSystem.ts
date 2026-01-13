export type FeedbackType = 'success' | 'error' | 'levelup' | 'achievement'

export class FeedbackSystem {
  private toastContainer: HTMLElement | null = null

  constructor() {
    this.initToastContainer()
  }

  private initToastContainer() {
    if (typeof document !== 'undefined') {
      this.toastContainer = document.createElement('div')
      this.toastContainer.className = 'feedback-toast-container'
      this.toastContainer.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        pointer-events: none;
      `
      document.body.appendChild(this.toastContainer)
    }
  }

  // 答题反馈
  showAnswerFeedback(correct: boolean, points: number) {
    if (correct) {
      this.showParticleEffect('success')
      this.playSound('correct')
      this.showToast(`✅ 回答正确！+${points}分`, 'success')
      this.addScoreAnimation(points)
    } else {
      this.showParticleEffect('error')
      this.playSound('incorrect')
      this.showToast('❌ 回答错误，再想想', 'error')
    }
  }

  // 粒子特效
  showParticleEffect(type: FeedbackType) {
    if (typeof window === 'undefined') return

    // 使用简单的CSS动画模拟粒子效果
    const particle = document.createElement('div')
    particle.className = `particle-effect particle-${type}`
    particle.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 100px;
      height: 100px;
      pointer-events: none;
      z-index: 9999;
    `

    if (type === 'success') {
      particle.innerHTML = '✨'
      particle.style.fontSize = '60px'
      particle.style.animation = 'particleSuccess 1s ease-out forwards'
    } else if (type === 'error') {
      particle.innerHTML = '💥'
      particle.style.fontSize = '60px'
      particle.style.animation = 'particleError 1s ease-out forwards'
    } else if (type === 'levelup') {
      particle.innerHTML = '🎉'
      particle.style.fontSize = '80px'
      particle.style.animation = 'particleLevelUp 2s ease-out forwards'
    } else if (type === 'achievement') {
      particle.innerHTML = '🏆'
      particle.style.fontSize = '80px'
      particle.style.animation = 'particleAchievement 2s ease-out forwards'
    }

    document.body.appendChild(particle)

    setTimeout(() => {
      particle.remove()
    }, type === 'levelup' || type === 'achievement' ? 2000 : 1000)

    // 添加CSS动画（如果还没有）
    this.ensureAnimationStyles()
  }

  // 音效
  playSound(type: string) {
    if (typeof Audio === 'undefined') return

    try {
      // 使用Web Audio API生成简单音效
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      const oscillator = audioContext.createOscillator()
      const gainNode = audioContext.createGain()

      oscillator.connect(gainNode)
      gainNode.connect(audioContext.destination)

      if (type === 'correct') {
        oscillator.frequency.value = 800
        oscillator.type = 'sine'
      } else if (type === 'incorrect') {
        oscillator.frequency.value = 300
        oscillator.type = 'sawtooth'
      } else if (type === 'levelup') {
        oscillator.frequency.value = 600
        oscillator.type = 'sine'
      }

      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3)

      oscillator.start(audioContext.currentTime)
      oscillator.stop(audioContext.currentTime + 0.3)
    } catch (error) {
      // 如果Web Audio API不可用，静默失败
      console.warn('Audio playback not available:', error)
    }
  }

  // Toast提示
  showToast(message: string, type: 'success' | 'error' | 'info' = 'info') {
    if (!this.toastContainer) return

    const toast = document.createElement('div')
    toast.className = `feedback-toast feedback-toast-${type}`
    toast.textContent = message
    toast.style.cssText = `
      padding: 0.75rem 1.25rem;
      margin-bottom: 0.5rem;
      background: ${type === 'success' ? '#ecfdf5' : type === 'error' ? '#fee2e2' : '#eff6ff'};
      color: ${type === 'success' ? '#059669' : type === 'error' ? '#dc2626' : '#1e40af'};
      border: 1px solid ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
      border-radius: 8px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      animation: toastSlideIn 0.3s ease-out;
      pointer-events: auto;
      font-size: 0.875rem;
      font-weight: 500;
    `

    this.toastContainer.appendChild(toast)

    setTimeout(() => {
      toast.style.animation = 'toastSlideOut 0.3s ease-out forwards'
      setTimeout(() => {
        toast.remove()
      }, 300)
    }, 3000)
  }

  // 分数动画
  addScoreAnimation(points: number) {
    if (typeof document === 'undefined') return

    const scoreElement = document.createElement('div')
    scoreElement.className = 'score-animation'
    scoreElement.textContent = `+${points}`
    scoreElement.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: 2rem;
      font-weight: 700;
      color: #10b981;
      pointer-events: none;
      z-index: 9998;
      animation: scoreFloat 1.5s ease-out forwards;
      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    `

    document.body.appendChild(scoreElement)

    setTimeout(() => {
      scoreElement.remove()
    }, 1500)

    this.ensureAnimationStyles()
  }

  // 确保动画样式已添加
  private ensureAnimationStyles() {
    if (typeof document === 'undefined') return

    const styleId = 'feedback-animations'
    if (document.getElementById(styleId)) return

    const style = document.createElement('style')
    style.id = styleId
    style.textContent = `
      @keyframes particleSuccess {
        0% {
          transform: translate(-50%, -50%) scale(0);
          opacity: 1;
        }
        50% {
          transform: translate(-50%, -50%) scale(1.2);
          opacity: 1;
        }
        100% {
          transform: translate(-50%, -50%) scale(0.8);
          opacity: 0;
        }
      }

      @keyframes particleError {
        0% {
          transform: translate(-50%, -50%) scale(0) rotate(0deg);
          opacity: 1;
        }
        50% {
          transform: translate(-50%, -50%) scale(1.5) rotate(180deg);
          opacity: 1;
        }
        100% {
          transform: translate(-50%, -50%) scale(0) rotate(360deg);
          opacity: 0;
        }
      }

      @keyframes particleLevelUp {
        0% {
          transform: translate(-50%, -50%) scale(0);
          opacity: 1;
        }
        30% {
          transform: translate(-50%, -50%) scale(1.5);
          opacity: 1;
        }
        100% {
          transform: translate(-50%, -50%) scale(1);
          opacity: 0;
        }
      }

      @keyframes particleAchievement {
        0% {
          transform: translate(-50%, -50%) scale(0) rotateY(0deg);
          opacity: 1;
        }
        50% {
          transform: translate(-50%, -50%) scale(1.3) rotateY(180deg);
          opacity: 1;
        }
        100% {
          transform: translate(-50%, -50%) scale(1) rotateY(360deg);
          opacity: 0;
        }
      }

      @keyframes toastSlideIn {
        from {
          transform: translateX(100%);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }

      @keyframes toastSlideOut {
        from {
          transform: translateX(0);
          opacity: 1;
        }
        to {
          transform: translateX(100%);
          opacity: 0;
        }
      }

      @keyframes scoreFloat {
        0% {
          transform: translate(-50%, -50%) translateY(0);
          opacity: 1;
        }
        100% {
          transform: translate(-50%, -50%) translateY(-100px);
          opacity: 0;
        }
      }
    `
    document.head.appendChild(style)
  }

  // 清理
  destroy() {
    if (this.toastContainer) {
      this.toastContainer.remove()
      this.toastContainer = null
    }
  }
}

// 单例
let feedbackSystemInstance: FeedbackSystem | null = null

export function getFeedbackSystem(): FeedbackSystem {
  if (!feedbackSystemInstance) {
    feedbackSystemInstance = new FeedbackSystem()
  }
  return feedbackSystemInstance
}

