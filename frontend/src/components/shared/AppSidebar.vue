<template>
  <!-- Mobile top bar -->
  <header class="sidebar-topbar">
    <button
      class="icon-btn"
      type="button"
      aria-label="Open navigation menu"
      aria-controls="app-sidebar"
      :aria-expanded="mobileOpen"
      @click="mobileOpen = true"
    >
      <Menu :size="20" :stroke-width="2" />
    </button>

    <router-link to="/" class="topbar-brand">
      <span class="brand-mark"><Trophy :size="16" :stroke-width="2.2" /></span>
      <span>TournamentOS</span>
    </router-link>

    <router-link v-if="user" to="/profile" class="topbar-profile" aria-label="Go to profile">
      <user-avatar
        :avatar="user.avatar"
        :username="user.username || 'User'"
        :full-name="user.full_name || ''"
        :size="30"
        :position-key="user.id ? `image-position:avatar:user:${user.id}` : ''"
      />
    </router-link>
    <router-link v-else to="/login" class="topbar-login">Login</router-link>
  </header>

  <!-- Mobile backdrop -->
  <transition name="scrim">
    <div v-if="mobileOpen" class="sidebar-scrim" @click="mobileOpen = false"></div>
  </transition>

  <!-- Sidebar / mobile drawer -->
  <aside
    id="app-sidebar"
    class="sidebar"
    :class="{ collapsed, 'mobile-open': mobileOpen }"
    :inert="!isDesktop && !mobileOpen"
    aria-label="Primary navigation"
  >
    <div class="sidebar-header">
      <router-link to="/" class="brand" :title="collapsed ? 'TournamentOS' : undefined">
        <span class="brand-mark"><Trophy :size="18" :stroke-width="2.2" /></span>
        <span class="brand-name">TournamentOS</span>
      </router-link>

      <button
        v-if="isDesktop"
        class="icon-btn collapse-toggle"
        type="button"
        :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        @click="toggleCollapsed"
      >
        <PanelLeftOpen v-if="collapsed" :size="18" />
        <PanelLeftClose v-else :size="18" />
      </button>

      <button
        v-else
        class="icon-btn drawer-close"
        type="button"
        aria-label="Close navigation menu"
        @click="mobileOpen = false"
      >
        <X :size="20" />
      </button>
    </div>

    <nav class="sidebar-nav" aria-label="Main">
      <p class="nav-group-label">{{ user ? 'Workspace' : 'Account' }}</p>

      <router-link
        v-for="item in navItems"
        :key="item.section"
        :to="item.to"
        class="nav-item"
        :class="{ active: isSectionActive(item.section), 'nav-item--cta': item.cta }"
        :aria-current="isSectionActive(item.section) ? 'page' : undefined"
        :title="isDesktop && collapsed ? item.label : undefined"
        @click="mobileOpen = false"
      >
        <component :is="item.icon" class="nav-icon" :size="18" :stroke-width="2" />
        <span class="nav-label">{{ item.label }}</span>
        <span v-if="item.section === 'notifications' && unreadTotal" class="nav-badge">
          {{ unreadTotal > 99 ? '99+' : unreadTotal }}
        </span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <div class="sidebar-actions">
        <div v-if="user" class="sidebar-notify">
          <NotificationDropdown />
        </div>
        <SwitchThemeButton class="sidebar-theme" />
      </div>

      <router-link
        v-if="user"
        to="/profile"
        class="profile-card"
        :class="{ active: isSectionActive('profile') }"
        :title="isDesktop && collapsed ? displayName : undefined"
        @click="mobileOpen = false"
      >
        <user-avatar
          :avatar="user.avatar"
          :username="user.username || 'User'"
          :full-name="user.full_name || ''"
          :size="34"
          :position-key="user.id ? `image-position:avatar:user:${user.id}` : ''"
        />
        <span class="profile-text">
          <span class="profile-name">{{ displayName }}</span>
          <span class="profile-role">{{ roleLabel }}</span>
        </span>
        <ChevronRight class="profile-chevron" :size="16" />
      </router-link>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch, type Component } from 'vue'
import { useRoute } from 'vue-router'
import {
  Bell,
  CalendarDays,
  ChevronRight,
  ClipboardCheck,
  Home,
  LogIn,
  Menu,
  Newspaper,
  PanelLeftClose,
  PanelLeftOpen,
  Shield,
  Trophy,
  UserPlus,
  Users,
  X,
} from 'lucide-vue-next'
import NotificationDropdown from '@/components/shared/NotificationDropdown.vue'
import SwitchThemeButton from '@/components/shared/SwitchThemeButton.vue'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useGetUnreadNotificationCount } from '@/api/notifications/notifications'
import { hasRole } from '@/shared/lib/permissions'

type Props = {
  collapsed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  collapsed: false,
})

const emit = defineEmits<{
  'update:collapsed': [value: boolean]
}>()

const route = useRoute()
const mobileOpen = ref(false)
const isDesktop = ref(true)
let mediaQuery: MediaQueryList | null = null

const { data: user } = useGetUserProfile()
const { data: unreadCount } = useGetUnreadNotificationCount()

const unreadTotal = computed(() => unreadCount.value?.unread_count ?? 0)
const displayName = computed(() => user.value?.full_name || user.value?.username || 'User')
const roleLabel = computed(() => {
  const role = user.value?.role
  return role ? role.charAt(0).toUpperCase() + role.slice(1) : ''
})

const isAdmin = computed(() => hasRole(user.value, 'admin'))
const isJury = computed(() => hasRole(user.value, 'jury'))

type Section =
  | 'home'
  | 'teams'
  | 'tournaments'
  | 'news'
  | 'calendar'
  | 'evaluation'
  | 'profile'
  | 'notifications'
  | 'admin'
  | 'login'
  | 'register'

interface NavItem {
  section: Section
  to: string
  label: string
  icon: Component
  cta?: boolean
}

const navItems = computed<NavItem[]>(() => {
  if (!user.value) {
    return [
      { section: 'login', to: '/login', label: 'Login', icon: LogIn },
      { section: 'register', to: '/register', label: 'Register', icon: UserPlus, cta: true },
    ]
  }

  return [
    { section: 'home', to: '/', label: 'Home', icon: Home },
    { section: 'teams', to: '/teams', label: 'Teams', icon: Users },
    { section: 'tournaments', to: '/tournaments', label: 'Tournaments', icon: Trophy },
    { section: 'news', to: '/news', label: 'News', icon: Newspaper },
    { section: 'calendar', to: '/calendar', label: 'Calendar', icon: CalendarDays },
    ...(isJury.value
      ? [
          {
            section: 'evaluation',
            to: '/evaluation',
            label: 'Evaluations',
            icon: ClipboardCheck,
          } as NavItem,
        ]
      : []),
    ...(isAdmin.value
      ? [{ section: 'admin', to: '/admin', label: 'Admin', icon: Shield } as NavItem]
      : []),
    { section: 'notifications', to: '/profile/notifications', label: 'Notifications', icon: Bell },
  ]
})

const routeResolved = computed(() => route.matched.length > 0)

const isSectionActive = (section: Section) => {
  if (!routeResolved.value) return false
  const path = route.path

  if (section === 'home') return path === '/'
  if (section === 'teams') return path === '/teams' || path.startsWith('/teams/')
  if (section === 'news') return path === '/news' || path.startsWith('/news/')
  if (section === 'tournaments') return path === '/tournaments' || path.startsWith('/tournaments/')
  if (section === 'calendar') return path === '/calendar'
  if (section === 'evaluation') return path === '/evaluation' || path.startsWith('/evaluation/')
  if (section === 'notifications') return path.startsWith('/profile/notifications')
  if (section === 'profile')
    return (
      path === '/profile' || path === '/complete-profile' || path === '/profile/tournaments-history'
    )
  if (section === 'admin') return path === '/admin' || path.startsWith('/admin/')

  return false
}

const toggleCollapsed = () => {
  emit('update:collapsed', !props.collapsed)
}

const closeOnEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape') mobileOpen.value = false
}

const handleMediaChange = (event: MediaQueryListEvent) => {
  isDesktop.value = event.matches
}

watch(
  () => route.fullPath,
  () => {
    mobileOpen.value = false
  },
)

watch(
  [mobileOpen, isDesktop],
  ([open, desktop]) => {
    document.body.style.overflow = open && !desktop ? 'hidden' : ''
  },
  { immediate: true },
)

watch(isDesktop, (desktop) => {
  if (desktop) mobileOpen.value = false
})

onMounted(() => {
  mediaQuery = window.matchMedia('(min-width: 901px)')
  isDesktop.value = mediaQuery.matches
  mediaQuery.addEventListener('change', handleMediaChange)
  document.addEventListener('keydown', closeOnEscape)
})

onUnmounted(() => {
  mediaQuery?.removeEventListener('change', handleMediaChange)
  document.removeEventListener('keydown', closeOnEscape)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.brand {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  min-width: 0;
  color: var(--foreground);
  text-decoration: none;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  color: var(--primary-foreground);
  background: var(--primary);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--primary-foreground) 12%, transparent);
}

.brand-name {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
}

.sidebar {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 30;
  display: flex;
  flex-direction: column;
  width: var(--sidebar-width, 264px);
  background: var(--card);
  border-right: 1px solid var(--border);
  transition:
    width 0.22s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 1.15rem 1rem;
  border-bottom: 1px solid var(--border-soft);
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  padding: 0;
  border: 1px solid transparent;
  border-radius: 8px;
  color: var(--muted-foreground);
  background: transparent;
  cursor: pointer;
  transition:
    background 0.15s ease,
    color 0.15s ease;
}

.icon-btn:hover {
  color: var(--foreground);
  background: var(--secondary);
}

.icon-btn:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 1px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-height: 0;
  padding: 0.9rem 0.7rem;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-group-label {
  margin: 0 0 0.35rem;
  padding: 0 0.6rem;
  color: var(--muted-foreground);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  min-height: 38px;
  padding: 0.45rem 0.6rem;
  border-radius: 8px;
  color: var(--muted-foreground);
  font-size: 0.88rem;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  transition:
    background 0.15s ease,
    color 0.15s ease;
}

.nav-item:hover {
  color: var(--foreground);
  background: var(--secondary);
}

.nav-item:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 1px;
}

.nav-item.active {
  color: var(--primary);
  background: var(--primary-soft);
}

.nav-item--cta {
  color: var(--primary-foreground);
  background: var(--primary);
}

.nav-item--cta:hover {
  color: var(--primary-foreground);
  background: var(--primary);
  opacity: 0.85;
}

.nav-item--cta.active {
  color: var(--primary-foreground);
  background: var(--primary);
  box-shadow: inset 0 0 0 2px color-mix(in srgb, var(--primary-foreground) 25%, transparent);
}

.nav-icon {
  flex-shrink: 0;
}

.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  margin-left: auto;
  padding: 0 6px;
  border-radius: 999px;
  color: var(--primary-foreground);
  background: var(--destructive);
  font-size: 0.68rem;
  font-weight: 700;
  line-height: 1;
  flex-shrink: 0;
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  padding: 0.75rem 0.7rem 0.9rem;
  border-top: 1px solid var(--border-soft);
}

.sidebar-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0 0.25rem;
}

.sidebar-actions :deep(.btn) {
  width: 34px;
  height: 34px;
  padding: 0;
}

.sidebar-actions :deep(.notification-bell) {
  width: 34px;
  height: 34px;
  color: var(--muted-foreground);
}

.sidebar-actions :deep(.notification-bell:hover),
.sidebar-actions :deep(.notification-bell.active) {
  color: var(--foreground);
}

.sidebar-notify {
  display: inline-flex;
}

/* Open the notification popover upward, away from the bottom edge. */
.sidebar-notify :deep(.dropdown-menu) {
  top: auto;
  right: auto;
  bottom: calc(100% + 8px);
  left: 0;
  width: min(320px, calc(100vw - 2rem));
  background: var(--popover);
  box-shadow: var(--shadow-overlay);
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  min-width: 0;
  padding: 0.45rem 0.5rem;
  border-radius: 10px;
  color: var(--foreground);
  text-decoration: none;
  transition: background 0.15s ease;
}

.profile-card:hover {
  background: var(--secondary);
}

.profile-card.active {
  background: var(--primary-soft);
}

.profile-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
  line-height: 1.25;
}

.profile-name {
  overflow: hidden;
  font-size: 0.84rem;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.profile-role {
  color: var(--muted-foreground);
  font-size: 0.72rem;
  font-weight: 600;
}

.profile-chevron {
  margin-left: auto;
  color: var(--muted-foreground);
  flex-shrink: 0;
}

@media (min-width: 901px) {
  .sidebar.collapsed {
    width: var(--sidebar-width-collapsed, 78px);
  }

  .sidebar.collapsed .sidebar-header {
    flex-direction: column;
    gap: 0.55rem;
    padding: 0.9rem 0.5rem;
  }

  .sidebar.collapsed .brand-name,
  .sidebar.collapsed .nav-label,
  .sidebar.collapsed .nav-group-label,
  .sidebar.collapsed .profile-text,
  .sidebar.collapsed .profile-chevron {
    display: none;
  }

  .sidebar.collapsed .sidebar-nav {
    padding-inline: 0.55rem;
  }

  .sidebar.collapsed .nav-item {
    justify-content: center;
    gap: 0;
    padding-inline: 0;
  }

  .sidebar.collapsed .nav-badge {
    position: absolute;
    top: 5px;
    right: 7px;
    min-width: 8px;
    width: 8px;
    height: 8px;
    padding: 0;
    font-size: 0;
  }

  .sidebar.collapsed .nav-item {
    position: relative;
  }

  .sidebar.collapsed .sidebar-actions {
    flex-direction: column;
    gap: 0.35rem;
    padding: 0;
  }

  .sidebar.collapsed .profile-card {
    justify-content: center;
    padding: 0.35rem 0;
  }
}

/* ---------- Mobile top bar ---------- */
.sidebar-topbar {
  position: fixed;
  top: 0;
  right: 0;
  left: 0;
  z-index: 40;
  display: none;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  height: 60px;
  padding: 0 0.9rem;
  background: color-mix(in srgb, var(--card) 88%, transparent);
  border-bottom: 1px solid var(--border-soft);
  backdrop-filter: blur(12px);
}

.topbar-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: 0.95rem;
  font-weight: 700;
  text-decoration: none;
}

.topbar-brand .brand-mark {
  width: 30px;
  height: 30px;
  border-radius: 8px;
}

.topbar-profile {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
}

.topbar-login {
  color: var(--primary);
  font-size: 0.85rem;
  font-weight: 700;
  text-decoration: none;
}

.sidebar-scrim {
  position: fixed;
  inset: 0;
  z-index: 50;
  background: var(--scrim);
  backdrop-filter: blur(2px);
}

.scrim-enter-active,
.scrim-leave-active {
  transition: opacity 0.22s ease;
}

.scrim-enter-from,
.scrim-leave-to {
  opacity: 0;
}

@media (max-width: 900px) {
  .sidebar-topbar {
    display: flex;
  }

  .sidebar {
    z-index: 60;
    width: min(300px, 86vw);
    box-shadow: var(--shadow-overlay);
    transform: translateX(-100%);
  }

  .sidebar.mobile-open {
    transform: translateX(0);
  }

  .sidebar-nav {
    padding: 1rem;
  }

  .sidebar-header {
    padding: 1rem;
  }

  .sidebar-footer {
    padding: 0.85rem 1rem 1rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .sidebar,
  .sidebar-scrim,
  .scrim-enter-active,
  .scrim-leave-active {
    transition: none;
  }
}
</style>
