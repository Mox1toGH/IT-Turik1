<template>
  <div id="app" class="app-shell">
    <VueQueryDevtools />

    <app-navbar />

    <app-notification />

    <main class="page-content">
      <ui-offline-banner />
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <div :key="$route.path">
            <component :is="Component" />
          </div>
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import AppNavbar from './components/shared/AppNavbar.vue'
import AppNotification from './components/shared/AppNotification.vue'
import UiOfflineBanner from './components/ui/UiOfflineBanner'
import { VueQueryDevtools } from '@tanstack/vue-query-devtools'
import { useThemeStore } from '@/stores/theme'

useThemeStore()
</script>

<style scoped>
.page-enter-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}

.page-leave-active {
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.app-shell {
  --nav-offset: 76px;
  position: relative;
  min-height: 100vh;
  overflow-x: clip;
  padding-top: var(--nav-offset);
}

.page-content {
  width: 100%;
  margin: 2rem 0 0;
  padding: 0 clamp(1rem, 3vw, 2.5rem) 2rem;
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
    padding: 0 1rem;
    margin-top: 1rem;
  }
}
</style>
