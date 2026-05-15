<template>
  <section class="page-shell">
    <ui-card :is-error="isLoadingError">
      <template #error>
        <div style="display: flex; height: 436px; justify-content: center; align-items: center">
          <p>Error while fetching profile info (code: {{ profileError?.code }})</p>
        </div>
      </template>

      <template #header>
        <div class="head">
          <div>
            <p class="section-eyebrow">User Center</p>
            <h1 class="section-title profile-title">My profile</h1>
          </div>
          <p class="meta">Joined: {{ user?.created_at ? formatDate(user?.created_at) : 'N/A' }}</p>
        </div>
        <div class="avatar-row">
          <div class="avatar-box">
            <user-avatar
              :avatar="user?.avatar"
              :avatar-frame-url="user?.avatar_frame_url"
              :username="user?.username || 'user'"
              :full-name="user?.full_name || ''"
              :size="108"
              :position-key="user?.id ? `image-position:avatar:user:${user.id}` : ''"
            />
            <avatar-modal :user="user" :disabled="isLoading" />
          </div>
          <ui-card class="balance-card">
            <template #header>
              <span class="card-text-title">Points balance</span>
            </template>
            <ui-skeleton-loader :loading="isPointsLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" width="100%" />
              </template>
              <p class="balance-value">{{ pointsBalance?.balance ?? 0 }}</p>
            </ui-skeleton-loader>
          </ui-card>
        </div>
      </template>

      <div class="details">
        <ui-card class="field-card">
          <template #header>
            <span class="card-text-title">Username</span>
          </template>
          <ui-skeleton-loader :loading="isLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" />
            </template>

            <strong class="item-value value-wrap">{{ user?.username || '-' }}</strong>
          </ui-skeleton-loader>
        </ui-card>
        <ui-card class="field-card">
          <template #header>
            <span class="card-text-title">Email</span>
          </template>

          <ui-skeleton-loader :loading="isLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" />
            </template>

            <strong class="item-value value-wrap">{{ user?.email || '-' }}</strong>
          </ui-skeleton-loader>
        </ui-card>
        <ui-card class="field-card">
          <template #header>
            <span class="card-text-title">Role</span>
          </template>

          <ui-skeleton-loader :loading="isLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" />
            </template>

            <ui-badge variant="green">{{ user?.role ?? '-' }}</ui-badge>
          </ui-skeleton-loader>
        </ui-card>
        <ui-card class="field-card">
          <template #header>
            <span class="card-text-title">Full name</span>
          </template>

          <ui-skeleton-loader :loading="isLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" />
            </template>

            <strong class="item-value value-wrap">{{ user?.full_name || '-' }}</strong>
          </ui-skeleton-loader>
        </ui-card>
        <ui-card class="field-card">
          <template #header>
            <span class="card-text-title">City</span>
          </template>

          <ui-skeleton-loader :loading="isLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" />
            </template>

            <strong class="item-value value-wrap">{{ user?.city || '-' }}</strong>
          </ui-skeleton-loader>
        </ui-card>
        <ui-card class="field-card">
          <template #header>
            <span class="card-text-title">Phone</span>
          </template>

          <ui-skeleton-loader :loading="isLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" />
            </template>

            <strong class="item-value value-fixed">{{ user?.phone || '-' }}</strong>
          </ui-skeleton-loader>
        </ui-card>
        <ui-card class="field-card">
          <template #header>
            <span class="card-text-title">Teams</span>
          </template>

          <div>
            <ui-skeleton-loader :loading="isLoading">
              <template #skeleton>
                <div style="display: flex; flex-direction: column; gap: 4px">
                  <ui-skeleton v-for="i in 2" :key="i" variant="rect" width="150px" />
                </div>
              </template>

              <div class="team-list">
                <router-link
                  v-for="team in user?.teams || []"
                  :key="team.id"
                  :to="`/teams/${team.id}`"
                  class="team-link"
                >
                  {{ team.name }}
                </router-link>
              </div>

              <p v-if="!(user?.teams || []).length" class="text-muted">No teams yet.</p>
            </ui-skeleton-loader>
          </div>
        </ui-card>
      </div>

      <div v-if="user?.active_tournament" class="tournament-overview-row">
        <router-link :to="`/tournaments/${user.active_tournament.id}`" class="overview-link">
          <ui-card class="active-tournament-card">
            <template #header>
              <span class="card-text-title">Active tournament</span>
            </template>
            <div class="active-tournament-content">
              <div>
                <p class="active-tournament-name">{{ user.active_tournament.name }}</p>
                <p class="active-tournament-meta">{{ formatDate(user.active_tournament.start_date) }} - {{ formatDate(user.active_tournament.end_date) }}</p>
              </div>
              <ui-button
                as-link
                to="/profile/tournaments-history"
                variant="secondary"
                size="sm"
                class="history-btn"
                @click.stop
              >
                Tournament history
              </ui-button>
            </div>
          </ui-card>
        </router-link>
      </div>

      <div class="stats-link-row">
        <ui-button :disabled="isLoading" as-link to="/stats" variant="secondary"
          >My Statistics</ui-button
        >
        <ui-button :disabled="isLoading" as-link to="/profile/points" variant="secondary">
          Transaction History
        </ui-button>
        <ui-button :disabled="isLoading" as-link to="/profile/orders" variant="secondary"
          >My Shop Orders</ui-button
        >
        <ui-button :disabled="isLoading" as-link to="/profile/inventory" variant="secondary"
          >Digital Inventory</ui-button
        >
      </div>

      <div class="actions">
        <ui-button :disabled="isLoading" @click="goToEditProfile"> Edit Profile </ui-button>
        <ui-button :disabled="isLoading" @click="goToNotifications"> Notifications </ui-button>
        <ui-button :disabled="isLoading" @click="goToCertificates"> Certificates </ui-button>
        <ui-button variant="danger" :disabled="isLoading || isDeleting" @click="logout">
          Log Out
        </ui-button>
      </div>

      <ui-card class="danger-zone">
        <p class="danger-text">Danger zone: this action permanently deletes your account.</p>

        <delete-profile-modal />
      </ui-card>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import DeleteProfileModal from '../components/profile/modals/DeleteProfileModal.vue'
import AvatarModal from '../components/profile/modals/AvatarModal.vue'
import { useUserStore } from '@/stores/user'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { formatDate } from '@/lib/date'
import { useGetMyPointsBalance } from '@/api/points/points'

const store = useUserStore()
const { data: user, isLoading, isLoadingError, error: profileError } = useGetUserProfile()
const { data: pointsBalance, isLoading: isPointsLoading } = useGetMyPointsBalance()

const router = useRouter()
const isDeleting = ref(false)

const logout = () => {
  store.logout()
  router.push('/login')
}

const goToEditProfile = () => {
  router.push('/profile/edit')
}

const goToNotifications = () => {
  router.push('/profile/notifications')
}

const goToCertificates = () => {
  router.push('/profile/certificates')
}

</script>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

.profile-title {
  margin-top: 0.2rem;
}

.meta {
  margin: 0;
  font-size: 0.86rem;
}

.avatar-row {
  margin-top: 0.8rem;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.9rem;
}

.avatar-box {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}

.balance-card {
  min-width: 220px;
  border: 1px solid color-mix(in srgb, var(--primary) 35%, transparent);
  background: color-mix(in srgb, var(--primary) 12%, var(--muted));
}

.balance-value {
  margin: 0;
  font-size: 2rem;
  line-height: 1;
  font-weight: 800;
  color: var(--primary);
}

.details {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.6rem;
  margin-top: 1rem;
  align-items: start;
}

.item {
  border: 1px solid var(--line-soft);
  border-radius: 14px;
  padding: 0.7rem;
  background: rgba(255, 255, 255, 0.85);
  min-width: 0;
  display: grid;
  gap: 0.3rem;
  align-content: start;
}

.item-label {
  color: var(--color-gray-500);
  font-size: 0.8rem;
  font-weight: 600;
  line-height: 1.2;
}

.field-card {
  background: var(--muted);
  color: var(--muted-foreground);
  gap: 0;
}

.item-phone {
  align-content: start;
}

.item-wide {
  grid-column: 1 / -1;
}

.team-list {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.team-link {
  color: var(--brand-700);
  text-decoration: none;
  font-weight: 700;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.badge {
  width: max-content;
  text-transform: uppercase;
}

.actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.stats-link-row {
  margin-top: 0.9rem;
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.tournament-overview-row {
  margin-top: 0.9rem;
  min-width: 220px;
  width: fit-content;
  max-width: 100%;
}

.overview-link {
  text-decoration: none;
  color: inherit;
}

.active-tournament-card {
  border: 1px solid color-mix(in srgb, var(--primary) 35%, transparent);
  background: color-mix(in srgb, var(--primary) 10%, var(--muted));
  min-height: 100%;
}

.active-tournament-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
}

.active-tournament-name,
.active-tournament-meta {
  margin: 0;
}

.active-tournament-name {
  font-weight: 700;
  color: var(--foreground);
}

.history-btn {
  align-self: center;
  border-color: color-mix(in srgb, var(--primary) 75%, #ffffff 25%);
  background: var(--primary);
  color: white;
  font-weight: 700;
  white-space: nowrap;
}

.history-btn:hover,
.history-btn:focus-visible,
.history-btn:active {
  background: color-mix(in srgb, var(--primary) 84%, black 16%);
  color: white;
  border-color: color-mix(in srgb, var(--primary) 72%, black 28%);
}

.danger-zone {
  margin-top: 1.4rem;
  padding-top: 1rem;
  border: 1px solied var(--destructive);
  background: color-mix(in srgb, var(--destructive) 10%, transparent);
}

.danger-text {
  margin: 0 0 0.6rem;
  color: color-mix(in srgb, var(--destructive) 80%, transparent);
  font-weight: 600;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: grid;
  place-items: center;
  z-index: 50;
  padding: 1rem;
}

@media (max-width: 760px) {
  .profile-card {
    max-width: 100%;
    margin: 0;
  }

  .head {
    flex-direction: column;
    align-items: flex-start;
  }

  .avatar-row {
    flex-direction: column;
    align-items: stretch;
  }

  .balance-card {
    min-width: 0;
    width: 100%;
  }

  .details {
    grid-template-columns: 1fr;
  }

  .tournament-overview-row {
    width: 100%;
    min-width: 0;
  }

  .actions {
    flex-direction: column;
  }
}
</style>
