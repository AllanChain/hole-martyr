<script lang="ts" setup>
import { onMounted, reactive } from 'vue'

const currentSettings = reactive({})
const changingSettings = reactive({})

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
  const settings = await resp.json()
  Object.assign(currentSettings, settings)
  Object.assign(changingSettings, settings)
}
const updateSettings = async () => {
  const resp = await fetch(`${import.meta.env.VITE_API_ROOT}settings`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(changingSettings),
  })
  const settings = await resp.json()
  Object.assign(currentSettings, settings)
  Object.assign(changingSettings, settings)
}
const resetChangingSettings = () => {
  Object.assign(changingSettings, currentSettings)
}

onMounted(fetchCurrentSettings)
</script>

<template>
  <details>
    <summary>Control Panel</summary>
    <div v-for="(_, key) of changingSettings" :key="key">
      <label>
        {{ key }}
        <input
          v-model="changingSettings[key]"
          type="number"
        >
      </label>
    </div>
    <button @click="resetChangingSettings">
      Reset
    </button>
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
