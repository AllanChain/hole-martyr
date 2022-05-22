<script lang="ts" setup>
import { format as formatDate } from 'light-date'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps<{
  time: number
}>()

let timerHandle: number

const currentTime = ref<number>(new Date().getTime())
const nextScanDate = computed(() =>
  formatDate(new Date(props.time), '{yyyy}-{MM}-{dd} {HH}:{mm}:{ss}'),
)
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
