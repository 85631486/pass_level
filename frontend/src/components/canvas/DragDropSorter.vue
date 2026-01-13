<template>
  <div class="drag-drop-container">
    <div class="source-zone">
      <h4>请将以下内容拖到正确位置</h4>
      <div class="items-list">
        <div
          v-for="item in items"
          :key="item.id"
          class="draggable-item"
          :class="{ dragged: draggedItemId === item.id }"
          draggable="true"
          @dragstart="handleDragStart($event, item)"
          @dragend="handleDragEnd"
        >
          {{ item.content }}
        </div>
      </div>
    </div>
    <div class="target-zones">
      <div
        v-for="zone in targetZones"
        :key="zone.id"
        class="drop-zone"
        :class="{ 
          correct: isCorrect(zone),
          over: draggedOverZoneId === zone.id
        }"
        @drop="handleDrop($event, zone)"
        @dragover.prevent
        @dragenter="handleDragEnter(zone.id)"
        @dragleave="handleDragLeave"
      >
        <h5>{{ zone.label }}</h5>
        <div class="dropped-items">
          <div
            v-for="(item, idx) in getDroppedItems(zone.id)"
            :key="item.id"
            class="dropped-item"
          >
            {{ item.content }}
            <button @click="removeItem(zone.id, idx)">×</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="allCorrect" class="success-message">
      ✅ 全部正确！
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface DragDropItem {
  id: string
  content: string
  category: string
}

interface TargetZone {
  id: string
  label: string
  accepts: string[]
}

interface Props {
  items?: DragDropItem[]
  targetZones?: TargetZone[]
}

const props = withDefaults(defineProps<Props>(), {
  items: () => [],
  targetZones: () => []
})

const items = ref<DragDropItem[]>([...props.items])
const targetZones = ref<TargetZone[]>([...props.targetZones])
const zoneItems = ref<Record<string, DragDropItem[]>>({})
const draggedItemId = ref<string | null>(null)
const draggedOverZoneId = ref<string | null>(null)

// 初始化zoneItems
targetZones.value.forEach(zone => {
  zoneItems.value[zone.id] = []
})

const allCorrect = computed(() => {
  return targetZones.value.every(zone => isCorrect(zone))
})

function handleDragStart(event: DragEvent, item: DragDropItem) {
  draggedItemId.value = item.id
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
  }
}

function handleDragEnd() {
  draggedItemId.value = null
  draggedOverZoneId.value = null
}

function handleDragEnter(zoneId: string) {
  draggedOverZoneId.value = zoneId
}

function handleDragLeave() {
  draggedOverZoneId.value = null
}

function handleDrop(event: DragEvent, zone: TargetZone) {
  event.preventDefault()
  if (!draggedItemId.value) return

  const item = items.value.find(i => i.id === draggedItemId.value)
  if (!item) return

  // 检查是否接受此类别
  if (zone.accepts.length > 0 && !zone.accepts.includes(item.category)) {
    return
  }

  // 从原位置移除
  const sourceZone = Object.keys(zoneItems.value).find(
    zid => zoneItems.value[zid]?.some(i => i.id === item.id)
  )
  if (sourceZone && zoneItems.value[sourceZone]) {
    zoneItems.value[sourceZone] = zoneItems.value[sourceZone].filter(i => i.id !== item.id)
  }

  // 添加到新位置
  if (!zoneItems.value[zone.id]) {
    zoneItems.value[zone.id] = []
  }
  zoneItems.value[zone.id]!.push(item)

  draggedItemId.value = null
  draggedOverZoneId.value = null
}

function getDroppedItems(zoneId: string): DragDropItem[] {
  return zoneItems.value[zoneId] || []
}

function isCorrect(zone: TargetZone): boolean {
  const dropped = zoneItems.value[zone.id] || []
  if (dropped.length === 0) return false
  
  // 检查所有项目是否都属于接受的类别
  return dropped.every(item => {
    if (zone.accepts.length === 0) return true
    return zone.accepts.includes(item.category)
  })
}

function removeItem(zoneId: string, index: number) {
  const zoneItemsArr = zoneItems.value[zoneId]
  if (!zoneItemsArr || !zoneItemsArr[index]) return

  const item = zoneItemsArr[index]
  zoneItemsArr.splice(index, 1)
  // 将项目放回源列表
  items.value.push(item)
}
</script>

<style scoped>
.drag-drop-container {
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 8px;
}

.source-zone {
  margin-bottom: 2rem;
}

.source-zone h4 {
  margin: 0 0 1rem;
  font-size: 1rem;
  font-weight: 600;
}

.items-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.draggable-item {
  padding: 0.75rem 1rem;
  background: #f3f4f6;
  border: 2px solid #d1d5db;
  border-radius: 6px;
  cursor: grab;
  transition: all 0.2s;
  user-select: none;
}

.draggable-item:hover {
  background: #e5e7eb;
  border-color: #3b82f6;
}

.draggable-item.dragged {
  opacity: 0.5;
}

.draggable-item:active {
  cursor: grabbing;
}

.target-zones {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.drop-zone {
  min-height: 150px;
  padding: 1rem;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  background: #f9fafb;
  transition: all 0.2s;
}

.drop-zone.over {
  border-color: #3b82f6;
  background: #eff6ff;
}

.drop-zone.correct {
  border-color: #10b981;
  background: #ecfdf5;
}

.drop-zone h5 {
  margin: 0 0 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.dropped-items {
  min-height: 100px;
}

.dropped-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.5rem;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
}

.dropped-item button {
  padding: 0.25rem 0.5rem;
  border: none;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 4px;
  cursor: pointer;
}

.success-message {
  margin-top: 1rem;
  padding: 1rem;
  text-align: center;
  background: #ecfdf5;
  border: 1px solid #10b981;
  border-radius: 6px;
  color: #059669;
  font-weight: 600;
}
</style>


