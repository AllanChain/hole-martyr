<script lang="ts" setup >
import { logs } from '../stores/logs'
</script>

<template>
  <div class="max-w-md w-100 h-screen px-4 bg-gray-50 overflow-y-auto">
    <h2 class="text-center">
      Logs
    </h2>
    <p
      v-for="(log, i) in logs"
      :key="i"
      class="text-sm my-2"
    >
      <span
        class="mr-1"
        :class="{
          'text-red-800': log.type === 'error',
          'text-bluegray-700': log.type === 'info',
        }"
      >{{ log.timeStr }}</span>
      <span class="text-gray-900">{{ log.message }}</span>
    </p>
  </div>
</template>
