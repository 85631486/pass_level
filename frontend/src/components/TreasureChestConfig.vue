<template>
  <div class="treasure-chest-config">
    <div class="config-header">
      <h4>宝箱配置</h4>
      <button class="btn-close-small" @click="$emit('close')">×</button>
    </div>
    
    <div class="config-form">
      <div class="form-group">
        <label>宝箱名称</label>
        <input v-model="config.name" type="text" class="form-input" />
      </div>
      
      <div class="form-group">
        <label>位置坐标</label>
        <div class="coord-inputs">
          <input 
            v-model.number="config.position_x" 
            type="number" 
            placeholder="X坐标" 
            class="form-input coord-input"
          />
          <input 
            v-model.number="config.position_y" 
            type="number" 
            placeholder="Y坐标" 
            class="form-input coord-input"
          />
        </div>
      </div>
      
      <div class="form-group">
        <label>奖励类型</label>
        <select v-model="rewardType" class="form-input">
          <option value="item">道具</option>
          <option value="point">积分</option>
          <option value="gift">礼品</option>
        </select>
      </div>
      
      <div class="form-group" v-if="rewardType === 'item'">
        <label>道具ID</label>
        <input v-model.number="rewardConfig.item_id" type="number" class="form-input" />
        <label>数量</label>
        <input v-model.number="rewardConfig.quantity" type="number" class="form-input" />
      </div>
      
      <div class="form-group" v-if="rewardType === 'point'">
        <label>积分数量</label>
        <input v-model.number="rewardConfig.amount" type="number" class="form-input" />
      </div>
      
      <div class="form-group" v-if="rewardType === 'gift'">
        <label>礼品ID</label>
        <input v-model.number="rewardConfig.gift_id" type="number" class="form-input" />
      </div>
      
      <div class="form-actions">
        <button class="btn-secondary" @click="$emit('close')">取消</button>
        <button class="btn-primary" @click="handleSave">保存</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  levelId?: number
  initialConfig?: {
    name?: string
    position_x?: number
    position_y?: number
    reward_config?: any
  }
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  save: [config: any]
}>()

const config = ref({
  name: props.initialConfig?.name || '宝箱',
  position_x: props.initialConfig?.position_x || 0,
  position_y: props.initialConfig?.position_y || 0
})

const rewardType = ref('point')
const rewardConfig = ref<any>({
  type: 'point',
  amount: 100
})

watch(rewardType, (newType) => {
  rewardConfig.value = { type: newType }
  if (newType === 'item') {
    rewardConfig.value.item_id = 0
    rewardConfig.value.quantity = 1
  } else if (newType === 'point') {
    rewardConfig.value.amount = 100
  } else if (newType === 'gift') {
    rewardConfig.value.gift_id = 0
  }
})

if (props.initialConfig?.reward_config) {
  rewardConfig.value = props.initialConfig.reward_config
  rewardType.value = rewardConfig.value.type || 'point'
}

const handleSave = () => {
  emit('save', {
    ...config.value,
    reward_config: rewardConfig.value
  })
}
</script>

<style scoped>
.treasure-chest-config {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 300px;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.config-header h4 {
  margin: 0;
  font-size: 1rem;
}

.btn-close-small {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
  color: #666;
}

.form-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.coord-inputs {
  display: flex;
  gap: 0.5rem;
}

.coord-input {
  flex: 1;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}
</style>

