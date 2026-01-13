组件目录说明（自动重构记录）

组织原则：
- 按功能模块划分子目录：`editor/`, `canvas/`, `panels/`, `toolbar/`, `ai/`, `ui/`, `player/`。
- 组件应被放置到其所属功能目录内；页面只引用这些模块化路径。

当前目录结构（重要子目录）：
- ai/: AI 相关弹窗与生成器（AIMindmapGenerator.vue）
- canvas/: 画布渲染与可视化组件（CanvasEditor, DrawingCanvas, StepComponentRenderer 等）
- editor/: 编辑器顶层容器（CanvasEditor.vue）
- panels/: 所有侧边栏 / 配置面板（EnhancedTaskConfigPanel.vue, PhaseStepConfigPanel.vue, TeachingGuideAssistant.vue, EditorGuidance.vue, 等）
- toolbar/: 侧边工具栏（RightToolsBar.vue）
- ui/: 小型可复用 UI 组件（MarkdownEditor.vue, EnhancedProgressBar.vue, InteractiveCodeEditor.vue, SkillNode/SkillTree 等）
- player/: 播放/预览相关组件（LevelInteractivePlayer.vue）

迁移记录（本次重构要点）：
- 已移动：
  - `AIMindmapGenerator.vue` -> `ai/`
  - `AIGeneratePanel.vue` -> `panels/`
  - `EnhancedProgressBar.vue`, `InteractiveCodeEditor.vue`, `MarkdownEditor.vue`, `SkillNode.vue`, `SkillTree.vue` -> `ui/`
  - 教学辅助与预览面板 -> `panels/`（TeachingGuideAssistant, TeachingGuidePreview, EditorGuidance, PhaseStepConfigPanel）
  - 交互组件（DragDropSorter, InteractiveVideo, DrawingCanvas, StepComponentRenderer）集中在 `canvas/`
  - 播放器移动到 `player/LevelInteractivePlayer.vue`

- 已删除（原位置的冗余副本）：
  - 根目录下的重复组件已移除以避免模块冲突（例如旧版 `InteractiveVideo.vue`、`DragDropSorter.vue`、`LevelInteractivePlayer.vue` 等）。

开发者指引：
- 新增组件请放到相应模块目录，导入使用相对路径从模块目录加载（例如 `../ui/MarkdownEditor.vue` 或 `./canvas/StepComponentRenderer.vue`）。
- 在进行跨目录移动后，务必运行 linter/build 并全量搜索旧路径以修正残余引用。
- 若添加/删除文件，请同时更新此 README（或运行重构脚本生成最新映射）。

如需我现在生成更详尽的组件映射（CSV/JSON）或将 README 转为项目 docs 页面，我可以继续执行。


