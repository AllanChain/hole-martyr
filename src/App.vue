<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { format as formatDate } from 'light-date'

interface Hole {
  pid: number
  text: string
  image?: string
}

const nextScan = ref<number>(0)
const currentTime = ref<number>(new Date().getTime())
const nextScanDate = computed(() =>
  formatDate(new Date(nextScan.value), '{yyyy}-{MM}-{dd} {HH}:{mm}:{ss}'),
)
const timeToNextScan = computed(() =>
  Math.floor((nextScan.value - currentTime.value) / 1000),
)
const capturedDeletions = ref<Hole[]>([])
let evtSource: EventSource
let timerHandle: number

onMounted(() => {
  if (evtSource) { return }
  evtSource = new EventSource(`${import.meta.env.VITE_API_ROOT}stream`)
  evtSource.addEventListener('scandone', (event) => {
    nextScan.value = JSON.parse(event.data).next * 1000
  })
  evtSource.addEventListener('deletion', (event) => {
    capturedDeletions.value.unshift(JSON.parse(event.data).hole)
  })
  evtSource.addEventListener('fetcherror', (event) => {
    console.log(event.data)
  })
  window.addEventListener('beforeunload', () => {
    evtSource.close()
  })
})
onMounted(async () => {
  const resp = await fetch(`${import.meta.env.VITE_API_ROOT}next`)
  const data = await resp.json()
  nextScan.value = data.next * 1000
})
onMounted(async () => {
  const resp = await fetch(`${import.meta.env.VITE_API_ROOT}recent-deletions`)
  const data = await resp.json()
  capturedDeletions.value = data
})
onMounted(() => {
  if (timerHandle) { return }
  timerHandle = setInterval(() => {
    currentTime.value = new Date().getTime()
  }, 1000)
})
onBeforeUnmount(() => {
  console.log('Before unmount is called!')
  clearInterval(timerHandle)
  evtSource.close()
})
</script>

<template>
  <div>Next scan is scheduled at {{ nextScanDate }}</div>
  <div>{{ timeToNextScan }} s</div>
  <div>{{ capturedDeletions.length }}</div>
  <div>
    <div v-for="hole of capturedDeletions" :key="hole.pid">
      [{{ hole.pid }}]
      <p v-if="hole.text">
        {{ hole.text }}
      </p>
      <p v-else>
        <b>Content Uncaught</b>
      </p>
      <div v-if="hole.image">
        <a :href="`https://pkuhelper.pku.edu.cn/services/pkuhole/images/${hole.image}`">Image</a>
      </div>
    </div>
  </div>
</template>
