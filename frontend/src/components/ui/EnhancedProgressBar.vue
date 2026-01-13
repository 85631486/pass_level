<template>
  <div class="enhanced-progress">
    <div class="progress-track">
      <div
        class="progress-fill"
        :style="{ width: `${progress}%` }"
      >
        <div class="progress-glow" />
      </div>
      <div
        v-for="(milestone, idx) in milestones"
        :key="idx"
        class="milestone-marker"
        :style="{ left: `${milestone.position}%` }"
        :class="{ reached: progress >= milestone.position }"
        :title="milestone.label"
      >
        <div class="milestone-icon">{{ milestone.icon }}</div>
        <div class="milestone-label">{{ milestone.label }}</div>
      </div>
    </div>
    <div class="progress-text">
      <span>进度: {{ progress }}%</span>
      <span v-if="nextMilestone" class="next-milestone">
        下一个里程碑: {{ nextMilestone.label }} ({{ nextMilestone.position }}%)
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Milestone {
  position: number
  label: string
  icon: string
}

interface Props {
  progress: number
  milestones?: Milestone[]
}

const props = withDefaults(defineProps<Props>(), {
  progress: 0,
  milestones: () => [
    { position: 25, label: '四分之一', icon: '🎯' },
    { position: 50, label: '一半', icon: '⭐' },
    { position: 75, label: '四分之三', icon: '🔥' },
    { position: 100, label: '完成', icon: '🏆' }
  ]
})

const nextMilestone = computed(() => {
  return props.milestones.find(m => props.progress < m.position)
})
</script>

<style scoped>
.enhanced-progress {
  padding: 1rem;
}

.progress-track {
  position: relative;
  width: 100%;
  height: 12px;
  background: #e5e7eb;
  border-radius: 999px;
  overflow: visible;
  margin-bottom: 2rem;
}

.progress-fill {
  position: relative;
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #10b981);
  border-radius: 999px;
  transition: width 0.5s ease;
  overflow: visible;
}

.progress-glow {
  position: absolute;
  top: 0;
  right: 0;
  width: 20px;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5));
  border-radius: 999px;
  animation: glowPulse 2s ease-in-out infinite;
}

.milestone-marker {
  position: absolute;
  top: -8px;
  transform: translateX(-50%);
  transition: all 0.3s ease;
}

.milestone-marker.reached {
  animation: milestoneReached 0.5s ease-out;
}

.milestone-icon {
  font-size: 1.5rem;
  text-align: center;
  margin-bottom: 0.25rem;
  filter: grayscale(1);
  transition: all 0.3s ease;
}

.milestone-marker.reached .milestone-icon {
  filter: grayscale(0);
  transform: scale(1.2);
}

.milestone-label {
  font-size: 0.75rem;
  color: #6b7280;
  text-align: center;
  white-space: nowrap;
}

.milestone-marker.reached .milestone-label {
  color: #10b981;
  font-weight: 600;
}

.progress-text {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: #6b7280;
}

.next-milestone {
  color: #3b82f6;
  font-weight: 500;
}

@keyframes glowPulse {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

@keyframes milestoneReached {
  0% {
    transform: translateX(-50%) scale(1);
  }
  50% {
    transform: translateX(-50%) scale(1.3);
  }
  100% {
    transform: translateX(-50%) scale(1.2);
  }
}
</style>

