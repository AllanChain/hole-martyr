<script lang="ts" setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { formatTime } from '../utils'

const props = defineProps<{
  time: number
}>()

let timerHandle: number

const currentTime = ref<number>(new Date().getTime())
const nextScanDate = computed(() => formatTime(props.time))
const timeToNextScan = computed(() =>
  Math.floor((props.time - currentTime.value) / 1000),
)

onMounted(() => {
  if (timerHandle) { return }
  timerHandle = setInterval(() => {
    currentTime.value = new Date().getTime()
  }, 1000)
})
onBeforeUnmount(() => {
  clearInterval(timerHandle)
})
</script>

<template>
  <div>
    Next scan: {{ nextScanDate }} (
    <span v-if="timeToNextScan > 0">{{ timeToNextScan }} s</span>
    <span v-else>Scanning {{ -timeToNextScan }} s</span>
    )
  </div>
</template>
