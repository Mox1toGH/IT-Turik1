<template>
  <div id="app" class="app-shell">
    <div class="bg-orb orb-a"></div>
    <div class="bg-orb orb-b"></div>
    <VueQueryDevtools />

    <app-navbar />

    <AppNotifications />

    <main class="page-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import AppNavbar from './components/shared/AppNavbar.vue'
import { VueQueryDevtools } from '@tanstack/vue-query-devtools'
import AppNotifications from './components/shared/AppNotifications.vue'

const applyTheme = () => {
  const html = document.documentElement
  const currentTheme = localStorage.getItem('theme') ?? 'light'

  if (currentTheme === 'dark') {
    html.classList.add('dark')
  } else {
    html.classList.remove('dark')
  }
}

applyTheme()
</script>

<style scoped>
.app-shell {
  --nav-offset: 76px;
  position: relative;
  min-height: 100vh;
  overflow-x: hidden;
  padding-top: var(--nav-offset);
}

.bg-orb {
  position: fixed;
  border-radius: 999px;
  filter: blur(40px);
  z-index: 1;
  pointer-events: none;
}

.orb-a {
  width: 320px;
  height: 320px;
  left: -90px;
  top: 80px;
  background: rgba(20, 184, 166, 0.18);
}

.orb-b {
  width: 260px;
  height: 260px;
  right: -70px;
  top: 220px;
  background: rgba(249, 115, 22, 0.18);
}

.page-content {
  width: min(1100px, 100% - 2rem);
  margin: 1.6rem auto 2.4rem;
  position: relative;
  z-index: 9;
}

@media (max-width: 680px) {
  .nav-container {
    align-items: flex-start;
    flex-direction: column;
  }

  .nav-links {
    width: 100%;
    justify-content: flex-start;
  }

  .page-content {
    width: min(1100px, 100% - 1rem);
    margin-top: 1rem;
  }

  .app-notice {
    top: 0.75rem;
    left: 0.75rem;
    right: 0.75rem;
    width: auto;
  }
}
</style>
