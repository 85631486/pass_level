<template>
  <div class="video-container">
    <div class="video-wrapper">
      <video
        ref="videoRef"
        :src="videoUrl"
        @timeupdate="onTimeUpdate"
        @pause="onPause"
        @play="onPlay"
        controls
        class="video-player"
      />
    </div>
    <div v-if="currentCheckpoint" class="checkpoint-popup">
      <div class="checkpoint-content">
        <h4>{{ currentCheckpoint.question }}</h4>
        <div class="checkpoint-actions">
          <button @click="answerCheckpoint">回答</button>
          <button @click="skipCheckpoint">跳过</button>
        </div>
      </div>
    </div>
    <div class="progress-bar-container">
      <div class="progress-bar">
        <div
          v-for="cp in checkpoints"
          :key="cp.time"
          class="checkpoint-marker"
          :style="{ left: `${(cp.time / duration) * 100}%` }"
          :title="`检查点: ${formatTime(cp.time)}`"
        />
        <div
          class="progress-fill"
          :style="{ width: `${(currentTime / duration) * 100}%` }"
        />
      </div>
    </div>
    <div v-if="progressTracking" class="progress-info">
      <span>观看进度: {{ Math.round((currentTime / duration) * 100) }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Checkpoint {
  time: number
  question: string
}

interface Props {
  url?: string
  checkpoints?: Checkpoint[]
  progressTracking?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  url: '',
  checkpoints: () => [],
  progressTracking: true
})

const videoRef = ref<HTMLVideoElement | null>(null)
const videoUrl = ref(props.url)
const currentTime = ref(0)
const duration = ref(0)
const currentCheckpoint = ref<Checkpoint | null>(null)
const checkpoints = ref<Checkpoint[]>([...props.checkpoints])
const answeredCheckpoints = ref<Set<number>>(new Set())

function onTimeUpdate() {
  if (videoRef.value) {
    currentTime.value = videoRef.value.currentTime
    duration.value = videoRef.value.duration || 0
    
    // 检查是否到达检查点
    checkCheckpoints()
  }
}

function onPlay() {
  // 视频开始播放
}

function onPause() {
  // 视频暂停
}

function checkCheckpoints() {
  if (!videoRef.value || checkpoints.value.length === 0) return

  // 查找当前时间附近的检查点（±2秒容差）
  const checkpoint = checkpoints.value.find(cp => {
    if (answeredCheckpoints.value.has(cp.time)) return false
    return Math.abs(currentTime.value - cp.time) < 2
  })

  if (checkpoint) {
    // 暂停视频并显示检查点
    if (videoRef.value) {
      videoRef.value.pause()
    }
    currentCheckpoint.value = checkpoint
  }
}

function answerCheckpoint() {
  if (currentCheckpoint.value) {
    answeredCheckpoints.value.add(currentCheckpoint.value.time)
    currentCheckpoint.value = null
    // 继续播放
    if (videoRef.value) {
      videoRef.value.play()
    }
  }
}

function skipCheckpoint() {
  if (currentCheckpoint.value) {
    answeredCheckpoints.value.add(currentCheckpoint.value.time)
    currentCheckpoint.value = null
    // 继续播放
    if (videoRef.value) {
      videoRef.value.play()
    }
  }
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

onMounted(() => {
  if (videoRef.value) {
    videoRef.value.addEventListener('loadedmetadata', () => {
      if (videoRef.value) {
        duration.value = videoRef.value.duration
      }
    })
  }
})
</script>

<style scoped>
.video-container {
  position: relative;
  background: #000000;
  border-radius: 8px;
  overflow: hidden;
}

.video-wrapper {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 aspect ratio */
}

.video-player {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.checkpoint-popup {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  min-width: 300px;
}

.checkpoint-content h4 {
  margin: 0 0 1.5rem;
  font-size: 1.125rem;
  color: #1f2937;
}

.checkpoint-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.checkpoint-actions button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.2s;
}

.checkpoint-actions button:first-child {
  background: #3b82f6;
  color: white;
}

.checkpoint-actions button:first-child:hover {
  background: #2563eb;
}

.checkpoint-actions button:last-child {
  background: #e5e7eb;
  color: #374151;
}

.checkpoint-actions button:last-child:hover {
  background: #d1d5db;
}

.progress-bar-container {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
}

.progress-bar {
  position: relative;
  width: 100%;
  height: 100%;
}

.progress-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: #3b82f6;
  transition: width 0.1s linear;
}

.checkpoint-marker {
  position: absolute;
  top: 0;
  width: 4px;
  height: 100%;
  background: #f59e0b;
  cursor: pointer;
  z-index: 2;
}

.checkpoint-marker:hover {
  width: 6px;
  background: #f97316;
}

.progress-info {
  position: absolute;
  bottom: 10px;
  right: 10px;
  padding: 0.5rem 0.75rem;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 4px;
  font-size: 0.75rem;
}
</style>

