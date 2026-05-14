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
            <p class="section-eyebrow">User Profile</p>
            <h1 class="section-title profile-title">
              {{ user?.full_name || user?.username || '-' }}
            </h1>
          </div>
          <p class="meta">Joined: {{ user?.created_at ? formatDate(user?.created_at) : 'N/A' }}</p>
        </div>
        <user-avatar
          :avatar="user?.avatar"
          :avatar-frame-url="user?.avatar_frame_url"
          :username="user?.username || 'user'"
          :full-name="user?.full_name || ''"
          :size="108"
          :position-key="user?.id ? `image-position:avatar:user:${user.id}` : ''"
        />
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
            <span class="card-text-title">Points balance</span>
          </template>
          <ui-skeleton-loader :loading="isAdminPointsLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" />
            </template>

            <strong class="item-value value-wrap">{{
              isAdmin ? (adminPointsBalance?.balance ?? 0) : '-'
            }}</strong>
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

      <ui-card v-if="isAdmin" class="manage-card">
        <template #header>
          <span class="card-text-title">Manage points balance</span>
        </template>
        <div class="manage-grid">
          <label class="field">
            <span class="field-label">Action</span>
            <ui-select
              v-model="operation"
              :options="operationOptions"
              placeholder="Select action"
              min-width="100%"
            />
          </label>
          <label class="field" v-if="operation !== 'reset'">
            <span class="field-label">Amount</span>
            <ui-input v-model="amount" type="number" min="0" />
          </label>
          <label class="field reason-field">
            <span class="field-label">Reason</span>
            <ui-input v-model="reason" />
          </label>
        </div>
        <div class="manage-actions">
          <ui-button :disabled="isSubmitting || !reason.trim()" @click="submitPointsUpdate">
            Apply
          </ui-button>
        </div>
      </ui-card>

      <div class="actions">
        <ui-button v-if="isAdmin" :disabled="isLoading" @click="goToTransactions"
          >Transaction History</ui-button
        >
        <ui-button :disabled="isLoading" @click="goBack">Back</ui-button>
      </div>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import { useGetUser, useGetUserProfile } from '@/api/accounts/accounts'
import { useAdminModifyUserPoints, useAdminUserPointsBalance } from '@/api/queries/points'
import { useNotification } from '@/composables/useNotification'
import { formatDate } from '@/lib/date'

const route = useRoute()
const router = useRouter()
const userId = computed(() => Number(route.params.id))
const { data: user, isLoading, isLoadingError, error: profileError } = useGetUser(userId)
const { data: viewer } = useGetUserProfile()
const isAdmin = computed(() => viewer.value?.role === 'admin')
const { showNotification } = useNotification()

const {
  data: adminPointsBalance,
  isLoading: isAdminPointsLoading,
  refetch: refetchAdminBalance,
} = useAdminUserPointsBalance(userId, { enabled: isAdmin })

const { mutateAsync: modifyUserPoints, isPending: isSubmitting } = useAdminModifyUserPoints()
const operation = ref<'add' | 'subtract' | 'set' | 'reset'>('add')
const amount = ref<number>(0)
const reason = ref('')
const operationOptions: Array<{ value: 'add' | 'subtract' | 'set' | 'reset'; label: string }> = [
  { value: 'add', label: 'Add points' },
  { value: 'subtract', label: 'Subtract points' },
  { value: 'set', label: 'Set exact balance' },
  { value: 'reset', label: 'Reset to zero' },
]

const goBack = () => {
  router.back()
}

const goToTransactions = () => {
  router.push(`/users/${userId.value}/points`)
}

const submitPointsUpdate = async () => {
  if (!isAdmin.value || !userId.value) return

  try {
    await modifyUserPoints({
      userId: userId.value,
    })
    await refetchAdminBalance()
    reason.value = ''
    amount.value = 0
    showNotification('Points balance updated.', 'success')
  } catch (error) {
    showNotification(error?.message || 'Failed to update points balance.', 'error')
  }
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

.manage-card {
  margin-top: 1rem;
  background: var(--muted);
  color: var(--muted-foreground);
}

.manage-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.6rem;
}

.field {
  display: grid;
  gap: 0.35rem;
}

.field-label {
  font-size: 0.8rem;
  color: var(--color-gray-500);
  font-weight: 600;
}

.reason-field {
  grid-column: 1 / -1;
}

.manage-actions {
  margin-top: 0.8rem;
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

  .details {
    grid-template-columns: 1fr;
  }

  .actions {
    flex-direction: column;
  }

  .manage-grid {
    grid-template-columns: 1fr;
  }
}
</style>
