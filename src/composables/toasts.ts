import { ref } from 'vue'

export interface Toast {
  message: string
  timeout: number
  type: 'success' | 'error' | 'info'
  id: string
}

export const toasts = ref<Toast[]>([])

export const addToast = (toast: Omit<Toast, 'id'>) => {
  const id = Math.random().toString()
  toasts.value.push({ ...toast, id })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, toast.timeout)
}
