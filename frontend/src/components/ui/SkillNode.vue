<template>
  <div class="skill-node">
    <div 
      class="skill-card"
      :class="{ 'skill-unlocked': skill.level > 0, 'skill-locked': skill.level === 0 }"
    >
      <div class="skill-header">
        <h4>{{ skill.skill_name }}</h4>
        <span class="skill-level" v-if="skill.level > 0">Lv.{{ skill.level }}</span>
      </div>
      <p v-if="skill.skill_description" class="skill-description">
        {{ skill.skill_description }}
      </p>
      <div class="skill-progress" v-if="skill.level > 0">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: (skill.experience / 100) * 100 + '%' }"
          ></div>
        </div>
        <span class="progress-text">经验: {{ skill.experience.toFixed(0) }} / 100</span>
      </div>
    </div>
    
    <div v-if="childSkills.length > 0" class="skill-children">
      <div
        v-for="child in childSkills"
        :key="child.skill_node_id"
        class="skill-child"
      >
        <SkillNode
          :skill="child"
          :all-skills="allSkills"
          :level="level + 1"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { StudentSkill } from '../../api/students'

interface Props {
  skill: StudentSkill
  allSkills: StudentSkill[]
  level: number
}

const props = defineProps<Props>()

const childSkills = computed(() => {
  return props.allSkills.filter(s => s.parent_id === props.skill.skill_node_id)
})
</script>

<style scoped>
.skill-node {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.skill-card {
  background: white;
  border: 2px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  min-width: 200px;
  margin-bottom: 1rem;
  transition: all 0.3s;
}

.skill-unlocked {
  border-color: #28a745;
  background: linear-gradient(135deg, #f8fff9 0%, #ffffff 100%);
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.2);
}

.skill-locked {
  border-color: #ddd;
  background: #f8f9fa;
  opacity: 0.6;
}

.skill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.skill-header h4 {
  margin: 0;
  font-size: 1rem;
  color: #333;
}

.skill-level {
  background: #28a745;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.skill-description {
  font-size: 0.85rem;
  color: #666;
  margin: 0.5rem 0;
  line-height: 1.4;
}

.skill-progress {
  margin-top: 0.5rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #28a745, #20c997);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: #666;
}

.skill-children {
  display: flex;
  gap: 2rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 2px dashed #ddd;
  position: relative;
}

.skill-children::before {
  content: '';
  position: absolute;
  top: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 1rem;
  background: #ddd;
}

.skill-child {
  position: relative;
}

.skill-child::before {
  content: '';
  position: absolute;
  top: -1rem;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 1rem;
  background: #ddd;
}
</style>

