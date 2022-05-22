<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import type { HoleComment } from '../types'

const props = defineProps<{ pid: number }>()

const comments = ref<HoleComment[]>([])

onMounted(async () => {
  const resp = await fetch(`${import.meta.env.VITE_API_ROOT}hole/${props.pid}/comments`)
  comments.value = await resp.json()
})
</script>

<template>
  <div
    v-if="comments.length"
    class="max-w-md ml-20 xs:ml-5 max-h-50 overflow-y-auto p-2 border-1 border-dashed border-gray rounded-md"
  >
    <div
      v-for="comment in comments"
      :key="comment.cid"
      class="bg-amber-200 my-1 rounded-md p-2"
    >
      {{ comment.text }}
    </div>
  </div>
</template>
