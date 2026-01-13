## 地图编辑器（LevelMapEditor.vue）模块说明

本页面用于教师可视化编辑「章节 → 模块 → 任务」的**鱼骨图关卡地图**，核心能力包括：

- 从后端加载 / 保存关卡地图配置（`levelMapsApi`、`levelsApi`）
- 使用鱼骨图布局算法将树状数据布置到画布上
- 支持拖拽主干、模块锚点、任务锚点，自动重算连线
- 集成 AI 思维导图生成（调用 `aiAssistantApi`）
- 配置任务对应的宝箱奖励（`TreasureChestConfig`）

### 关键文件

- `LevelMapEditor.vue`  
  - 页面入口，包含：
    - 顶部工具栏（新增模块/任务、宝箱配置、预览、清空、缩放、全屏等）
    - SVG 画布（主鱼骨、模块节点、任务节点、连线和锚点）
    - 节点编辑弹窗、宝箱配置弹窗、地图树形预览弹窗
  - 内部实现：
    - **布局相关**：`layoutFishbone`、`buildTreeFromNodes`、`recalcConnections`
    - **交互相关**：节点拖拽、画布平移与缩放、全屏切换、锚点拖拽
    - **后端交互**：`fetchMap`、`handleSave`、`handleSaveNode`、`handleTreasureConfigSave`

- 依赖组件与 API：
  - `components/AIMindmapGenerator.vue`：教学大纲 → AI 思维导图生成的对话框组件
  - `components/TreasureChestConfig.vue`：任务节点对应的宝箱奖励配置
  - `api/levelMaps.ts` / `api/levels.ts` / `api/chapters.ts` / `api/aiAssistant.ts`

### 数据结构约定

- `MindMapNode`
  - `id: string`：唯一标识，根节点通常为 `"root"`；
  - `type?: 'root' | 'branch' | 'sub'`：
    - `root`：章节根节点（鱼骨右侧的大圆角矩形）；
    - `branch`：模块节点，挂在主鱼骨上；
    - `sub`：任务节点，挂在模块鱼骨上；
  - `anchor?: { x: number; y: number }`：该节点在骨架线上的锚点坐标；
  - `boneParam?: number`：任务在模块鱼骨上的相对位置 \[0, 1\]，用于在拖拽时记忆比例。

- `connectionPairs: Array<{ parentId: string; childId: string }>`  
  - 描述逻辑连线（父子关系），由 `recalcConnections` 转换为实际 SVG 线段坐标。

- `spineLine: { x1: number; x2: number; y: number } | null`  
  - 主鱼骨（横向主干）的几何描述，支持左右端点拖拽调整长度。

这些字段会被整体序列化为 `map_config_json`，通过 `levelMapsApi.updateMap` 持久化到后端。

### 常见交互流程

1. **加载地图**：`onMounted` → `fetchMap()`  
   - 从 `levelMapsApi.getMap` 获取现有配置；  
   - 不存在时自动为章节创建根节点；  
   - 同步章节名称/描述，用于 AI 生成。

2. **AI 生成思维导图**：  
   - 打开 `AIMindmapGenerator`，教师粘贴教学大纲或补充说明；  
   - 前端调用 `/api/v1/ai-assistant/generate-mindmap`，得到树形 JSON；  
   - 使用 `layoutFishbone` 将树状数据转换为一组 `MindMapNode` + `connectionPairs`；
   - 调用 `recalcConnections` 计算连线和锚点。

3. **手动编辑地图**：  
   - 拖拽节点：`handleNodeMouseDown` → 实时更新 `nodes` 并重算连线；  
   - 拖拽模块锚点 / 任务锚点：`handleModuleAnchorMouseDown` / `handleAnchorMouseDown`；  
   - 新建模块/任务：`handleAddModule` / `handleAddNode`。

4. **保存地图**：  
   - `handleSave` 将 `{nodes, connections, connection_pairs, spine_line}` 序列化；  
   - 调用 `levelMapsApi.updateMap` 持久化；  
   - 后续学生端的闯关路径和宝箱展示会基于该配置渲染。

### 维护建议

- 如需调整布局算法（例如改变鱼骨角度、节点间距、左右分布规则），优先修改
  `layoutFishbone` 内部的参数与计算逻辑，尽量**保持输出数据结构不变**。
- 如需新增节点类型（例如「总结节点」），需要：
  - 扩展 `MindMapNode.type` 枚举；
  - 在模板的 `node-group` 样式中补充对应外观；
  - 在布局和重算连线逻辑中增加分支。

















