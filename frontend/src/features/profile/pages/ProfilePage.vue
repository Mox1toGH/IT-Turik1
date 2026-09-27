<template>
  <section class="page-shell profile-page">
    <div v-if="isLoadingError" class="error-state">
      <p>Error while fetching profile info (code: {{ profileError?.code }})</p>
    </div>

    <template v-else>
      <header class="profile-header">
        <div class="profile-header-copy">
          <div class="breadcrumb-label">
            <span>Workspace</span>
            <span aria-hidden="true">/</span>
            <span>Profile</span>
          </div>

          <h1 class="text-6xl">My profile</h1>
          <p class="profile-subtitle text-xl">Manage your account details and preferences.</p>
        </div>

        <div class="profile-actions">
          <ui-card variant="stat" class="joined-card">
            <strong class="text-base">{{
              user?.created_at ? formatDate(user.created_at) : 'N/A'
            }}</strong>
            <span class="text-sm">Joined</span>
          </ui-card>
        </div>
      </header>

      <div class="profile-rule" aria-hidden="true"></div>

      <div class="profile-layout">
        <main class="profile-main">
          <Transition name="profile-section" mode="out-in">
            <ProfileOverviewSection
              v-if="activeSection === 'overview'"
              :user="user"
              :is-loading="isLoading"
            />

            <div v-else class="profile-content-view">
              <ui-button
                variant="ghost"
                size="sm"
                class="back-to-profile"
                @click="activeSection = 'overview'"
              >
                <ArrowRight class="back-icon" />
                Back to profile
              </ui-button>
              <component :is="activeComponent" />
            </div>
          </Transition>
        </main>

        <aside class="profile-rail">
          <ui-card
            variant="panel"
            class="rail-card"
            role="navigation"
            aria-label="Profile shortcuts"
          >
            <p class="rail-eyebrow">Activity</p>
            <button
              :class="['rail-link', { active: activeSection === 'statistics' }]"
              type="button"
              @click="activeSection = 'statistics'"
            >
              <span class="rail-link-copy"><EditIcon />My statistics</span>
              <ArrowRight />
            </button>
            <button
              :class="['rail-link', { active: activeSection === 'transactions' }]"
              type="button"
              @click="activeSection = 'transactions'"
            >
              <span class="rail-link-copy"><FileCheckIcon />Transaction history</span>
              <ArrowRight />
            </button>
            <button
              :class="['rail-link', { active: activeSection === 'orders' }]"
              type="button"
              @click="activeSection = 'orders'"
            >
              <span class="rail-link-copy"><TeamIcon />My shop orders</span>
              <ArrowRight />
            </button>
            <button
              :class="['rail-link', { active: activeSection === 'inventory' }]"
              type="button"
              @click="activeSection = 'inventory'"
            >
              <span class="rail-link-copy"><LockIcon />Digital inventory</span>
              <ArrowRight />
            </button>
          </ui-card>

          <ui-card
            variant="panel"
            class="rail-card account-card"
            role="navigation"
            aria-label="Account shortcuts"
          >
            <p class="rail-eyebrow">Account</p>

            <button
              :class="['rail-link', { active: activeSection === 'certificates' }]"
              type="button"
              @click="activeSection = 'certificates'"
            >
              <span class="rail-link-copy"><FileCheckIcon />Certificates</span>
              <ArrowRight />
            </button>
          </ui-card>

          <ui-button variant="danger" :disabled="isLoading || isDeleting" @click="logout">
            Log out
          </ui-button>
        </aside>
      </div>

      <ui-card v-if="activeSection === 'overview'" class="danger-zone">
        <div>
          <p class="danger-title">Danger zone</p>
          <p class="danger-text">Permanently delete your account and all associated data.</p>
        </div>
        <delete-profile-modal />
      </ui-card>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import ArrowRight from '@/icons/ArrowRight.vue'
import EditIcon from '@/icons/EditIcon.vue'
import FileCheckIcon from '@/icons/FileCheckIcon.vue'
import LockIcon from '@/icons/LockIcon.vue'
import TeamIcon from '@/icons/TeamIcon.vue'
import DeleteProfileModal from '../components/profile/modals/DeleteProfileModal.vue'
import ProfileOverviewSection from '../components/profile/sections/ProfileOverviewSection.vue'
import { useUserStore } from '@/stores/user'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { formatDate } from '@/lib/date'
import StatsPage from '@/features/stats/pages/StatsPage.vue'
import TransactionHistorySection from '../components/profile/sections/TransactionHistorySection.vue'
import ShopOrderHistoryPage from '@/features/shop/pages/ShopOrderHistoryPage.vue'
import ShopInventoryPage from '@/features/shop/pages/ShopInventoryPage.vue'
import CertificatesSection from '../components/profile/sections/CertificatesSection.vue'

type ProfileSection =
  | 'overview'
  | 'statistics'
  | 'transactions'
  | 'orders'
  | 'inventory'
  | 'certificates'

const store = useUserStore()
const { data: user, isLoading, isLoadingError, error: profileError } = useGetUserProfile()
const router = useRouter()
const isDeleting = ref(false)
const activeSection = ref<ProfileSection>('overview')

const viewComponents = {
  statistics: StatsPage,
  transactions: TransactionHistorySection,
  orders: ShopOrderHistoryPage,
  inventory: ShopInventoryPage,
  certificates: CertificatesSection,
} as const

const activeComponent = computed(
  () => viewComponents[activeSection.value as Exclude<ProfileSection, 'overview'>],
)

const logout = () => {
  store.logout()
  router.push('/login')
}
</script>

<style scoped>
.profile-page {
  max-width: 1180px;
  margin: 0 auto;
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.profile-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1.25rem;
}

.profile-header-copy {
  min-width: 0;
}

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--accent-strong);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.profile-header h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.profile-subtitle {
  margin: 0.45rem 0 0;
  max-width: 780px;
  color: var(--muted-foreground);
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.joined-card {
  display: flex;
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

.profile-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.profile-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.profile-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 1.6rem;
  align-items: start;
}

.profile-main,
.profile-rail {
  display: grid;
  gap: 1rem;
  min-width: 0;
}

.profile-section-enter-active,
.profile-section-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}

.profile-section-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.profile-section-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.rail-card {
  display: grid;
  gap: 0;
  padding: 1.25rem;
}

.account-card {
  padding-top: 1.25rem;
}

.rail-eyebrow {
  margin: 0 0 0.7rem;
  color: var(--muted-foreground);
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.rail-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  min-width: 0;
  min-height: 48px;
  padding: 0.7rem 0;
  color: var(--foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  text-decoration: none;
}

.rail-link {
  width: 100%;
  border: 0;
  background: transparent;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.rail-link + .rail-link {
  border-top: 1px solid var(--line-soft);
}

.rail-link:hover {
  background: color-mix(in srgb, var(--primary) 5%, transparent);
}

.rail-link.active {
  background: color-mix(in srgb, var(--primary) 5%, transparent);
  color: var(--primary);
}

.rail-link-copy {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: 0.6rem;
  font-weight: 600;
}

.rail-link-copy :deep(svg) {
  width: 1rem;
  height: 1rem;
  flex: 0 0 auto;
  color: var(--muted-foreground);
}

.rail-link > :deep(svg) {
  width: 1rem;
  height: 1rem;
  flex: 0 0 auto;
  color: var(--muted-foreground);
}

.profile-content-view {
  display: grid;
  gap: 0.8rem;
}

.back-to-profile {
  justify-self: end;
}

.back-icon {
  transform: rotate(180deg);
}

.danger-zone {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.35rem;
  border-color: var(--destructive);
  border-color: color-mix(in srgb, var(--destructive) 55%, var(--border));
  background: color-mix(in srgb, var(--destructive) 8%, var(--card));
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
  color: color-mix(in srgb, var(--destructive) 72%, var(--foreground));
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
}

.error-state {
  display: grid;
  min-height: 360px;
  place-items: center;
  border: 1px solid var(--destructive);
  border-radius: 14px;
  background: color-mix(in srgb, var(--destructive) 10%, var(--card));
  color: var(--destructive);
}

@media (max-width: 800px) {
  .profile-page {
    padding: 1rem 1rem 2rem;
  }

  .profile-layout {
    grid-template-columns: 1fr;
  }

  .profile-rail {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .profile-header {
    align-items: flex-start;
    flex-direction: column;
    gap: 1rem;
  }

  .profile-header h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .profile-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .profile-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 560px) {
  .profile-rail {
    grid-template-columns: 1fr;
  }

  .danger-zone {
    align-items: flex-start;
    flex-direction: column;
  }

  .edit-details-link,
  .danger-zone :deep(button) {
    align-self: stretch;
  }
}
</style>
