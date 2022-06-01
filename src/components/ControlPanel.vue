<script lang="ts" setup>
import { onMounted, reactive } from 'vue'

const currentSettings = reactive({})

const deleteAllData = async () => {
  if (confirm('Are you sure you want to delete all data?')) {
    await fetch(`${import.meta.env.VITE_API_ROOT}delete-all`, {
      method: 'POST',
    })
    location.reload()
  }
}

const fetchCurrentSettings = async () => {
  const resp = await fetch(`${import.meta.env.VITE_API_ROOT}settings`)
  Object.assign(currentSettings, await resp.json())
}
const updateSettings = async () => {
  await fetch(`${import.meta.env.VITE_API_ROOT}settings`, {
    method: 'PATCH',
    body: JSON.stringify(currentSettings),
  })
}

onMounted(fetchCurrentSettings)
</script>

<template>
  <details>
    <summary>Control Panel</summary>
    <div v-for="(_, key) of currentSettings" :key="key">
      <label>
        {{ key }}
        <input
          v-model="currentSettings[key]"
          type="number"
          @change="console.log"
        >
      </label>
    </div>
    <button @click="updateSettings">
      Update Settings
    </button>
    <details>
      <summary>Dangerous</summary>
      <button @click="deleteAllData">
        Delete all data
      </button>
    </details>
  </details>
</template>
