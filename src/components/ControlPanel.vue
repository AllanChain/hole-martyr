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
  <details class="bg-gray-100 rounded-md p-2 max-w-md">
    <summary>Control Panel</summary>
    <div class="grid grid-cols-[2fr_1fr]">
      <template v-for="(_, key) of changingSettings" :key="key">
        <label :for="changingSettings[key]">
          {{ key }}
        </label>
        <input
          :id="changingSettings[key]"
          v-model="changingSettings[key]"
          class="max-w-20"
          type="number"
        >
      </template>
    </div>
    <button
      class="btn bg-yellow-500 hover:bg-yellow-600"
      @click="resetChangingSettings"
    >
      Reset
    </button>
    <button
      class="btn bg-green-500 hover:bg-green-600"
      @click="updateSettings"
    >
      Update Settings
    </button>
    <details class="bg-red-100 p-2 my-2 rounded-sm">
      <summary>Dangerous</summary>
      <button
        class="btn bg-red-500 hover:bg-red-600 text-white"
        @click="deleteAllData"
      >
        Delete all data
      </button>
    </details>
  </details>
</template>
