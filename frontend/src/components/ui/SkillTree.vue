<template>
  <div class="skill-tree">
    <div v-if="skills.length === 0" class="empty-skills">
      <p>暂无技能数据</p>
    </div>
    <div v-else class="tree-container">
      <div
        v-for="skill in rootSkills"
        :key="skill.skill_node_id"
        class="skill-branch"
      >
        <SkillNode
          :skill="skill"
          :all-skills="skills"
          :level="0"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { StudentSkill } from '../../api/students'
import SkillNode from './SkillNode.vue'

interface Props {
  skills: StudentSkill[]
}

const props = defineProps<Props>()

const rootSkills = computed(() => {
  return props.skills.filter(skill => !skill.parent_id)
})
</script>

<style scoped>
.skill-tree {
  padding: 1rem;
}

.empty-skills {
  text-align: center;
  padding: 2rem;
  color: #999;
}

.tree-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.skill-branch {
  display: flex;
  flex-direction: column;
}
</style>

