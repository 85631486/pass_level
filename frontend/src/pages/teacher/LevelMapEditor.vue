<template>
  <div class="level-map-editor" :class="{ fullscreen: isFullscreen }">
    <div class="page-header">
      <div class="header-left">
        <button class="btn-back" @click="handleBack">← 返回</button>
        <h2>地图编辑器</h2>
        <div class="header-actions">
          <button class="btn-primary" @click="showAIGenerator = true" :disabled="aiGenerating">
            <span>🤖</span>
            <span>{{ aiGenerating ? '生成中...' : 'AI生成思维导图' }}</span>
          </button>
          <button class="btn-primary" @click="handleSave" :disabled="saving">
            <span>💾</span>
            <span>{{ saving ? '保存中...' : '保存地图' }}</span>
          </button>
          <button class="btn-primary" @click="handleOpenLevelDesign">
            <span>🎯</span>
            <span>关卡设计</span>
          </button>
        </div>
      </div>
    </div>
    
    <div class="map-editor-content">
      <!-- 顶部工具条：左侧为编辑操作，中央为视图控制，右侧为显示信息 -->
      <div class="canvas-toolbar">
        <div class="canvas-toolbar-left">
          <button class="btn-tool primary" @click="handleAddModule">
            + 添加模块
          </button>
          <button class="btn-tool primary" @click="handleAddNode">
            + 添加节点
          </button>
          <button class="btn-tool" @click="handleOpenTreasureConfig">
            宝箱配置
          </button>
          <!-- 隐藏关卡编辑和地图预览按钮，双击节点即可编辑 -->
          <button class="btn-tool" @click="handleOpenLevelEditor" style="display: none;">
            关卡编辑
          </button>
          <button class="btn-tool" @click="handlePreviewMapTree" style="display: none;">
            地图预览
          </button>
          <button class="btn-tool" @click="handleClear">
            清空
          </button>
        </div>
        <div class="canvas-toolbar-center">
          <button class="canvas-btn" @click="zoomOut" title="缩小">
            -
          </button>
          <button class="canvas-btn" @click="zoomIn" title="放大">
            +
          </button>
          <button class="canvas-btn" @click="handleRelayout" title="重新布局（鱼骨图）">
            重新布局
          </button>
          <button class="canvas-btn" @click="fitToContent" title="适配内容">
            适配内容
          </button>
          <button class="canvas-btn" @click="resetView" title="重置视图">
            重置视图
          </button>
        </div>
        <div class="canvas-toolbar-right">
          <!-- 显示当前缩放比例 -->
          <span class="zoom-indicator">{{ Math.round(zoomScale * 100) }}%</span>
          <button class="canvas-btn fullscreen-btn" @click="toggleFullscreen">
            {{ isFullscreen ? '退出全屏' : '画布全屏' }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="mindmap-container">
        <div class="mindmap-canvas" ref="canvasRef">
          <svg
            :width="canvasWidth"
            :height="canvasHeight"
            class="mindmap-svg"
            :viewBox="`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`"
            preserveAspectRatio="xMidYMid meet"
            @mousedown="handleCanvasMouseDown"
            @wheel.prevent="handleCanvasWheel"
          >
            <g v-if="spineLine" class="spine-line">
              <line
                :x1="spineLine.x1"
                :y1="spineLine.y"
                :x2="spineLine.x2"
                :y2="spineLine.y"
                stroke="#94a3b8"
                stroke-width="6"
                stroke-linecap="round"
              />
              <!-- 主鱼骨左右端点，可拖拽调整长度 -->
              <circle
                :cx="spineLine.x1"
                :cy="spineLine.y"
                r="5"
                fill="#ffffff"
                stroke="#64748b"
                stroke-width="2"
                @mousedown.stop="handleSpineEndMouseDown('left', $event)"
              />
              <circle
                :cx="spineLine.x2"
                :cy="spineLine.y"
                r="5"
                fill="#ffffff"
                stroke="#64748b"
                stroke-width="2"
                @mousedown.stop="handleSpineEndMouseDown('right', $event)"
              />
            </g>
            <!-- 模块锚点（主干与大骨交点） -->
            <g class="module-anchor-points">
              <circle
                v-for="m in moduleAnchorPoints"
                :key="m.nodeId"
                :cx="m.x"
                :cy="m.y"
                r="5"
                fill="#ffffff"
                stroke="#64748b"
                stroke-width="2"
                @mousedown.stop="handleModuleAnchorMouseDown(m.nodeId, $event)"
              />
            </g>
            <!-- 任务连接点圆点 -->
            <g class="anchor-points">
              <circle
                v-for="p in anchorPoints"
                :key="p.nodeId"
                :cx="p.x"
                :cy="p.y"
                r="4"
                fill="#ffffff"
                stroke="#94a3b8"
                stroke-width="2"
                @mousedown.stop="handleAnchorMouseDown(p.nodeId)"
              />
            </g>
            <!-- 连线 -->
            <g class="connections">
              <line
                v-for="conn in connections"
                :key="conn.parentId + '-' + conn.childId"
                :x1="conn.x1"
                :y1="conn.y1"
                :x2="conn.x2"
                :y2="conn.y2"
                :class="['connection-line', selectedConnectionId === `${conn.parentId}-${conn.childId}` ? 'selected' : '']"
                @mousedown.stop="handleConnectionMouseDown(conn, $event)"
              />
            </g>
            <!-- 节点 -->
            <g class="nodes">
              <g
                v-for="node in nodes"
                :key="node.id"
                :transform="`translate(${node.x}, ${node.y})`"
                :class="['node-group', node.type, selectedNodeId === node.id ? 'selected' : '']"
                @mousedown.stop="handleNodeMouseDown(node, $event)"
                @dblclick="editingNode = { ...node }"
              >
                <rect
                  :width="node.width"
                  :height="node.height"
                  :rx="node.type === 'root' ? node.height / 2 : 12"
                  :fill="node.color || '#fff'"
                  :stroke="node.color || '#4c1d95'"
                  stroke-width="2"
                  class="node-rect"
                />
                <g v-if="node.badge" class="node-badge">
                  <circle cx="20" cy="20" r="16" />
                  <text x="20" y="23" text-anchor="middle">{{ node.badge }}</text>
                </g>
                <text
                  :x="node.width / 2"
                  :y="node.height / 2"
                  text-anchor="middle"
                  dominant-baseline="middle"
                  class="node-text"
                >
                  {{ node.name }}
                </text>
                <circle
                  :cx="node.width - 10"
                  :cy="10"
                  r="8"
                  fill="#dc3545"
                  class="node-delete"
                  @click.stop="handleDeleteNode(node.id)"
                />
                <text
                  :x="node.width - 10"
                  :y="14"
                  text-anchor="middle"
                  dominant-baseline="middle"
                  fill="white"
                  font-size="10"
                  class="delete-icon"
                  @click.stop="handleDeleteNode(node.id)"
                >×</text>
              </g>
            </g>
          </svg>
        </div>
      </div>
    </div>

    <!-- 底部状态栏 -->
    <div v-if="statusMessage" class="status-bar" :class="statusType">
      <span class="status-icon">
        <span v-if="statusType === 'success'">✓</span>
        <span v-else-if="statusType === 'error'">✕</span>
        <span v-else-if="statusType === 'warning'">⚠</span>
        <span v-else>ℹ</span>
      </span>
      <span class="status-text">{{ statusMessage }}</span>
      <button class="status-close" @click="clearStatus">×</button>
    </div>

    <!-- AI生成思维导图对话框 -->
    <AIMindmapGenerator
      v-if="showAIGenerator"
      :chapter-name="chapterName"
      :chapter-description="chapterDescription"
      @close="showAIGenerator = false"
      @generated="handleAIGenerated"
    />

    <!-- 节点编辑对话框 -->
    <div v-if="editingNode" class="modal-overlay" @click.self="editingNode = null">
      <div class="modal-content">
        <div class="modal-header">
          <h3>编辑关卡节点</h3>
          <button class="btn-close" @click="editingNode = null">×</button>
        </div>
        <div class="form">
          <div class="form-group">
            <label>关卡名称</label>
            <input v-model="editingNode.name" type="text" class="form-input" />
          </div>
          <div class="form-group">
            <label>关卡描述</label>
            <textarea v-model="editingNode.description" rows="3" class="form-textarea"></textarea>
          </div>
          <div class="form-actions">
            <button class="btn-secondary" @click="editingNode = null">取消</button>
            <button class="btn-primary" @click="handleSaveNode">保存</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 宝箱配置对话框 -->
    <div
      v-if="showTreasureConfig && treasureTargetNode"
      class="modal-overlay"
      @click.self="closeTreasureConfig"
    >
      <div class="modal-content small-modal">
        <TreasureChestConfig
          :level-id="treasureTargetNode.levelId"
          :initial-config="getTreasureInitialConfig(treasureTargetNode)"
          @close="closeTreasureConfig"
          @save="handleTreasureConfigSave"
        />
      </div>
    </div>

    <!-- 地图预览（关卡树） -->
    <div
      v-if="showPreviewTree"
      class="modal-overlay"
      @click.self="showPreviewTree = false"
    >
      <div class="modal-content preview-modal">
        <div class="modal-header">
          <h3>地图预览（关卡树）</h3>
          <button class="btn-close" @click="showPreviewTree = false">×</button>
        </div>
        <div class="preview-body">
          <div
            v-for="(line, idx) in previewLines"
            :key="idx"
            class="tree-line"
          >
            {{ line }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 章节关卡地图编辑器（鱼骨图思维导图）
 *
 * 主要职责：
 * - 从后端加载 / 保存章节的关卡地图配置
 * - 将树状关卡结构以鱼骨图形式渲染到 SVG 画布
 * - 支持节点拖拽、主干和模块锚点拖拽、任务锚点拖拽等交互
 * - 集成 AI 思维导图生成能力，辅助教师快速生成关卡树
 * - 支持配置任务对应的宝箱奖励
 *
 * 注意：本文件仍然集中定义了大部分编辑逻辑，为了「轻量拆分」，
 * 仅通过清晰的分段注释和函数分组来提升可读性，避免大规模重构。
 */

import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { levelMapsApi } from '../../api/levelMaps'
import { levelsApi } from '../../api/levels'
import { aiAssistantApi } from '../../api/aiAssistant'
import { chaptersApi } from '../../api/chapters'
import AIMindmapGenerator from '../../components/ai/AIMindmapGenerator.vue'
import TreasureChestConfig from '../../components/TreasureChestConfig.vue'

const route = useRoute()
const router = useRouter()
const chapterId = parseInt(route.params.id as string)

const canvasRef = ref<HTMLElement | null>(null)
const canvasWidth = ref(1200)
const canvasHeight = ref(800)
const viewBox = ref({ x: 0, y: 0, width: 1600, height: 900 })
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })
const viewBoxStart = ref({ x: 0, y: 0 })
const zoomScale = ref(1) // 相对于初始视图的缩放比例
const isFullscreen = ref(false)
const spineLine = ref<{ x1: number; x2: number; y: number } | null>(null)
// 任务锚点（大骨上的小圆点）
const anchorPoints = ref<Array<{ x: number; y: number; nodeId: string }>>([])
// 模块锚点（主干与大骨交点的小圆点）
const moduleAnchorPoints = ref<Array<{ x: number; y: number; nodeId: string }>>([])
const loading = ref(false)
const saving = ref(false)
const error = ref<string | null>(null)
const aiGenerating = ref(false)

interface MindMapNode {
  id: string
  name: string
  description?: string
  x: number
  y: number
  width: number
  height: number
  levelId?: number
  type?: 'root' | 'branch' | 'sub'
  color?: string
  badge?: string
  anchor?: {
    x: number
    y: number
  }
  // 任务节点在对应大骨线上的相对位置（0~1）
  boneParam?: number
}

const nodes = ref<MindMapNode[]>([])
const connectionPairs = ref<Array<{ parentId: string; childId: string }>>([])
const connections = ref<Array<{ x1: number; y1: number; x2: number; y2: number; parentId: string; childId: string }>>([])
const editingNode = ref<MindMapNode | null>(null)
const draggingNode = ref<MindMapNode | null>(null)
const dragOffset = ref({ x: 0, y: 0 })
const showAIGenerator = ref(false)
const chapterName = ref('')
const chapterDescription = ref('')
const pendingTaskNodeId = ref<string | null>(null)
const selectedConnectionId = ref<string | null>(null)
const selectedNodeId = ref<string | null>(null)

const showTreasureConfig = ref(false)
const treasureTargetNode = ref<MindMapNode | null>(null)
const showPreviewTree = ref(false)
const previewLines = ref<string[]>([])

// 状态栏相关
const statusMessage = ref<string>('')
const statusType = ref<'success' | 'error' | 'warning' | 'info'>('info')
let statusTimer: number | null = null

/**
 * 设置状态栏消息
 */
const setStatus = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info', duration: number = 5000) => {
  statusMessage.value = message
  statusType.value = type
  
  // 清除之前的定时器
  if (statusTimer) {
    clearTimeout(statusTimer)
  }
  
  // 设置自动清除
  if (duration > 0) {
    statusTimer = window.setTimeout(() => {
      clearStatus()
    }, duration)
  }
}

/**
 * 清除状态栏消息
 */
const clearStatus = () => {
  statusMessage.value = ''
  if (statusTimer) {
    clearTimeout(statusTimer)
    statusTimer = null
  }
}

/**
 * 根据节点与逻辑连接关系，重新计算：
 * - SVG 连线的几何坐标（connections）
 * - 模块锚点（moduleAnchorPoints）
 * - 任务锚点（anchorPoints）
 *
 * 说明：
 * - connectionPairs 仅保存 parentId / childId；
 * - 本函数会读取当前 nodes 的坐标和尺寸，计算线段起止点；
 * - 对于模块 / 任务，锚点会自动「粘附」在大骨线上，保证布局合理。
 */
const recalcConnections = () => {
  const newConnections: Array<{ x1: number; y1: number; x2: number; y2: number; parentId: string; childId: string }> = []
  const newAnchorPoints: Array<{ x: number; y: number; nodeId: string }> = []
  const newModuleAnchorPoints: Array<{ x: number; y: number; nodeId: string }> = []

  if (connectionPairs.value.length === 0 && nodes.value.length > 1) {
    const rootNode = nodes.value[0]
    if (rootNode) {
      connectionPairs.value = nodes.value.slice(1).map(node => ({
        parentId: rootNode.id,
        childId: node.id
      }))
    }
  }

  connectionPairs.value.forEach(pair => {
    const parentNode = nodes.value.find(node => node.id === pair.parentId)
    const childNode = nodes.value.find(node => node.id === pair.childId)
    if (parentNode && childNode) {
      let startX = parentNode.x + parentNode.width / 2
      let startY = parentNode.y + parentNode.height / 2
      let targetX = childNode.x + childNode.width / 2
      let targetY = childNode.y + childNode.height / 2

      // 主干 -> 模块：从主干上的锚点出发，并记录模块锚点
      if (parentNode.type === 'root' && childNode.type === 'branch' && childNode.anchor) {
        startX = childNode.anchor.x
        startY = childNode.anchor.y
        newModuleAnchorPoints.push({
          x: childNode.anchor.x,
          y: childNode.anchor.y,
          nodeId: childNode.id,
        })
      }

      // 模块 -> 任务：锚点必须始终粘在大骨线上，并记录任务锚点
      if (parentNode.type === 'branch' && childNode.type === 'sub') {
        const anchor = parentNode.anchor
        if (anchor) {
          const ax = anchor.x
          const ay = anchor.y
          const bx = parentNode.x + parentNode.width / 2
          const by = parentNode.y + parentNode.height / 2
          const t = childNode.boneParam ?? 0.5
          const anchorX = ax + (bx - ax) * t
          const anchorY = ay + (by - ay) * t

          childNode.anchor = { x: anchorX, y: anchorY }
          startX = anchorX
          startY = anchorY
          newAnchorPoints.push({ x: anchorX, y: anchorY, nodeId: childNode.id })
        }
      }

      // 线段终点先指向节点中心，再缩短到矩形边缘，使线条停在节点边上
      const vx = targetX - startX
      const vy = targetY - startY
      const len = Math.sqrt(vx * vx + vy * vy) || 1

      let offset =
        childNode.type === 'branch'
          ? Math.min(childNode.width, childNode.height) * 0.55
          : Math.min(childNode.width, childNode.height) * 0.45
      if (offset > len * 0.8) {
        offset = len * 0.8
      }

      const endX = targetX - (vx / len) * offset
      const endY = targetY - (vy / len) * offset

      newConnections.push({
        x1: startX,
        y1: startY,
        x2: endX,
        y2: endY,
        parentId: parentNode.id,
        childId: childNode.id
      })
    }
  })

  connections.value = newConnections
  anchorPoints.value = newAnchorPoints
  moduleAnchorPoints.value = newModuleAnchorPoints
}

/**
 * 从后端加载当前章节的地图配置（关卡鱼骨图）
 *
 * 逻辑：
 * 1. 调用 levelMapsApi.getMap 获取 map_config_json；
 * 2. 如有配置则反序列化为 nodes / connection_pairs / spine_line；
 * 3. 如没有任何节点，则以章节信息自动创建根节点；
 * 4. 同时加载章节名称/描述，供 AI 生成使用；
 * 5. 最后根据 connectionPairs 计算连线和锚点。
 */
const fetchMap = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await levelMapsApi.getMap(chapterId)
    const mapConfig = response.data.map_config_json
    
    if (mapConfig) {
      try {
        const config = JSON.parse(mapConfig)
        if (config.nodes) {
          nodes.value = config.nodes
        }
        if (config.connection_pairs && config.connection_pairs.length > 0) {
          connectionPairs.value = config.connection_pairs
        } else {
          connectionPairs.value = []
        }
        recalcConnections()
        if (config.spine_line) {
          spineLine.value = config.spine_line
        } else {
          spineLine.value = null
        }
      } catch (e) {
        console.error('Failed to parse map config:', e)
      }
    }
    
    // 如果没有节点，创建根节点
    if (nodes.value.length === 0) {
      const chapterResponse = await chaptersApi.getChapter(chapterId)
      const chapter = chapterResponse.data
      chapterName.value = chapter.name
      chapterDescription.value = chapter.description || ''
      nodes.value = [{
        id: 'root',
        name: chapter.name,
        description: chapter.description,
        x: canvasWidth.value / 2 - 100,
        y: 50,
        width: 200,
        height: 60
      }]
    } else {
      // 加载章节信息用于AI生成
      try {
        const chapterResponse = await chaptersApi.getChapter(chapterId)
        const chapter = chapterResponse.data
        chapterName.value = chapter.name
        chapterDescription.value = chapter.description || ''
      } catch (e) {
        console.error('Failed to load chapter info:', e)
      }
    }
    
    if (connectionPairs.value.length > 0) {
      recalcConnections()
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || '加载地图失败'
    console.error('Error fetching map:', err)
  } finally {
    loading.value = false
  }
}

const handleBack = () => {
  router.push('/teacher/chapters')
}

/**
 * 处理点击「关卡设计」按钮，跳转到选中关卡的编辑页面
 * 
 * 逻辑：
 * - 检查是否有选中的关卡节点（sub 类型）
 * - 如果节点还没有保存为关卡（没有 levelId），自动创建关卡
 * - 然后跳转到该关卡的编辑页面
 */
const handleOpenLevelDesign = async () => {
  const selectedNode = nodes.value.find(
    (n) => n.id === selectedNodeId.value && n.type === 'sub'
  )
  
  if (!selectedNode) {
    setStatus('请先在地图上点击选择一个关卡节点（任务节点），再点击「关卡设计」', 'warning')
    return
  }
  
  // 如果节点还没有保存为关卡，先自动创建关卡
  if (!selectedNode.levelId) {
    try {
      setStatus('正在创建关卡...', 'info', 0)
      const response = await levelsApi.createLevel(chapterId, {
        chapter_id: chapterId,
        name: selectedNode.name || '新关卡',
        description: selectedNode.description,
        order: nodes.value.indexOf(selectedNode)
      })
      // 将创建的关卡ID保存到节点中
      selectedNode.levelId = response.data.id
      // 保存地图配置，以便下次加载时保留 levelId
      await handleSave()
    } catch (err: any) {
      setStatus(err.response?.data?.detail || '创建关卡失败，请稍后重试', 'error')
      console.error('Error creating level:', err)
      return
    }
  }
  
  // 跳转到选中关卡的编辑页面
  router.push({ name: 'teacher-level-editor', params: { levelId: selectedNode.levelId! } })
}

/**
 * 基于当前 nodes / connectionPairs 构建一棵「逻辑树」
 *
 * 用途：
 * - 提供给 layoutFishbone 重新布局；
 * - 提供给地图预览（ASCII 树）。
 *
 * 返回值：
 * - 与 AI 返回结构兼容的 { id, name/topic, description, children } 形式。
 */
const buildTreeFromNodes = (): any | null => {
  if (nodes.value.length === 0) return null

  const nodeDataMap = new Map<string, any>()
  nodes.value.forEach((n) => {
    nodeDataMap.set(n.id, {
      id: n.id,
      topic: n.name,
      name: n.name,
      description: n.description,
      children: [] as any[],
    })
  })

  // 找到根节点（优先 type === 'root'）
  const rootNode =
    nodes.value.find((n) => n.type === 'root') ?? nodes.value[0]
  if (!rootNode) return null

  // 根据 connectionPairs 构建树
  connectionPairs.value.forEach((pair) => {
    const parent = nodeDataMap.get(pair.parentId)
    const child = nodeDataMap.get(pair.childId)
    if (parent && child) {
      parent.children.push(child)
    }
  })

  return nodeDataMap.get(rootNode.id)
}

/**
 * 重新根据树状数据进行鱼骨布局
 *
 * 调用场景：
 * - 手动点击「重新布局」按钮；
 * - 新增模块后希望整体自适应排布；
 * - AI 生成思维导图后进行初次布局。
 */
const handleRelayout = () => {
  const rootData = buildTreeFromNodes()
  if (!rootData) return

  const layoutResult = layoutFishbone(rootData, spineLine.value ?? undefined)
  nodes.value = layoutResult.nodes
  connectionPairs.value = layoutResult.connectionPairs
  recalcConnections()
}

/**
 * 根据当前关卡结构生成文本树预览（ASCII 风格）
 *
 * 示例：
 * 根节点
 *   ├─ 模块1
 *   │  └─ 任务1
 *   └─ 模块2
 */
const handlePreviewMapTree = () => {
  const rootData = buildTreeFromNodes()
  if (!rootData) {
    setStatus('当前地图为空，无法预览', 'warning')
    return
  }

  const lines: string[] = []

  const walk = (node: any, prefix: string) => {
    const label = node.name || node.topic || '未命名关卡'
    lines.push(`${prefix}${label}`)
    if (node.children && node.children.length) {
      node.children.forEach((child: any, index: number) => {
        const childPrefix = prefix + (index === node.children.length - 1 ? '  └─ ' : '  ├─ ')
        walk(child, childPrefix)
      })
    }
  }

  walk(rootData, '')
  previewLines.value = lines
  showPreviewTree.value = true
}

/**
 * 处理 AI 思维导图生成结果
 *
 * 来源：
 * - AIMindmapGenerator 组件通过事件 `@generated` 传入 data；
 * - data 可能已经包含解析后的 result，也可能只包含 syllabus 等参数。
 *
 * 逻辑：
 * - 若 data.result 存在，直接使用布局算法生成鱼骨图；
 * - 否则调用传统 aiAssistantApi.generateMindmap 接口；
 * - 最终更新 nodes / connectionPairs 并刷新连线。
 */
const handleAIGenerated = async (data: { syllabus: string; chapter_name?: string; description?: string; result?: any }) => {
  if (aiGenerating.value) return
  
  aiGenerating.value = true
  try {
    // 如果已经有结果（从流式输出中获取），直接使用
    let mindmapData = data.result
    
    // 如果没有结果，使用传统API调用（向后兼容）
    if (!mindmapData) {
      const response = await aiAssistantApi.generateMindmap({
        syllabus: data.syllabus,
        chapter_name: data.chapter_name || chapterName.value,
        description: data.description || chapterDescription.value
      })
      mindmapData = response.data
    }
    
    if (mindmapData && mindmapData.root) {
      const layoutResult = layoutFishbone(mindmapData.root)
      nodes.value = layoutResult.nodes
      connectionPairs.value = layoutResult.connectionPairs
      recalcConnections()
      showAIGenerator.value = false
    } else {
      setStatus('AI生成失败：未返回有效数据，请检查教学大纲格式或稍后重试', 'error')
    }
  } catch (err: any) {
    setStatus(err.response?.data?.detail || 'AI生成失败，请检查网络连接或稍后重试', 'error')
    console.error('Error generating mindmap:', err)
  } finally {
    aiGenerating.value = false
  }
}

/**
 * 鱼骨图布局算法
 *
 * 输入：
 * - rootData：树状关卡结构（根节点 + children）
 * - existingSpineLine：可选的已有主干参数（用于保持用户拖拽后的主干形状）
 *
 * 输出：
 * - nodes：包含几何信息的 MindMapNode 列表
 * - connectionPairs：父子关系（用于后续计算连线与锚点）
 *
 * 约定：
 * - 根节点渲染在主干右侧；
 * - 模块节点沿主干左右交替分布（上 / 下鱼骨），角度约 60 度；
 * - 任务节点沿模块鱼骨均匀分布，并统一偏移到鱼骨一侧。
 */
const layoutFishbone = (
  rootData: any,
  existingSpineLine?: { x1: number; x2: number; y: number }
): { nodes: MindMapNode[]; connectionPairs: Array<{ parentId: string; childId: string }> } => {
  const newNodes: MindMapNode[] = []
  const connectionPairsLocal: Array<{ parentId: string; childId: string }> = []
  const nodeMap = new Map<string, MindMapNode>()

  const createNode = (
    data: any,
    centerX: number,
    centerY: number,
    options: { type?: MindMapNode['type']; color?: string; badge?: string; width?: number; height?: number } = {}
  ): MindMapNode => {
    const nodeId = data.id || `node_${Date.now()}_${Math.random()}`
    const nodeName = data.topic || data.name || '未命名'
    const autoWidth = Math.max(160, Math.min(nodeName.length * 12 + 40, 260))
    const width = options.width ?? autoWidth
    const height = options.height ?? 60
    const node: MindMapNode = {
      id: nodeId,
      name: nodeName,
      description: data.description,
      x: centerX - width / 2,
      y: centerY - height / 2,
      width,
      height,
      type: options.type,
      color: options.color,
      badge: options.badge
    }
    newNodes.push(node)
    nodeMap.set(nodeId, node)
    return node
  }

  const rootName = rootData.topic || rootData.name || '未命名'
  const autoRootWidth = Math.max(160, Math.min(rootName.length * 12 + 40, 260))
  const rootWidth = Math.max(autoRootWidth, 240)
  const rootHeight = 80
  const gapBetweenSpineAndRoot = 40
  const spineY = existingSpineLine?.y ?? canvasHeight.value / 2

  let spineStartX: number
  let spineEndX: number
  let rootCenterX: number

  if (existingSpineLine) {
    spineStartX = existingSpineLine.x1
    spineEndX = existingSpineLine.x2
    const rootLeft = spineEndX + gapBetweenSpineAndRoot
    rootCenterX = rootLeft + rootWidth / 2
  } else {
    rootCenterX = canvasWidth.value - 200
    spineEndX = rootCenterX - rootWidth / 2 - gapBetweenSpineAndRoot
    const spineLength = Math.min(rootCenterX - 160, 1100)
    spineStartX = spineEndX - spineLength
  }

  const rootNode = createNode(rootData, rootCenterX, spineY, {
    type: 'root',
    color: '#ec4899',
    width: rootWidth,
    height: rootHeight
  })

  spineLine.value = {
    x1: spineStartX,
    x2: spineEndX,
    y: spineY
  }

  const branches = rootData.children || []
  const totalTopBranches = Math.ceil(branches.length / 2)
  const totalBottomBranches = Math.floor(branches.length / 2)
  const pairCount = Math.max(totalTopBranches, totalBottomBranches, 1)
  const availableLength = Math.max(spineEndX - spineStartX - 120, 200)
  const branchSpacing = Math.max(180, availableLength / pairCount)
  const baseAngle = (60 * Math.PI) / 180 // 默认 60 度斜率
  const branchColors = ['#fbbf24', '#f472b6', '#a5b4fc', '#34d399', '#fdba74', '#7dd3fc']

  branches.forEach((module: any, index: number) => {
    const direction: 'top' | 'bottom' = index % 2 === 0 ? 'top' : 'bottom'
    const pairIndex = Math.floor(index / 2)
    const dirSign = direction === 'top' ? -1 : 1

    const angle = dirSign * baseAngle
    const anchorX = spineEndX - branchSpacing * (pairIndex + 0.5)
    const anchorY = spineY

    const tasks = Array.isArray(module.children) ? module.children : []
    const minBone = 260
    const stepPerTask = 80
    const boneLength = minBone + Math.max(0, tasks.length - 1) * stepPerTask

    const dx = -Math.cos(angle)
    const dy = Math.sin(angle)
    const endX = anchorX + dx * boneLength
    const endY = anchorY + dy * boneLength

    const color = branchColors[index % branchColors.length]
    const moduleNode = createNode(module, endX, endY, {
      type: 'branch',
      color,
      badge: module.order ? String(module.order) : String(index + 1)
    })
    moduleNode.anchor = { x: anchorX, y: anchorY }

    connectionPairsLocal.push({ parentId: rootNode.id, childId: moduleNode.id })

    if (tasks.length > 0) {
      const offsetX = 120 // 所有任务节点统一在鱼骨左侧一定距离

      tasks.forEach((task: any, taskIndex: number) => {
        const t = (taskIndex + 1) / (tasks.length + 1)
        const px = anchorX + (endX - anchorX) * t
        const py = anchorY + (endY - anchorY) * t

        const cx = px - offsetX
        const cy = py

        const taskNode = createNode(task, cx, cy, { type: 'sub' })
        taskNode.anchor = { x: px, y: py }
        taskNode.boneParam = t
        connectionPairsLocal.push({ parentId: moduleNode.id, childId: taskNode.id })
      })
    }
  })

  return {
    nodes: newNodes,
    connectionPairs: connectionPairsLocal
  }
}

/**
 * 在当前地图中新增一个「任务」节点
 *
 * 交互流程：
 * - 先在主干末端附近创建一个悬空任务节点；
 * - 如果之前已经选中了某条分骨线，则立刻挂载到那条线；
 * - 否则提示用户「请点击一条分鱼骨线以连接该任务」，
 *   并将新建任务作为 pendingTaskNodeId 记录，等待后续挂载。
 */
const handleAddNode = () => {
  const newNode: MindMapNode = {
    id: `task_${Date.now()}`,
    name: '新任务',
    x: spineLine.value ? spineLine.value.x2 - 200 : 200,
    y: spineLine.value ? spineLine.value.y : 200,
    width: 150,
    height: 50,
    type: 'sub'
  }
  nodes.value.push(newNode)

  if (selectedConnectionId.value) {
    const connection = connections.value.find(
      (conn) => `${conn.parentId}-${conn.childId}` === selectedConnectionId.value
    )
    if (connection) {
      pendingTaskNodeId.value = newNode.id
      attachPendingTaskToConnection(connection)
      return
    }
  }

  pendingTaskNodeId.value = newNode.id
  alert('已创建新任务，请点击一条分鱼骨线以连接该任务。')
}

/**
 * 新增一个模块（branch 节点）
 *
 * 逻辑：
 * - 以根节点为父节点，生成一个新的 branch；
 * - 在主干中点附近初始化锚点；
 * - 更新 connectionPairs 后调用 handleRelayout，统一重新布局。
 */
const handleAddModule = () => {
  const rootNode = nodes.value.find((n) => n.type === 'root') ?? nodes.value[0]
  if (!rootNode) {
    setStatus('请先创建根节点', 'warning')
    return
  }

  const newModule: MindMapNode = {
    id: `module_${Date.now()}`,
    name: '新模块',
    x: rootNode.x - 200,
    y: rootNode.y,
    width: 160,
    height: 60,
    type: 'branch',
    color: '#c4b5fd',
    badge: `${nodes.value.filter((n) => n.type === 'branch').length + 1}`
  }
  newModule.anchor = {
    x: spineLine.value ? (spineLine.value.x2 + spineLine.value.x1) / 2 : rootNode.x,
    y: spineLine.value ? spineLine.value.y : rootNode.y + newModule.height / 2
  }

  nodes.value.push(newModule)
  connectionPairs.value.push({
    parentId: rootNode.id,
    childId: newModule.id
  })
  handleRelayout()
}

/**
 * 打开某个任务节点对应的宝箱配置弹窗
 *
 * 限制：
 * - 只有选中的节点且类型为 sub（任务）时才允许配置宝箱；
 * - 如果节点还没有绑定后端关卡（levelId 为空），会引导先保存节点。
 */
const handleOpenTreasureConfig = () => {
  const node = nodes.value.find((n) => n.id === selectedNodeId.value && n.type === 'sub')
  if (!node) {
    setStatus('请先点击选择一个任务节点，再配置宝箱', 'warning')
    return
  }

  if (!node.levelId) {
    setStatus('请先在"编辑关卡节点"中保存该节点，再配置宝箱奖励', 'warning')
    editingNode.value = { ...node }
    return
  }

  treasureTargetNode.value = node
  showTreasureConfig.value = true
}

/**
 * 从当前选中的任务节点跳转到关卡编辑页面
 *
 * 要求：
 * - 必须先选中一个类型为 sub 的任务节点；
 * - 且该节点已经在后端创建了关卡（levelId 不为空）。
 */
const handleOpenLevelEditor = () => {
  const node = nodes.value.find((n) => n.id === selectedNodeId.value && n.type === 'sub')
  if (!node) {
    setStatus('请先点击选择一个任务节点，再进入关卡编辑', 'warning')
    return
  }

  if (!node.levelId) {
    setStatus('该节点尚未保存为关卡，请先在"编辑关卡节点"中保存，再进入关卡编辑', 'warning')
    editingNode.value = { ...node }
    return
  }

  router.push({ name: 'teacher-level-editor', params: { levelId: node.levelId } })
}

const closeTreasureConfig = () => {
  showTreasureConfig.value = false
  treasureTargetNode.value = null
}

/**
 * 根据任务节点生成宝箱初始位置与名称
 */
const getTreasureInitialConfig = (node: MindMapNode) => {
  const centerX = node.x + node.width / 2
  const centerY = node.y + node.height / 2
  return {
    name: `${node.name}宝箱`,
    position_x: centerX,
    position_y: centerY,
  }
}

/**
 * 将宝箱配置提交给后端
 *
 * 注意：一个任务节点可以对应多个宝箱，此处调用 levelsApi.createTreasureChest
 * 由后端负责具体业务规则。
 */
const handleTreasureConfigSave = async (config: any) => {
  if (!treasureTargetNode.value || !treasureTargetNode.value.levelId) {
    return
  }

  try {
    const levelId = treasureTargetNode.value.levelId
    await levelsApi.createTreasureChest(levelId, {
      level_id: levelId,
      name: config.name,
      position_x: config.position_x,
      position_y: config.position_y,
      reward_config: config.reward_config,
    })
    setStatus('宝箱配置已保存', 'success')
    closeTreasureConfig()
  } catch (err: any) {
    console.error('Error saving treasure chest:', err)
    setStatus(err.response?.data?.detail || '保存宝箱配置失败', 'error')
  }
}

/**
 * 删除某个关卡节点（模块 / 任务）
 *
 * - 会同时删除以该节点为父 / 子的所有连接关系；
 * - 删除后会重新计算连接线和锚点。
 */
const handleDeleteNode = (nodeId: string) => {
  if (confirm('确定要删除这个关卡节点吗？')) {
    nodes.value = nodes.value.filter(n => n.id !== nodeId)
    connectionPairs.value = connectionPairs.value.filter(
      pair => pair.parentId !== nodeId && pair.childId !== nodeId
    )
    recalcConnections()
    setStatus('节点已删除', 'success')
  }
}

let clickTimer: number | null = null
let hasMoved = false

/**
 * 处理节点在画布中的拖拽与点击（单击 / 双击）逻辑
 *
 * 行为：
 * - 按下后监听 document 上的 mousemove / mouseup，实现平滑拖拽；
 * - 若移动距离极小，则被视为点击（支持 300ms 内双击打开编辑框）；
 * - 拖动过程中实时调用 recalcConnections() 保持连线跟随节点移动。
 */
const handleNodeMouseDown = (node: MindMapNode, event: MouseEvent) => {
  if (event.target && (event.target as HTMLElement).classList.contains('node-delete')) {
    return
  }
  
  selectedNodeId.value = node.id
  hasMoved = false
  const startX = event.clientX
  const startY = event.clientY
  
  draggingNode.value = node
  dragOffset.value = {
    x: event.clientX - node.x,
    y: event.clientY - node.y
  }
  
  const handleMouseMove = (e: MouseEvent) => {
    const deltaX = Math.abs(e.clientX - startX)
    const deltaY = Math.abs(e.clientY - startY)
    if (deltaX > 5 || deltaY > 5) {
      hasMoved = true
    }
    
    if (draggingNode.value) {
      draggingNode.value.x = e.clientX - dragOffset.value.x
      draggingNode.value.y = e.clientY - dragOffset.value.y
      recalcConnections()
    }
  }
  
  const handleMouseUp = () => {
    draggingNode.value = null
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
    
    // 如果没有移动，处理点击事件（用于双击编辑）
    if (!hasMoved) {
      if (clickTimer) {
        // 双击
        clearTimeout(clickTimer)
        clickTimer = null
        editingNode.value = { ...node }
      } else {
        // 单击，设置定时器等待可能的双击
        clickTimer = window.setTimeout(() => {
          clickTimer = null
        }, 300)
      }
    }
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

/**
 * 拖动任务锚点（任务所在的小骨与模块骨架的交点）
 *
 * 本质上是沿着模块的骨架线做一维投影，更新 taskNode.boneParam，
 * 之后通过 recalcConnections 根据比例重新计算锚点坐标。
 */
const handleAnchorMouseDown = (nodeId: string) => {
  const taskNode = nodes.value.find(n => n.id === nodeId)
  if (!taskNode) return

  const parentPair = connectionPairs.value.find(pair => pair.childId === nodeId)
  if (!parentPair) return
  const parentNode = nodes.value.find(n => n.id === parentPair.parentId)
  if (!parentNode || parentNode.type !== 'branch') return

  const anchor = parentNode.anchor
  if (!anchor) return

  const ax = anchor.x
  const ay = anchor.y
  const bx = parentNode.x + parentNode.width / 2
  const by = parentNode.y + parentNode.height / 2
  const abx = bx - ax
  const aby = by - ay
  const abLenSq = abx * abx + aby * aby || 1

  const handleMouseMove = (e: MouseEvent) => {
    // 鼠标在画布坐标系中的位置（假设viewBox与画布等比缩放）
    const rect = (canvasRef.value as HTMLElement | null)?.getBoundingClientRect()
    if (!rect) return
    const mx = (e.clientX - rect.left) * (viewBox.value.width / rect.width) + viewBox.value.x
    const my = (e.clientY - rect.top) * (viewBox.value.height / rect.height) + viewBox.value.y

    const amx = mx - ax
    const amy = my - ay
    let t = (amx * abx + amy * aby) / abLenSq
    // 限制在 0.1~0.9 区间，避免滑出骨头两端
    t = Math.max(0.1, Math.min(0.9, t))

    taskNode.boneParam = t
    recalcConnections()
  }

  const handleMouseUp = () => {
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

/**
 * 拖动模块锚点（主干与大骨交点的小圆点）
 *
 * 允许教师在主干上左右移动模块的位置，从而调整整体布局。
 */
const handleModuleAnchorMouseDown = (nodeId: string, event: MouseEvent) => {
  event.preventDefault()
  const moduleNode = nodes.value.find(n => n.id === nodeId)
  if (!moduleNode || !spineLine.value) return

  const { x1, x2, y } = spineLine.value
  const rect = (canvasRef.value as HTMLElement | null)?.getBoundingClientRect()
  if (!rect) return
  const startX = event.clientX
  const initialAnchorX = moduleNode.anchor?.x ?? x1

  const handleMouseMove = (e: MouseEvent) => {
    const dxPixel = e.clientX - startX
    const dxCanvas = dxPixel * (viewBox.value.width / rect.width)
    let clampedX = initialAnchorX + dxCanvas
    clampedX = Math.max(x1, Math.min(x2, clampedX))

    moduleNode.anchor = { x: clampedX, y }
    recalcConnections()
  }

  const handleMouseUp = () => {
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

/**
 * 将一个「待挂接任务节点」绑定到指定连接线上
 *
 * 用途：
 * - 用户先创建任务，再点击某条鱼骨线，将任务挂到该线对应的模块下。
 *
 * 实现要点：
 * - 根据连接线起止点计算投影比例 t；
 * - 将任务锚点定位在线段内部（0.1 ~ 0.9 之间）；
 * - 更新 pendingNode 的坐标与 boneParam，并补充 connectionPairs。
 */
const attachPendingTaskToConnection = (
  connection: { parentId: string; childId: string; x1: number; y1: number; x2: number; y2: number },
  event?: MouseEvent
) => {
  if (!pendingTaskNodeId.value) return

  const parentNode = nodes.value.find((n) => n.id === connection.parentId)
  const childNode = nodes.value.find((n) => n.id === connection.childId)

  const moduleNode =
    parentNode && parentNode.type === 'branch'
      ? parentNode
      : childNode && childNode.type === 'branch'
        ? childNode
        : null

  if (!moduleNode) return

  const pendingNode = nodes.value.find((n) => n.id === pendingTaskNodeId.value)
  if (!pendingNode) return

  const ax = connection.x1
  const ay = connection.y1
  const bx = connection.x2
  const by = connection.y2
  const abx = bx - ax
  const aby = by - ay
  const abLenSq = abx * abx + aby * aby || 1

  let t = 0.5
  if (event) {
    const rect = (canvasRef.value as HTMLElement | null)?.getBoundingClientRect()
    if (!rect) return
    const mx = (event.clientX - rect.left) * (viewBox.value.width / rect.width) + viewBox.value.x
    const my = (event.clientY - rect.top) * (viewBox.value.height / rect.height) + viewBox.value.y
    t = ((mx - ax) * abx + (my - ay) * aby) / abLenSq
  }
  t = Math.max(0.1, Math.min(0.9, t))

  const anchorX = ax + abx * t
  const anchorY = ay + aby * t

  pendingNode.type = 'sub'
  pendingNode.anchor = { x: anchorX, y: anchorY }
  pendingNode.boneParam = t
  pendingNode.x = anchorX - 120
  pendingNode.y = anchorY - pendingNode.height / 2

  connectionPairs.value.push({
    parentId: moduleNode.id,
    childId: pendingNode.id
  })

  pendingTaskNodeId.value = null
  recalcConnections()
}

/**
 * 点击连线：
 * - 若存在 pendingTaskNodeId，则表示用户正在为新任务选择挂接位置；
 *   此时会调用 attachPendingTaskToConnection 将任务挂载到当前连接线。
 * - 否则，如果是「主干 → 模块」的连接线，则允许通过拖动来改变模块在主干上的位置。
 */
const handleConnectionMouseDown = (
  connection: { parentId: string; childId: string; x1: number; y1: number; x2: number; y2: number },
  event: MouseEvent
) => {
  const connectionId = `${connection.parentId}-${connection.childId}`
  selectedConnectionId.value = connectionId

  if (pendingTaskNodeId.value) {
    attachPendingTaskToConnection(connection, event)
    return
  }

  const parentNode = nodes.value.find(n => n.id === connection.parentId)
  const childNode = nodes.value.find(n => n.id === connection.childId)

  if (parentNode && parentNode.type === 'root' && childNode && childNode.type === 'branch') {
    handleModuleAnchorMouseDown(childNode.id, event)
  }
}

/**
 * 拖动主鱼骨左右端点
 *
 * - 左端：受限于最左侧模块锚点和画布边界，避免骨架过长/越界；
 * - 右端：受限于根节点位置，避免主干穿过根节点。
 */
const handleSpineEndMouseDown = (side: 'left' | 'right', event: MouseEvent) => {
  if (!spineLine.value) return

  const startX = event.clientX
  const initial = { ...spineLine.value }
  const rect = (canvasRef.value as HTMLElement | null)?.getBoundingClientRect()
  if (!rect) return

  const handleMouseMove = (e: MouseEvent) => {
    const dxClient = e.clientX - startX
    const dxCanvas = dxClient * (viewBox.value.width / rect.width)

    if (!spineLine.value) return
    let { x1, x2, y } = initial

    if (side === 'left') {
      x1 = x1 + dxCanvas
      // 不要超过所有模块锚点最小值，留一点边距
      const minAnchorX = moduleAnchorPoints.value.length
        ? Math.min(...moduleAnchorPoints.value.map(m => m.x)) - 60
        : x1
      const rootMin = viewBox.value.x + 40
      x1 = Math.min(x1, x2 - 80)
      x1 = Math.min(x1, minAnchorX)
      x1 = Math.max(x1, rootMin)
    } else {
      x2 = x2 + dxCanvas
      // 不要越过根节点左侧
      const rootLimit = x2 // 初始值
      x2 = Math.max(x2, x1 + 120)
      x2 = Math.min(x2, rootLimit + 400)
    }

    spineLine.value = { x1, x2, y }
  }

  const handleMouseUp = () => {
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

/**
 * 保存当前编辑中的节点（关卡）信息到后端
 *
 * 行为：
 * - 若节点已有 levelId：调用 updateLevel 仅同步名称 / 描述；
 * - 若无 levelId：在当前章节下创建新关卡，并写回 levelId。
 */
const handleSaveNode = async () => {
  if (!editingNode.value) return
  
  const node = nodes.value.find(n => n.id === editingNode.value!.id)
  if (node) {
    node.name = editingNode.value.name
    node.description = editingNode.value.description
    
    // 如果节点有关卡ID，更新关卡；否则创建新关卡
    if (node.levelId) {
      try {
        await levelsApi.updateLevel(node.levelId, {
          name: node.name,
          description: node.description
        })
      } catch (err) {
        console.error('Error updating level:', err)
      }
    } else {
      try {
        const response = await levelsApi.createLevel(chapterId, {
          chapter_id: chapterId,
          name: node.name,
          description: node.description,
          order: nodes.value.indexOf(node)
        })
        node.levelId = response.data.id
      } catch (err) {
        console.error('Error creating level:', err)
      }
    }
  }
  
  editingNode.value = null
  recalcConnections()
}

/**
 * 清空当前地图的所有节点与连线
 *
 * 仅清空前端状态，不会立刻同步到后端，
 * 需要教师后续点击「保存地图」才会真正覆盖后端配置。
 */
const handleClear = () => {
  if (confirm('确定要清空所有节点吗？')) {
    nodes.value = []
    connections.value = []
    connectionPairs.value = []
    spineLine.value = null
    pendingTaskNodeId.value = null
    setStatus('所有节点已清空', 'success')
  }
}

/**
 * 将当前地图配置保存到后端
 *
 * 持久化内容：
 * - 首先同步所有节点到后端（创建或更新关卡）
 * - 然后保存地图配置（节点位置、连线关系、主鱼骨位置等）
 */
const handleSave = async () => {
  saving.value = true
  try {
    // 第一步：同步所有节点到后端（创建或更新关卡）
    for (const node of nodes.value) {
      // 只处理任务节点（sub 类型），根节点和模块节点不需要创建关卡
      if (node.type === 'sub') {
        if (node.levelId) {
          // 如果节点已有 levelId，更新关卡信息
          try {
            await levelsApi.updateLevel(node.levelId, {
              name: node.name,
              description: node.description
            })
          } catch (err) {
            console.error(`Error updating level ${node.levelId}:`, err)
            // 继续处理其他节点，不中断整个保存流程
          }
        } else {
          // 如果节点没有 levelId，创建新关卡
          try {
            const response = await levelsApi.createLevel(chapterId, {
              chapter_id: chapterId,
              name: node.name || '新关卡',
              description: node.description,
              order: nodes.value.indexOf(node)
            })
            // 将创建的关卡ID保存到节点中
            node.levelId = response.data.id
          } catch (err) {
            console.error(`Error creating level for node ${node.id}:`, err)
            // 继续处理其他节点，不中断整个保存流程
          }
        }
      }
    }
    
    // 第二步：保存地图配置（包含更新后的节点信息）
    const mapConfig = {
      nodes: nodes.value,
      connections: connections.value,
      connection_pairs: connectionPairs.value,
      // 保存主鱼骨的位置信息，避免刷新后消失
      spine_line: spineLine.value
    }
    
    await levelMapsApi.updateMap(chapterId, {
      map_config_json: JSON.stringify(mapConfig)
    })
    
    setStatus('地图保存成功！所有节点已同步到后端。', 'success')
  } catch (err: any) {
    setStatus(err.response?.data?.detail || '保存失败', 'error')
    console.error('Error saving map:', err)
  } finally {
    saving.value = false
  }
}

/**
 * 处理点击画布空白区域进行「拖动画布」的逻辑
 *
 * 实现：
 * - 记录鼠标和 viewBox 的起始位置；
 * - 将像素位移映射到 viewBox 坐标系，实现平移。
 */
const handleCanvasMouseDown = (event: MouseEvent) => {
  // 只在点击空白区域时进行平移（节点本身的 mousedown 已经 .stop 阻止冒泡）
  if (event.button !== 0) return
  selectedNodeId.value = null
  isPanning.value = true
  panStart.value = { x: event.clientX, y: event.clientY }
  viewBoxStart.value = { x: viewBox.value.x, y: viewBox.value.y }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isPanning.value) return
    const dx = e.clientX - panStart.value.x
    const dy = e.clientY - panStart.value.y

    // 将屏幕像素位移换算到 viewBox 坐标系
    const scaleX = viewBox.value.width / canvasWidth.value
    const scaleY = viewBox.value.height / canvasHeight.value
    viewBox.value.x = viewBoxStart.value.x - dx * scaleX
    viewBox.value.y = viewBoxStart.value.y - dy * scaleY
  }

  const handleMouseUp = () => {
    isPanning.value = false
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

/**
 * 处理在画布上使用滚轮缩放（按住 Ctrl 时生效）
 *
 * - 以鼠标所在位置作为缩放中心；
 * - 通过调整 viewBox 宽高与偏移实现缩放；
 * - 同步维护 zoomScale，用于在 UI 中展示缩放百分比。
 */
const handleCanvasWheel = (event: WheelEvent) => {
  // 仅在按住 Ctrl 时进行缩放，避免影响普通滚动
  if (!event.ctrlKey) return

  event.preventDefault()

  const zoomFactor = 1.1
  // 鼠标向上滚动（deltaY < 0）放大，向下滚动（deltaY > 0）缩小
  const direction = event.deltaY < 0 ? 1 / zoomFactor : zoomFactor

  // 当前鼠标在 SVG 宽高中的比例位置
  const rect = (canvasRef.value as HTMLElement | null)?.getBoundingClientRect()
  if (!rect) return

  const offsetX = event.clientX - rect.left
  const offsetY = event.clientY - rect.top

  const xRatio = offsetX / canvasWidth.value
  const yRatio = offsetY / canvasHeight.value

  const newWidth = viewBox.value.width * direction
  const newHeight = viewBox.value.height * direction

  // 以鼠标所在点为中心缩放
  const newX = viewBox.value.x + viewBox.value.width * xRatio - newWidth * xRatio
  const newY = viewBox.value.y + viewBox.value.height * yRatio - newHeight * yRatio

  viewBox.value = {
    x: newX,
    y: newY,
    width: newWidth,
    height: newHeight
  }

  zoomScale.value *= direction
}

/**
 * 以画布中心为基准缩放一小步
 *
 * 通过构造一个“假 WheelEvent”复用 handleCanvasWheel 逻辑。
 */
const zoomByDelta = (deltaY: number) => {
  const rect = (canvasRef.value as HTMLElement | null)?.getBoundingClientRect()
  if (!rect) return

  // 以画布中心为缩放参考点
  const centerX = rect.width / 2
  const centerY = rect.height / 2

  const fakeEvent = {
    ctrlKey: true,
    deltaY,
    clientX: rect.left + centerX,
    clientY: rect.top + centerY,
    preventDefault: () => {}
  } as unknown as WheelEvent

  handleCanvasWheel(fakeEvent)
}

const zoomIn = () => {
  // 与当前滚轮逻辑保持一致：正方向代表放大（viewBox 变小）
  zoomByDelta(1)
}

const zoomOut = () => {
  zoomByDelta(-1)
}

/**
 * 将视图重置为「初始画布大小」对应的 viewBox
 */
const resetView = () => {
  viewBox.value = {
    x: 0,
    y: 0,
    width: canvasWidth.value,
    height: canvasHeight.value
  }
  zoomScale.value = 1
}

/**
 * 自动将视图缩放到刚好包含所有节点（带一定边距）
 *
 * - 遍历 nodes，计算包围盒；
 * - 在包围盒基础上增加 padding；
 * - 将 viewBox 设置为该区域，并估算新的 zoomScale。
 */
const fitToContent = () => {
  if (nodes.value.length === 0) {
    resetView()
    return
  }

  let minX = Infinity
  let minY = Infinity
  let maxX = -Infinity
  let maxY = -Infinity

  nodes.value.forEach((node) => {
    minX = Math.min(minX, node.x)
    minY = Math.min(minY, node.y)
    maxX = Math.max(maxX, node.x + node.width)
    maxY = Math.max(maxY, node.y + node.height)
  })

  // 留一些边距
  const padding = 80
  minX -= padding
  minY -= padding
  maxX += padding
  maxY += padding

  const contentWidth = maxX - minX
  const contentHeight = maxY - minY

  viewBox.value = {
    x: minX,
    y: minY,
    width: contentWidth,
    height: contentHeight
  }

  // 粗略计算缩放比例（与初始画布大小相比）
  const scaleX = canvasWidth.value / contentWidth
  const scaleY = canvasHeight.value / contentHeight
  zoomScale.value = Math.min(scaleX, scaleY)
}

/**
 * 切换画布全屏 / 非全屏模式
 *
 * - 通过外层容器 class 切换实现视觉上的全屏；
 * - 切换后通过 nextTick 重新测量画布尺寸，并重置 viewBox。
 */
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value

  // 全屏切换后刷新一次视图尺寸和viewBox，避免出现黑边
  nextTick(() => {
    updateCanvasSize()
    resetView()
  })
}

const updateCanvasSize = () => {
  if (canvasRef.value) {
    const rect = canvasRef.value.getBoundingClientRect()
    canvasWidth.value = rect.width || window.innerWidth
    canvasHeight.value = rect.height || window.innerHeight - 200
  } else {
    // 获取主内容区域的宽度（减去侧边栏）
    const sidebarWidth = document.querySelector('.sidebar.collapsed') ? 70 : 260
    canvasWidth.value = window.innerWidth - sidebarWidth - 20 // 减去侧边栏和少量边距
    canvasHeight.value = window.innerHeight - 200
  }
}

onMounted(() => {
  // 根据容器大小初始化画布尺寸，使画布尽量充满视口
  updateCanvasSize()

  // 初始视图与画布尺寸保持一致
  viewBox.value = {
    x: 0,
    y: 0,
    width: canvasWidth.value,
    height: canvasHeight.value
  }
  zoomScale.value = 1

  // 监听窗口大小变化
  window.addEventListener('resize', updateCanvasSize)

  fetchMap()
})

onUnmounted(() => {
  // 清理事件监听器
  window.removeEventListener('resize', updateCanvasSize)
})
</script>

<style scoped>
.level-map-editor {
  padding: 0.75rem 0.5rem 1rem;
  margin-top: -0.5rem;
  width: 100%;
  min-height: calc(100vh - 4rem);
  display: flex;
  flex-direction: column;
  color: var(--text-primary, #333);
  box-sizing: border-box;
}

/* 当状态栏显示时，为页面内容添加顶部间距，避免被遮挡 */
.level-map-editor:has(.status-bar) .page-header {
  margin-top: 3rem;
}

.level-map-editor.fullscreen {
  position: fixed;
  inset: 0;
  padding: 1rem;
  z-index: 2000;
  background: radial-gradient(circle at top, #0f172a 0, #020617 40%, #020617 100%);
}

.level-map-editor.fullscreen .page-header {
  margin-bottom: 0.5rem;
}

.level-map-editor.fullscreen .map-editor-content {
  padding-bottom: 0;
}

/* 状态栏样式 */
.status-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    transform: translateY(-100%);
  }
  to {
    transform: translateY(0);
  }
}

.status-bar.success {
  background: #f0fdf4;
  border-bottom-color: #86efac;
  color: #166534;
}

.status-bar.error {
  background: #fef2f2;
  border-bottom-color: #fca5a5;
  color: #991b1b;
}

.status-bar.warning {
  background: #fffbeb;
  border-bottom-color: #fde047;
  color: #854d0e;
}

.status-bar.info {
  background: #eff6ff;
  border-bottom-color: #93c5fd;
  color: #1e40af;
}

.status-icon {
  font-size: 1.2rem;
  font-weight: bold;
  line-height: 1;
}

.status-text {
  flex: 1;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: inherit;
  opacity: 0.6;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s ease;
}

.status-close:hover {
  opacity: 1;
}

.page-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 0.75rem;
  padding: 0 0.5rem;
  width: 100%;
  box-sizing: border-box;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.btn-back {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0.5rem 0;
  margin-bottom: 0.5rem;
}

.btn-back:hover {
  text-decoration: underline;
}

.page-header h2 {
  margin: 0;
  font-size: 1.5rem;
  white-space: nowrap;
  color: #1f2937 !important; /* 深灰色，确保文字清晰可见 */
  font-weight: 700; /* 加粗字体 */
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.header-actions .btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff !important; /* 确保文字颜色为纯白色，清晰可见 */
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 700; /* 加粗字体，提高可读性 */
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2); /* 添加文字阴影，增强对比度 */
}

.header-actions .btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.header-actions .btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-primary,
.btn-secondary {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.map-editor-content {
  flex: 1;
  overflow: hidden;
  background: transparent;
  border-radius: 0;
  padding: 0;
  width: 100%;
  box-sizing: border-box;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
}

.error {
  color: #dc3545;
}

.mindmap-container {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.canvas-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 0.5rem 0.5rem 0.75rem;
  margin-bottom: 0.25rem;
}

.canvas-toolbar-center {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  flex: 1;
}

.canvas-toolbar-left,
.canvas-toolbar-right {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.5rem;
}

.canvas-toolbar-right {
  justify-content: flex-end;
}

.canvas-btn {
  padding: 0.35rem 0.9rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.7);
  background: white;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.12);
}

.canvas-btn:hover {
  background: #f3f4f6;
  transform: translateY(-1px);
}

.zoom-indicator {
  font-size: 0.8rem;
  color: #6b7280;
}

.fullscreen-btn {
  margin-left: 0.5rem;
}

.toolbar {
  margin-bottom: 1rem;
  display: flex;
  gap: 1rem;
}

.btn-tool {
  padding: 0.35rem 1.2rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.9rem;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  min-width: 120px;
  white-space: nowrap;
  box-shadow: 0 3px 8px rgba(15, 23, 42, 0.08);
}

.btn-tool.primary {
  border-color: #6366f1;
  color: #3730a3;
  font-weight: 600;
}

.btn-tool:hover {
  background: #f8f9fa;
}

.mindmap-canvas {
  flex: 1;
  width: 100%;
  background: white;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.25);
  border: 1px solid rgba(148, 163, 184, 0.4);
  box-sizing: border-box;
}

.mindmap-svg {
  width: 100%;
  height: 100%;
}

.spine-line line {
  stroke: #94a3b8;
}

.module-anchor-points circle {
  filter: drop-shadow(0 1px 2px rgba(15, 23, 42, 0.35));
}

.anchor-points circle {
  filter: drop-shadow(0 1px 2px rgba(15, 23, 42, 0.35));
}

.connection-line {
  stroke: #cbd5f5;
  stroke-width: 2;
  cursor: pointer;
  transition: stroke 0.2s ease, stroke-width 0.2s ease;
}

.connection-line.selected {
  stroke: #6366f1;
  stroke-width: 3;
}

.node-group {
  cursor: move;
}

.node-group.selected .node-rect {
  stroke: #6366f1;
  stroke-width: 3;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.4), 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* 为不同类型的节点设置选中时的背景色 */
.node-group.selected.sub .node-rect {
  fill: #e0e7ff !important; /* 任务节点选中时使用浅蓝色背景 */
}

.node-group.selected.branch .node-rect {
  fill: #e0e7ff !important; /* 模块节点选中时使用浅蓝色背景 */
}

.node-group.selected.root .node-rect {
  fill: linear-gradient(135deg, #c084fc, #8b5cf6) !important; /* 根节点选中时使用更深的紫色渐变 */
  stroke: #6366f1;
  stroke-width: 3;
}

.node-group.selected .node-text {
  font-weight: 700;
}

.node-group.selected.sub .node-text,
.node-group.selected.branch .node-text {
  fill: #1e1b4b !important; /* 任务和模块节点选中时文字颜色更深，确保清晰可见 */
}

.node-group.root .node-rect {
  fill: linear-gradient(135deg, #ec4899, #a855f7);
  stroke: none;
}

.node-group.root .node-text {
  font-size: 20px;
  font-weight: 600;
  fill: #fff;
}

.node-group.branch .node-rect {
  stroke: transparent;
  filter: drop-shadow(0 6px 12px rgba(15, 23, 42, 0.15));
}

.node-group.branch .node-text {
  font-weight: 600;
  fill: #0f172a;
}

.node-group.sub .node-rect {
  fill: #fff;
  stroke: #cbd5f5;
}

.node-group.sub .node-text {
  fill: #1f2937;
  font-size: 13px;
}

.node-rect {
  transition: fill 0.2s;
}

.node-group:hover .node-rect {
  fill: #f0f8ff;
}

.node-text {
  font-size: 14px;
  fill: #333;
  pointer-events: none;
  user-select: none;
}

.node-badge {
  pointer-events: none;
}

.node-badge circle {
  fill: rgba(255, 255, 255, 0.9);
  stroke: rgba(15, 23, 42, 0.2);
}

.node-badge text {
  font-size: 12px;
  font-weight: 600;
  fill: #475569;
}

.node-delete {
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.node-group:hover .node-delete {
  opacity: 1;
}

.delete-icon {
  pointer-events: none;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  color: #1f2937 !important; /* 深灰色，确保标题清晰可见 */
  font-weight: 700; /* 加粗字体 */
  font-size: 1.25rem; /* 稍微增大字体 */
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}
</style>
