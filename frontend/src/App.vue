<template>
  <div id="app" class="app-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <VueQueryDevtools />

    <app-sidebar v-model:collapsed="sidebarCollapsed" />

    <app-notification />

    <div class="app-main">
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
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import AppSidebar from './components/shared/AppSidebar.vue'
import AppNotification from './components/shared/AppNotification.vue'
import UiOfflineBanner from './components/ui/UiOfflineBanner'
import { VueQueryDevtools } from '@tanstack/vue-query-devtools'
import { useThemeStore } from '@/stores/theme'

useThemeStore()

const SIDEBAR_COLLAPSED_KEY = 'sidebar-collapsed'
const sidebarCollapsed = ref(localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === '1')

watch(sidebarCollapsed, (collapsed) => {
  localStorage.setItem(SIDEBAR_COLLAPSED_KEY, collapsed ? '1' : '0')
})
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
  --sidebar-width: 264px;
  --sidebar-width-collapsed: 78px;
  --nav-offset: 0px;
  position: relative;
  min-height: 100vh;
  overflow-x: clip;
}

.app-shell.sidebar-collapsed {
  --sidebar-width: var(--sidebar-width-collapsed);
}

.app-main {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  margin-left: var(--sidebar-width);
  transition: margin-left 0.22s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-content {
  flex: 1;
  width: 100%;
  margin: 0;
  padding: 2rem clamp(1rem, 3vw, 2.5rem) 2rem;
  position: relative;
  z-index: 9;
}

@media (max-width: 900px) {
  .app-shell {
    --nav-offset: 60px;
  }

  .app-main {
    margin-left: 0;
    padding-top: var(--nav-offset);
    transition: none;
  }

  .page-content {
    padding: 1rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .app-main {
    transition: none;
  }
}
</style>
