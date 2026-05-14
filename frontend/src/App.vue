<template>
  <div id="app" class="app-shell">
    <div class="bg-orb orb-a"></div>
    <div class="bg-orb orb-b"></div>
    <VueQueryDevtools />

    <app-navbar />

    <Transition name="global-notice" mode="out-in">
      <div
        v-if="notification"
        :key="notification.id"
        :class="['notice', 'app-notice', notification.type, `type-${notification.type}`]"
        role="status"
        aria-live="polite"
      >
        <span>{{ notification.message }}</span>
        <ui-button
          class="close-notice-btn"
          :variant="notification.type === 'success' ? 'default' : 'danger'"
          size="sm"
          type="button"
          @click="hideNotification()"
          ><CrossIcon
        /></ui-button>
      </div>
    </Transition>

    <main class="page-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useNotification } from '@/composables/useNotification'
import AppNavbar from './components/shared/AppNavbar.vue'
import UiButton from './components/ui/UiButton.vue'
import { VueQueryDevtools } from '@tanstack/vue-query-devtools'
import CrossIcon from './icons/CrossIcon.vue'

const { notification, hideNotification } = useNotification()

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

.app-notice {
  position: fixed;
  top: 1rem;
  right: 1rem;
  margin: 0;
  width: min(92vw, 420px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  z-index: 2000;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.24);
  backdrop-filter: blur(20px);
}

.close-notice-btn {
  background: transparent;
  border: none;
}

.type-info {
  color: #0f3a58;
  background: #ecfeff;
  border-color: #7dd3fc;
}

.type-warning {
  color: #92400e;
  background: #fffbeb;
  border-color: #fcd34d;
}

.global-notice-enter-active,
.global-notice-leave-active {
  transition:
    opacity 220ms ease,
    transform 220ms ease;
}

.global-notice-enter-from,
.global-notice-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.global-notice-enter-to,
.global-notice-leave-from {
  opacity: 1;
  transform: translateY(0);
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
