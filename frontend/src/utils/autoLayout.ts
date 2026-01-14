/**
 * 自动布局算法工具
 * 用于在可视化编辑器中自动排列组件，避免重叠
 */

import type { StepComponent } from '../types/coursePlayer'

export interface LayoutPosition {
  x: number
  y: number
  width: number
  height: number
}

/**
 * 组件类型的默认尺寸配置
 */
export const DEFAULT_COMPONENT_SIZES: Record<string, { width: number; height: number }> = {
  text: { width: 1200, height: 80 },           // 标题：宽度 100%（假设画布 1200px），高度 80px
  code: { width: 1200, height: 300 },          // 代码编辑器：宽度 100%，高度 300px
  quiz: { width: 1200, height: 250 },          // 题目：宽度 100%，高度 250px
  video: { width: 600, height: 400 },          // 视频：宽度 50%，高度 400px
  image: { width: 600, height: 400 },          // 图片：宽度 50%，高度 400px
  drawing: { width: 800, height: 500 },        // 绘图：宽度 66%，高度 500px
  dragdrop: { width: 1200, height: 300 },      // 拖拽排序：宽度 100%，高度 300px
}

/**
 * 检测两个矩形是否重叠
 */
export function isOverlapping(rect1: LayoutPosition, rect2: LayoutPosition, margin: number = 10): boolean {
  return !(
    rect1.x + rect1.width + margin <= rect2.x ||
    rect2.x + rect2.width + margin <= rect1.x ||
    rect1.y + rect1.height + margin <= rect2.y ||
    rect2.y + rect2.height + margin <= rect1.y
  )
}

/**
 * 自动布局算法：按从上到下、从左到右的方式排列组件
 * @param components 组件列表
 * @param canvasWidth 画布宽度（默认 1200）
 * @param canvasHeight 画布高度（默认 1080）
 * @param margin 组件间距（默认 20）
 * @returns 布局后的组件列表
 */
export function autoLayoutComponents(
  components: StepComponent[],
  canvasWidth: number = 1200,
  canvasHeight: number = 1080,
  margin: number = 20
): StepComponent[] {
  if (components.length === 0) return components

  // 克隆组件以避免修改原数组
  const layoutedComponents = components.map(c => ({ ...c }))

  // 第一步：为没有位置信息的组件设置默认位置
  let currentY = margin
  let currentX = margin

  for (let i = 0; i < layoutedComponents.length; i++) {
    const component = layoutedComponents[i]

    // 如果组件没有位置信息，或位置为 (0, 0)，则需要重新布局
    if (!component.position || (component.position.x === 0 && component.position.y === 0)) {
      const defaultSize = DEFAULT_COMPONENT_SIZES[component.type] || { width: 600, height: 200 }
      const width = Math.min(defaultSize.width, canvasWidth - 2 * margin)
      const height = defaultSize.height

      // 检查当前行是否还有空间
      if (currentX + width + margin > canvasWidth) {
        // 换行
        currentX = margin
        currentY += height + margin
      }

      // 检查是否超出画布高度
      if (currentY + height > canvasHeight) {
        currentY = Math.max(margin, canvasHeight - height - margin)
      }

      component.position = {
        x: currentX,
        y: currentY,
        width,
        height,
        rotation: 0
      }

      // 更新当前位置（用于下一个组件）
      currentX += width + margin
    }
  }

  // 第二步：检测并解决重叠问题
  const MAX_ITERATIONS = 10
  let hasOverlap = true
  let iterations = 0

  while (hasOverlap && iterations < MAX_ITERATIONS) {
    hasOverlap = false
    iterations++

    for (let i = 0; i < layoutedComponents.length; i++) {
      for (let j = i + 1; j < layoutedComponents.length; j++) {
        const comp1 = layoutedComponents[i]
        const comp2 = layoutedComponents[j]

        if (comp1.position && comp2.position && isOverlapping(comp1.position, comp2.position, margin)) {
          hasOverlap = true

          // 将 comp2 移到 comp1 下方
          comp2.position.y = comp1.position.y + comp1.position.height + margin

          // 检查是否超出画布
          if (comp2.position.y + comp2.position.height > canvasHeight) {
            comp2.position.y = Math.max(margin, canvasHeight - comp2.position.height - margin)
          }
        }
      }
    }
  }

  return layoutedComponents
}

/**
 * 检测组件列表中是否存在重叠
 */
export function hasOverlappingComponents(components: StepComponent[], margin: number = 10): boolean {
  for (let i = 0; i < components.length; i++) {
    for (let j = i + 1; j < components.length; j++) {
      const pos1 = components[i].position
      const pos2 = components[j].position
      if (pos1 && pos2 && isOverlapping(pos1, pos2, margin)) {
        return true
      }
    }
  }
  return false
}

/**
 * 为组件分配合理的默认尺寸
 */
export function assignDefaultSize(component: StepComponent, canvasWidth: number = 1200): void {
  if (!component.position) {
    component.position = { x: 0, y: 0, width: 600, height: 200, rotation: 0 }
  }

  const defaultSize = DEFAULT_COMPONENT_SIZES[component.type]
  if (defaultSize) {
    component.position.width = Math.min(defaultSize.width, canvasWidth - 40)
    component.position.height = defaultSize.height
  }
}
