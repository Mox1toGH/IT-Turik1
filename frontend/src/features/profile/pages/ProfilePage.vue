<template>
  <section class="page-shell profile-page">
    <header class="profile-hero">
      <div class="profile-hero-copy">
        <div class="breadcrumb-label">
          <span>Workspace</span>
          <span aria-hidden="true">/</span>
          <span>Profile</span>
        </div>

        <h1 class="text-4xl">My profile</h1>
        <p class="section-subtitle text-base">Manage your account details and preferences.</p>
      </div>

      <div class="profile-hero-actions">
        <ui-card class="joined-card">
          <strong class="text-base">{{
            user?.created_at ? formatDate(user.created_at) : 'N/A'
          }}</strong>
          <span class="text-sm">Joined</span>
        </ui-card>
      </div>
    </header>

    <div class="profile-rule" aria-hidden="true"></div>

    <div v-if="isLoadingError" class="error-state">
      <p>Error while fetching profile info</p>
    </div>

    <div v-else class="profile-layout">
      <aside class="profile-sidebar">
        <div class="sidebar-sticky">
          <ui-card class="sidebar-card">
            <template #header>
              <div class="sidebar-card-header">
                <p class="section-eyebrow">Sections</p>
              </div>
            </template>
            <nav class="anchor-nav" aria-label="Profile sections">
              <a
                v-for="section in profileSections"
                :key="section.key"
                :href="`#${section.key}`"
                class="anchor-chip"
                @click.prevent="scrollToSection(section.key)"
              >
                {{ section.label }}
              </a>
            </nav>
          </ui-card>

          <ui-card class="sidebar-card">
            <template #header>
              <div class="sidebar-card-header">
                <p class="section-eyebrow">Quick actions</p>
              </div>
            </template>
            <div class="quick-actions">
              <ui-button
                variant="danger"
                size="sm"
                :disabled="isLoading || isDeleting"
                @click="logout"
              >
                Log out
              </ui-button>
            </div>
          </ui-card>
        </div>
      </aside>

      <div class="profile-content">
        <div id="overview" class="profile-group">
          <ProfileOverviewSection :user="user" :is-loading="isLoading" :query="userQuery" />
        </div>

        <div id="statistics" class="profile-group">
          <UserStats />
        </div>

        <div id="account" class="profile-group">
          <ui-card class="danger-zone">
            <div>
              <div>
                <p class="danger-title">Danger zone</p>
                <p class="danger-text">Permanently delete your account and all associated data.</p>
              </div>

              <ui-button
                class="danger-action"
                type="button"
                variant="danger"
                :disabled="isLoading"
                @click="isDeleteModalOpen = true"
              >
                Delete account
              </ui-button>
            </div>

            <delete-profile-modal v-model="isDeleteModalOpen" />
          </ui-card>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import DeleteProfileModal from '../components/profile/modals/DeleteProfileModal.vue'
import ProfileOverviewSection from '../components/profile/sections/ProfileOverviewSection.vue'
import UserStats from '../components/profile/sections/UserStats.vue'
import { useUserStore } from '@/stores/user'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { formatDate } from '@/lib/date'

interface ProfileSection {
  key: string
  label: string
}

const profileSections: ProfileSection[] = [
  { key: 'overview', label: 'Overview' },
  { key: 'statistics', label: 'Statistics' },
  { key: 'account', label: 'Danger zone' },
]

const store = useUserStore()
const userQuery = useGetUserProfile()
const { data: user, isLoading, isLoadingError } = userQuery
const router = useRouter()
const isDeleting = ref(false)
const isDeleteModalOpen = ref(false)

const logout = () => {
  store.logout()
  router.push('/login')
}

function scrollToSection(key: string) {
  document.getElementById(key)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<style scoped>
.profile-page {
  gap: 1.4rem;
}

.profile-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.profile-hero-copy {
  min-width: 0;
}

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.profile-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.profile-hero .section-subtitle {
  margin: 0.45rem 0 0;
  max-width: 780px;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.profile-hero-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  flex-shrink: 0;
}

.joined-card {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
  padding: 0.5rem 1.1rem;
  min-height: 30px;
  border-color: var(--border);
}

.joined-card strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
  white-space: nowrap;
}

.joined-card span {
  color: var(--muted-foreground);
  font-weight: 700;
  white-space: nowrap;
}

.profile-rule {
  height: 1px;
  background: var(--border);
}

.profile-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 1.5rem;
  align-items: start;
}

.profile-sidebar {
  align-self: stretch;
}

.sidebar-sticky {
  position: sticky;
  top: calc(var(--nav-offset, 76px) + 1rem);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-height: calc(100vh - var(--nav-offset, 76px) - 2rem);
  overflow-y: auto;
  overscroll-behavior: contain;
}

.sidebar-card {
  flex-shrink: 0;
}

.sidebar-card-header {
  display: flex;
  align-items: center;
}

.section-eyebrow {
  margin: 0;
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted-foreground);
}

.anchor-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.anchor-chip {
  display: block;
  padding: 0.4rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--muted-foreground);
  text-decoration: none;
  transition:
    background-color 0.15s ease,
    color 0.15s ease;
}

.anchor-chip:hover {
  background: var(--subtle);
  color: var(--foreground);
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 2.25rem;
  min-width: 0;
}

.profile-group {
  scroll-margin-top: calc(var(--nav-offset, 76px) + 1rem);
  min-width: 0;
}

/* Clear separation between the stacked sections in the content column. */
.profile-group + .profile-group {
  border-top: 1px solid var(--border);
  padding-top: 2.25rem;
}

.danger-zone.card {
  flex-direction: column;
  align-items: flex-start;
  padding: 1.35rem;
  border-color: var(--destructive-ring);
  background: var(--destructive-soft);
}

.danger-action {
  margin-top: 1rem;
  width: max-content;
}

.danger-title,
.danger-text {
  margin: 0;
}

.danger-title {
  color: var(--destructive);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
}

.danger-text {
  margin-top: 0.35rem;
  color: var(--muted-foreground);
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
}

.error-state {
  display: grid;
  min-height: 360px;
  place-items: center;
  border: 1px solid var(--destructive-ring);
  border-radius: var(--radius);
  background: var(--destructive-soft);
  color: var(--destructive);
}

@media (max-width: 1024px) {
  .profile-layout {
    grid-template-columns: 1fr;
  }

  .sidebar-sticky {
    position: static;
    max-height: none;
    overflow: visible;
  }

  .anchor-nav {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .anchor-chip {
    padding: 0.35rem 0.75rem;
    border: 1px solid var(--border);
    border-radius: 999px;
  }
}

@media (max-width: 800px) {
  .profile-page {
    padding: 1rem 1rem 2rem;
  }

  .profile-hero {
    align-items: flex-start;
    flex-direction: column;
    gap: 1rem;
  }

  .profile-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .profile-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .profile-hero-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 560px) {
  .danger-action {
    width: 100%;
  }
}
</style>
