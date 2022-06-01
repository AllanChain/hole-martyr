<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import type { Hole } from './types'
import HoleCard from './components/HoleCard.vue'
import NextScan from './components/NextScan.vue'
import ControlPanel from './components/ControlPanel.vue'

const nextScanTime = ref<number>(0)

const capturedDeletions = ref<Hole[]>([])
let evtSource: EventSource

onMounted(() => {
  if (evtSource) { return }
  evtSource = new EventSource(`${import.meta.env.VITE_API_ROOT}stream`)
  evtSource.addEventListener('scanstart', () => {
    nextScanTime.value = new Date().getTime()
  })
  evtSource.addEventListener('scandone', (event) => {
    nextScanTime.value = JSON.parse(event.data).next * 1000
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
  nextScanTime.value = data.next * 1000
})
onMounted(async () => {
  const resp = await fetch(`${import.meta.env.VITE_API_ROOT}recent-deletions`)
  const data = await resp.json()
  capturedDeletions.value = data
})

onBeforeUnmount(() => {
  console.log('Before unmount is called!')
  evtSource.close()
})
</script>

<template>
  <NextScan :time="nextScanTime" />
  <ControlPanel />
  <div>
    <HoleCard v-for="hole of capturedDeletions" :key="hole.pid" :hole="hole" />
  </div>
</template>
