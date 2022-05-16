import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')

const evtSource = new EventSource('http://127.0.0.1:3000/api/stream')
evtSource.onmessage = (e) => {
  console.log(e.data)
}
evtSource.addEventListener('update', (event) => {
  // Logic to handle status updates
  console.log(event.data)
})
evtSource.addEventListener('end', () => {
  console.log('Handling end....')
  evtSource.close()
})
window.addEventListener('beforeunload', () => {
  if (!evtSource.CLOSED) {
    evtSource.close()
  }
})
