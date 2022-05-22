<script setup lang="ts">
import type { Hole } from '../types'
import { formatTime } from '../utils'
import HoleComment from './HoleComment.vue'

defineProps<{
  hole: Hole
}>()
</script>

<template>
  <div class="bg-blue-200 p-2 my-2 max-w-md rounded-lg shadow-md">
    <div class="flex items-center">
      <div class="text-red-900">
        [{{ hole.pid }}]
      </div>
      <div class="flex-1" />
      <div class="ml-2">
        {{ hole.reply_count }}
      </div>
      <div class="i-carbon-chat" />
      <div class="ml-2">
        {{ hole.like_count }}
      </div>
      <div class="i-carbon-star" />
    </div>

    <div>
      <div v-if="hole.created_at && hole.deleted_at">
        <span class="text-gray-700">{{ formatTime(hole.created_at * 1000) }}</span>
        |
        <span class="text-red-800">{{ hole.deleted_at - hole.created_at }}s</span>
      </div>
    </div>

    <p v-if="hole.text || hole.image">
      {{ hole.text }}
    </p>
    <p v-else>
      <b>Content Uncaught</b>
    </p>
    <div v-if="hole.image" class="text-center">
      <a
        :href="`https://pkuhelper.pku.edu.cn/services/pkuhole/images/${hole.image}`"
        target="_blank"
        rel="noopener noreferrer"
      >Image</a>
    </div>
  </div>
  <HoleComment :pid="hole.pid" />
</template>
