<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import type { Hole } from './types'
import HoleCard from './components/HoleCard.vue'
import NextScan from './components/NextScan.vue'
import ControlPanel from './components/ControlPanel.vue'
import ToastContainer from './components/ToastContainer.vue'
import { addToast } from './stores/toasts'
import LogContainer from './components/LogContainer.vue'
import { addLog } from './stores/logs'
import { formatTime } from './utils'
import { hasPermission } from './stores/notification'

const nextScanTime = ref<number>(0)

const capturedDeletions = ref<Hole[]>([])
let evtSource: EventSource

onMounted(() => {
  if (evtSource) { return }
  evtSource = new EventSource(`${import.meta.env.VITE_API_ROOT}stream`)
  evtSource.addEventListener('scanstart', () => {
    nextScanTime.value = new Date().getTime()
    addLog('Scan started')
  })
  evtSource.addEventListener('scandone', (event) => {
    nextScanTime.value = JSON.parse(event.data).next * 1000
    addLog(`Scan done. Next scan scheduled at ${formatTime(nextScanTime.value)}`)
  })
  evtSource.addEventListener('deletion', (event) => {
    const hole = JSON.parse(event.data).hole
    capturedDeletions.value.unshift(hole)
    addLog(`Deletion captured: #${hole.pid}`)
    if (hasPermission) {
      const notification = new Notification(`#${hole.pid} deleted`, {
        body: hole.text,
        icon: 'https://pkuhelper.pku.edu.cn/hole/static/favicon/256.png',
      })
      setTimeout(() => notification.close(), 3000)
    }
  })
  evtSource.addEventListener('fetcherror', (event) => {
    console.log(event.data)
    addToast({
      message: event.data.slice(0, 50),
      timeout: 3000,
      type: 'error',
    })
    addLog(`Fetch Error: \n${event.data}`)
  })
  evtSource.addEventListener('close', (event) => {
    console.log('close', event.data)
    addLog('Connection closed')
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
  <div class="flex">
    <div class="flex-1" />
    <div class="w-100">
      <NextScan :time="nextScanTime" />
      <ControlPanel />
      <div>
        <HoleCard v-for="hole of capturedDeletions" :key="hole.pid" :hole="hole" />
      </div>
    </div>
    <div class="flex-1" />
    <LogContainer />
    <div class="flex-1" />
  </div>
  <ToastContainer />
</template>
