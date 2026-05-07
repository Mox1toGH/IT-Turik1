<template>
  <nav class="main-nav">
    <div class="nav-container">
      <div style="display: flex; justify-content: center; align-items: center; gap: 10px">
        <router-link to="/" class="brand">TournamentOS</router-link>
        <switch-theme-button />
      </div>

      <div class="nav-links">
        <div class="nav-links desktop">
          <template v-if="!user">
            <router-link to="/login" :class="navItemClass('login')">Login</router-link>
            <router-link to="/register" style="text-decoration: none">
              <ui-button :class="navItemClass('register', true)">Register</ui-button>
            </router-link>
          </template>

          <template v-else>
            <router-link to="/" :class="navItemClass('home')">Home</router-link>
            <router-link to="/teams" :class="navItemClass('teams')">Teams</router-link>
            <router-link to="/tournaments" :class="navItemClass('tournaments')"
              >Tournaments</router-link
            >
            <router-link to="/profile" :class="navItemClass('profile')">Profile</router-link>

            <router-link v-if="isAdmin" to="/admin/role-codes" :class="navItemClass('admin')"
              >Admin</router-link
            >

            <notification-dropdown />

            <ui-button @click="logout" size="sm" variant="danger" class="logout-btn"
              >Logout</ui-button
            >
          </template>
        </div>

        <div
          class="burger-menu"
          @click="mobileMenuOpen = !mobileMenuOpen"
          aria-label="Toggle navigation menu"
        >
          Menu
          <button class="burger-menu-icon" :class="{ active: mobileMenuOpen }">
            <span></span>
            <span></span>
          </button>
        </div>
      </div>

      <transition name="mobile-menu-fade">
        <div v-if="mobileMenuOpen" class="mobile-menu">
          <template v-if="!user">
            <router-link
              to="/login"
              :class="navItemClass('login')"
              @click="mobileMenuOpen = false"
              class="mobile-nav-item"
              >Login</router-link
            >
            <router-link
              to="/register"
              :class="navItemClass('register', true)"
              @click="mobileMenuOpen = false"
              class="mobile-nav-item"
              >Register</router-link
            >
          </template>

          <template v-else>
            <router-link
              to="/"
              :class="navItemClass('home')"
              @click="mobileMenuOpen = false"
              class="mobile-nav-item"
              >Home</router-link
            >
            <router-link
              to="/teams"
              :class="navItemClass('teams')"
              @click="mobileMenuOpen = false"
              class="mobile-nav-item"
              >Teams</router-link
            >
            <router-link
              to="/tournaments"
              :class="navItemClass('tournaments')"
              @click="mobileMenuOpen = false"
              class="mobile-nav-item"
              >Tournaments</router-link
            >
            <router-link
              to="/profile"
              :class="navItemClass('profile')"
              @click="mobileMenuOpen = false"
              class="mobile-nav-item"
              >Profile</router-link
            >
            <router-link
              v-if="isAdmin"
              to="/admin/role-codes"
              :class="navItemClass('admin')"
              @click="mobileMenuOpen = false"
              class="mobile-nav-item"
              >Admin</router-link
            >
            <ui-button
              @click="handleMobileLogout"
              size="sm"
              variant="danger"
              class="mobile-logout-btn"
              >Logout</ui-button
            >
          </template>
        </div>
      </transition>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UiButton from '../ui/UiButton.vue'
import { useUserStore } from '@/stores/user'
import { useProfile } from '@/api/queries/accounts'
import SwitchThemeButton from './SwitchThemeButton.vue'
import NotificationDropdown from '@/features/profile/components/notifications/NotificationDropdown.vue'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const mobileMenuOpen = ref(false)

const { data: user } = useProfile()

const isAdmin = computed(() => user.value?.role === 'admin')

type Section = 'home' | 'teams' | 'tournaments' | 'profile' | 'admin' | 'login' | 'register'

const navItemClass = (section: Section, cta = false) => ({
  'nav-item': true,
  'nav-cta': cta,
  active: isSectionActive(section),
})

const logout = () => {
  store.logout()
  router.push('/login')
}

const handleMobileLogout = () => {
  mobileMenuOpen.value = false
  logout()
}

const isSectionActive = (section: Section) => {
  const path = route.path

  if (section === 'home') return path === '/'
  if (section === 'teams') return path === '/teams' || path.startsWith('/teams/')
  if (section === 'profile')
    return path === '/profile' || path.startsWith('/profile/') || path === '/complete-profile'
  if (section === 'admin') return path === '/admin/role-codes'

  return false
}
</script>

<style scoped>
.main-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  backdrop-filter: blur(10px);
  background: color-mix(in srgb, var(--background) 80%, transparent);
  border-bottom: 1px solid color-mix(in srgb, var(--border) 40%, transparent);
}

.brand {
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--foreground);
}

.nav-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0.9rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.nav-item {
  color: var(--foreground);
  font-weight: 700;
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn {
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
}

.nav-item:hover {
  background: var(--secondary);
}

.nav-item.active {
  background: var(--secondary);
  color: var(--secondary-foreground);
}

.nav-cta {
  color: var(--primary-foreground);
  background: linear-gradient(120deg, var(--brand-700), var(--brand-500));
}

.nav-cta:hover {
  background: linear-gradient(120deg, var(--brand-600), var(--brand-500));
}

.nav-cta.active {
  color: var(--primary-foreground);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.45);
}

.burger-menu {
  min-height: 35px;
  color: var(--ink-700);
  font-weight: 700;
  display: none;
  align-items: center;
  gap: 10px;
}

.burger-menu-icon {
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 28px;
  height: 22px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  gap: 5px;
}

.burger-menu-icon span {
  width: 100%;
  height: 3px;
  background: var(--foreground);
  border-radius: 5px;
  transition: all 0.15s ease;
}

.burger-menu-icon.active span:nth-child(1) {
  transform: rotate(45deg) translate(2px, 3px);
}

.burger-menu-icon.active span:nth-child(2) {
  transform: rotate(-45deg) translate(2px, -3px);
}

.mobile-menu {
  position: fixed;
  top: 59.8px;
  left: 0;
  width: 100vw;
  height: calc(100vh - 48.8px);
  display: none;
  flex-direction: column;
  gap: 5px;
  padding: 1rem;
  border-top: 1px solid var(--line-soft);
  background: var(--background);
}

.mobile-menu-fade-enter-from,
.mobile-menu-fade-leave-to {
  transition: opacity 0.25s ease;
  opacity: 0;
}

.mobile-nav-item {
  color: var(--ink-700);
  font-weight: 700;
  padding: 0.75rem 1rem;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: block;
  text-align: left;
}

.mobile-nav-item:hover {
  background: var(--secondary);
}

.mobile-nav-item.active {
  background: var(--secondary);
}

.mobile-nav-item.nav-cta {
  color: white;
  background: linear-gradient(120deg, var(--brand-700), var(--brand-500));
}

.mobile-nav-item.nav-cta:hover {
  background: linear-gradient(120deg, var(--brand-600), var(--brand-500));
}

.mobile-logout-btn {
  width: 100%;
  margin-top: 0.5rem;
  border-radius: 999px;
}

@media (max-width: 817px) {
  .nav-links.desktop {
    display: none;
  }

  .burger-menu {
    display: flex;
  }

  .mobile-menu {
    display: flex;
  }

  .nav-container {
    padding: 0.75rem 1rem;
  }

  .brand {
    font-size: 1rem;
  }
}
</style>
