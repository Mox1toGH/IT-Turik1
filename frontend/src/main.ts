import './assets/main.css'
import 'vue-tel-input/vue-tel-input.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { VueQueryPlugin } from '@tanstack/vue-query'
import { queryClient } from './lib/queryClient'
import { connectNotificationSocket } from './lib/notificationSocket'

const app = createApp(App)

app.use(VueQueryPlugin, { queryClient: queryClient })
app.use(createPinia())
app.use(router)

app.config.errorHandler = (err, instance, info) => {
  console.error('[app] render error:', err, info, instance)
}

app.mount('#app')

connectNotificationSocket(queryClient)
