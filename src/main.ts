import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')

const evtSource = new EventSource('/api/stream')
evtSource.onmessage = (e) => {
  console.log(e)
}
evtSource.addEventListener('scandone', (event) => {
  console.log('scandone', event.data)
})
evtSource.addEventListener('end', () => {
  console.log('Handling end....')
  evtSource.close()
})
window.addEventListener('beforeunload', () => {
  evtSource.close()
})
