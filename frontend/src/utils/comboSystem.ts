export class ComboSystem {
  private comboCount = 0
  private comboTimer: number | null = null
  private onComboCallback?: (count: number) => void
  private onComboBonusCallback?: (count: number, bonus: number) => void

  constructor(
    onCombo?: (count: number) => void,
    onComboBonus?: (count: number, bonus: number) => void
  ) {
    this.onComboCallback = onCombo
    this.onComboBonusCallback = onComboBonus
  }

  addCombo() {
    this.comboCount++
    this.resetTimer()
    this.showComboEffect()

    // 触发连击回调
    if (this.onComboCallback) {
      this.onComboCallback(this.comboCount)
    }

    // 检查连击奖励
    if (this.comboCount >= 3) {
      this.triggerComboBonus()
    }
  }

  private showComboEffect() {
    if (typeof document === 'undefined') return

    // 移除旧的连击显示
    const oldCombo = document.querySelector('.combo-display')
    if (oldCombo) {
      oldCombo.remove()
    }

    // 创建新的连击显示
    const comboDisplay = document.createElement('div')
    comboDisplay.className = 'combo-display'
    comboDisplay.textContent = `${this.comboCount} 连击！`
    comboDisplay.style.cssText = `
      position: fixed;
      top: 20%;
      left: 50%;
      transform: translateX(-50%);
      font-size: 2rem;
      font-weight: 700;
      color: #f59e0b;
      pointer-events: none;
      z-index: 9999;
      animation: comboPulse 0.5s ease-out;
      text-shadow: 0 2px 8px rgba(245, 158, 11, 0.5);
    `

    document.body.appendChild(comboDisplay)

    setTimeout(() => {
      comboDisplay.style.animation = 'comboFadeOut 0.5s ease-out forwards'
      setTimeout(() => {
        comboDisplay.remove()
      }, 500)
    }, 1000)

    this.ensureAnimationStyles()
  }

  private triggerComboBonus() {
    let bonusExp = 0
    let bonusCoins = 0

    if (this.comboCount === 3) {
      bonusExp = 5 // 额外10%经验
      bonusCoins = 2
    } else if (this.comboCount === 5) {
      bonusExp = 10 // 额外20%经验
      bonusCoins = 5
    } else if (this.comboCount === 10) {
      bonusExp = 25 // 额外50%经验
      bonusCoins = 10
    }

    if (bonusExp > 0 && this.onComboBonusCallback) {
      this.onComboBonusCallback(this.comboCount, bonusExp)
    }
  }

  private resetTimer() {
    if (this.comboTimer) {
      clearTimeout(this.comboTimer)
    }

    // 5秒内没有新的连击，重置计数
    this.comboTimer = window.setTimeout(() => {
      this.comboCount = 0
      this.comboTimer = null
    }, 5000)
  }

  getComboCount(): number {
    return this.comboCount
  }

  reset() {
    this.comboCount = 0
    if (this.comboTimer) {
      clearTimeout(this.comboTimer)
      this.comboTimer = null
    }
  }

  private ensureAnimationStyles() {
    if (typeof document === 'undefined') return

    const styleId = 'combo-animations'
    if (document.getElementById(styleId)) return

    const style = document.createElement('style')
    style.id = styleId
    style.textContent = `
      @keyframes comboPulse {
        0% {
          transform: translateX(-50%) scale(0.5);
          opacity: 0;
        }
        50% {
          transform: translateX(-50%) scale(1.2);
          opacity: 1;
        }
        100% {
          transform: translateX(-50%) scale(1);
          opacity: 1;
        }
      }

      @keyframes comboFadeOut {
        from {
          transform: translateX(-50%) translateY(0);
          opacity: 1;
        }
        to {
          transform: translateX(-50%) translateY(-50px);
          opacity: 0;
        }
      }
    `
    document.head.appendChild(style)
  }
}

