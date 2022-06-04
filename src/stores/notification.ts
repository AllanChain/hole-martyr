import { ref } from 'vue'

export const hasPermission = ref(false)

const updatePermission = () => {
  hasPermission.value = !(
    Notification.permission === 'denied'
     || Notification.permission === 'default'
  )
}

updatePermission()

export const requestPermission = async () => {
  if (!hasPermission.value) {
    await Notification.requestPermission()
    updatePermission()
  }
}
