<template>
  <div class="advanced-style-editor">
    <div class="style-section">
      <h4>字体样式</h4>
      <div class="form-group">
        <label>字体</label>
        <select v-model="localStyle.fontFamily" @change="emitUpdate">
          <option value="">默认</option>
          <option value="Arial">Arial</option>
          <option value="Helvetica">Helvetica</option>
          <option value="Times New Roman">Times New Roman</option>
          <option value="Courier New">Courier New</option>
          <option value="Verdana">Verdana</option>
          <option value="Georgia">Georgia</option>
          <option value="Palatino">Palatino</option>
          <option value="Garamond">Garamond</option>
          <option value="Comic Sans MS">Comic Sans MS</option>
          <option value="Trebuchet MS">Trebuchet MS</option>
          <option value="Impact">Impact</option>
        </select>
      </div>
      <div class="form-group">
        <label>字号</label>
        <input
          v-model.number="localStyle.fontSize"
          type="number"
          min="8"
          max="200"
          placeholder="如：16"
          @input="emitUpdate"
        />
      </div>
      <div class="form-group">
        <label>字重</label>
        <select v-model="localStyle.fontWeight" @change="emitUpdate">
          <option value="">默认</option>
          <option value="100">100 - 细</option>
          <option value="200">200 - 超细</option>
          <option value="300">300 - 轻</option>
          <option value="400">400 - 正常</option>
          <option value="500">500 - 中等</option>
          <option value="600">600 - 半粗</option>
          <option value="700">700 - 粗</option>
          <option value="800">800 - 超粗</option>
          <option value="900">900 - 最粗</option>
        </select>
      </div>
      <div class="form-group">
        <label>字体样式</label>
        <select v-model="localStyle.fontStyle" @change="emitUpdate">
          <option value="normal">正常</option>
          <option value="italic">斜体</option>
        </select>
      </div>
      <div class="form-group">
        <label>文字颜色</label>
        <div class="color-input-group">
          <input
            v-model="localStyle.color"
            type="color"
            @change="emitUpdate"
          />
          <input
            v-model="localStyle.color"
            type="text"
            placeholder="#000000"
            @input="emitUpdate"
          />
        </div>
      </div>
      <div class="form-group">
        <label>文本对齐</label>
        <div class="align-buttons">
          <button
            v-for="align in textAlignOptions"
            :key="align.value"
            :class="{ active: localStyle.textAlign === align.value }"
            @click="setTextAlign(align.value)"
          >
            {{ align.icon }}
          </button>
        </div>
      </div>
    </div>

    <div class="style-section">
      <h4>背景样式</h4>
      <div class="form-group">
        <label>背景颜色</label>
        <div class="color-input-group">
          <input
            v-model="localStyle.backgroundColor"
            type="color"
            @change="emitUpdate"
          />
          <input
            v-model="localStyle.backgroundColor"
            type="text"
            placeholder="#ffffff"
            @input="emitUpdate"
          />
        </div>
      </div>
      <div class="form-group">
        <label>背景图片</label>
        <input
          v-model="localStyle.backgroundImage"
          type="text"
          placeholder="输入图片URL"
          @input="emitUpdate"
        />
      </div>
    </div>

    <div class="style-section">
      <h4>边框样式</h4>
      <div class="form-group">
        <label>边框宽度</label>
        <input
          v-model.number="localStyle.borderWidth"
          type="number"
          min="0"
          max="20"
          placeholder="0"
          @input="emitUpdate"
        />
      </div>
      <div class="form-group">
        <label>边框样式</label>
        <select v-model="localStyle.borderStyle" @change="emitUpdate">
          <option value="none">无</option>
          <option value="solid">实线</option>
          <option value="dashed">虚线</option>
          <option value="dotted">点线</option>
        </select>
      </div>
      <div class="form-group">
        <label>边框颜色</label>
        <div class="color-input-group">
          <input
            v-model="localStyle.borderColor"
            type="color"
            @change="emitUpdate"
          />
          <input
            v-model="localStyle.borderColor"
            type="text"
            placeholder="#000000"
            @input="emitUpdate"
          />
        </div>
      </div>
      <div class="form-group">
        <label>圆角</label>
        <input
          v-model.number="localStyle.borderRadius"
          type="number"
          min="0"
          max="50"
          placeholder="0"
          @input="emitUpdate"
        />
      </div>
    </div>

    <div class="style-section">
      <h4>阴影样式</h4>
      <div class="form-group">
        <label>阴影</label>
        <input
          v-model="localStyle.boxShadow"
          type="text"
          placeholder="如：0 2px 4px rgba(0,0,0,0.1)"
          @input="emitUpdate"
        />
        <div class="shadow-presets">
          <button
            v-for="preset in shadowPresets"
            :key="preset.label"
            @click="applyShadowPreset(preset.value)"
          >
            {{ preset.label }}
          </button>
        </div>
      </div>
    </div>

    <div class="style-section">
      <h4>间距</h4>
      <div class="form-group">
        <label>内边距</label>
        <input
          v-model="localStyle.padding"
          type="text"
          placeholder="如：10px 或 10px 20px"
          @input="emitUpdate"
        />
      </div>
      <div class="form-group">
        <label>外边距</label>
        <input
          v-model="localStyle.margin"
          type="text"
          placeholder="如：10px 或 10px 20px"
          @input="emitUpdate"
        />
      </div>
    </div>

    <div class="style-section">
      <h4>其他</h4>
      <div class="form-group">
        <label>透明度</label>
        <input
          v-model.number="localStyle.opacity"
          type="number"
          min="0"
          max="1"
          step="0.1"
          placeholder="1"
          @input="emitUpdate"
        />
      </div>
      <div class="form-group">
        <label>层级 (z-index)</label>
        <input
          v-model.number="localStyle.zIndex"
          type="number"
          placeholder="1"
          @input="emitUpdate"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { ComponentStyle } from '../../types/coursePlayer'

interface Props {
  style?: ComponentStyle
}

interface Emits {
  (e: 'update:style', style: ComponentStyle): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const localStyle = ref<ComponentStyle>({ ...(props.style || {}) })

const textAlignOptions: Array<{ value: 'left' | 'center' | 'right' | 'justify', icon: string }> = [
  { value: 'left', icon: '⬅️' },
  { value: 'center', icon: '⬆️' },
  { value: 'right', icon: '➡️' },
  { value: 'justify', icon: '↔️' },
]

const shadowPresets = [
  { label: '无阴影', value: 'none' },
  { label: '小阴影', value: '0 1px 2px rgba(0,0,0,0.1)' },
  { label: '中阴影', value: '0 2px 4px rgba(0,0,0,0.1)' },
  { label: '大阴影', value: '0 4px 8px rgba(0,0,0,0.15)' },
  { label: '特大阴影', value: '0 8px 16px rgba(0,0,0,0.2)' },
]

watch(() => props.style, (newStyle) => {
  localStyle.value = { ...(newStyle || {}) }
}, { deep: true })

function emitUpdate() {
  emit('update:style', { ...localStyle.value })
}

function setTextAlign(align: 'left' | 'center' | 'right' | 'justify') {
  localStyle.value.textAlign = align
  emitUpdate()
}

function applyShadowPreset(value: string) {
  localStyle.value.boxShadow = value
  emitUpdate()
}
</script>

<style scoped>
.advanced-style-editor {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1rem;
}

.style-section {
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 1rem;
}

.style-section:last-child {
  border-bottom: none;
}

.style-section h4 {
  margin: 0 0 0.75rem 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.form-group label {
  font-size: 0.75rem;
  color: #6b7280;
}

.form-group input,
.form-group select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.875rem;
}

.color-input-group {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.color-input-group input[type="color"] {
  width: 50px;
  height: 40px;
  padding: 0;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
}

.color-input-group input[type="text"] {
  flex: 1;
}

.align-buttons {
  display: flex;
  gap: 0.25rem;
}

.align-buttons button {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: #ffffff;
  cursor: pointer;
  font-size: 1.25rem;
}

.align-buttons button:hover {
  background: #f3f4f6;
}

.align-buttons button.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: #ffffff;
}

.shadow-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.shadow-presets button {
  padding: 0.25rem 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: #ffffff;
  cursor: pointer;
  font-size: 0.75rem;
}

.shadow-presets button:hover {
  background: #f3f4f6;
}
</style>

