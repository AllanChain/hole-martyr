<script lang="ts" setup>
import { toasts } from '../composables/toasts'
</script>

<template>
  <div class="fixed bottom-5 left-1/2 translate-x--1/2">
    <TransitionGroup
      enter-active-class="duration-400 ease-out"
      enter-from-class="transform opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="duration-400 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="transform opacity-0"
      tag="div"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="flex items-center rounded-md p-2 min-w-50 shadow-md"
        :class="{
          'bg-blue-100': toast.type === 'info',
          'bg-green-100': toast.type === 'success',
          'bg-red-100': toast.type === 'error',
        }"
      >
        <div
          :class="{
            'i-carbon-information': toast.type === 'info',
            'i-carbon-checkmark-outline': toast.type === 'success',
            'i-carbon-misuse-outline': toast.type === 'error',
          }"
        />
        <div class="ml-1 text-gray-900">
          {{ toast.message }}
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>
