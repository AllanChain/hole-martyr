import { ref } from 'vue'
import { formatDate } from '../utils'

export interface Log {
  timeStr: string
  message: string
  type: 'info' | 'error'
}

export const logs = ref<Log[]>([])

export const addLog = (message: string, type: 'info' | 'error' = 'info') => {
  logs.value.unshift({
    message,
    type,
    timeStr: formatDate(new Date()),
  })
}
