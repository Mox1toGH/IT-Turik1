<template>
  <div
    id="app"
    class="app-shell"
    :class="{ 'sidebar-collapsed': sidebarCollapsed, 'archive-mode': $route.meta.fullscreen }"
  >
    <VueQueryDevtools v-if="!$route.meta.fullscreen" />

    <app-sidebar v-if="!$route.meta.fullscreen" v-model:collapsed="sidebarCollapsed" />

    <app-notification v-if="!$route.meta.fullscreen" />

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
        <footer v-if="!$route.meta.fullscreen" class="app-footer">
          <span class="app-footer-label">TOURNAMENTOS</span>
          <router-link class="app-footer-link" to="/team">
            <span>MEET THE PEOPLE BEHIND THE PROJECT</span>
            <span class="app-footer-arrow" aria-hidden="true">-></span>
          </router-link>
        </footer>
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

.app-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-top: 2.25rem;
  padding: 1rem 1.15rem;
  border: 1px solid color-mix(in srgb, var(--primary) 38%, var(--border));
  border-radius: 0.85rem;
  background: linear-gradient(
    115deg,
    color-mix(in srgb, var(--primary) 11%, var(--card)),
    var(--card)
  );
  color: var(--muted-foreground);
  font:
    700 0.72rem/1.4 ui-monospace,
    monospace;
  letter-spacing: 0.12em;
  box-shadow: 0 8px 24px color-mix(in srgb, var(--foreground) 7%, transparent);
}

.app-footer-label {
  color: var(--muted-foreground);
}
.app-footer-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.8rem 1rem;
  border: 1px solid color-mix(in srgb, var(--primary) 70%, transparent);
  border-radius: 0.6rem;
  background: var(--primary);
  color: var(--primary-foreground);
  font-size: 0.78rem;
  line-height: 1.2;
  text-decoration: none;
  transition:
    transform 0.18s ease,
    filter 0.18s ease,
    box-shadow 0.18s ease;
}
.app-footer-link:hover {
  color: var(--primary-foreground);
  filter: brightness(1.08);
  transform: translateY(-2px);
  box-shadow: 0 5px 16px color-mix(in srgb, var(--primary) 28%, transparent);
}
.app-footer-link:focus-visible {
  outline: 3px solid color-mix(in srgb, var(--primary) 55%, white);
  outline-offset: 3px;
}
.app-footer-arrow {
  font-size: 1.2em;
}

.archive-mode {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  overflow-x: clip;
  overflow-y: visible;
}
.archive-mode .app-main,
.archive-mode .page-content {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  overflow: visible;
}
.archive-mode .page-content {
  z-index: 1;
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

@media (max-width: 600px) {
  .app-footer {
    align-items: flex-start;
    flex-direction: column;
  }
  .app-footer-link {
    width: 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .app-main,
  .app-footer-link {
    transition: none;
  }
}
</style>
