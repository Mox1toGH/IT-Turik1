<template>
  <div class="invitations-panel">
    <div class="panel-head">
      <div>
        <h2>Pending invitations</h2>
        <p class="text-muted">People who have been invited to this team.</p>
      </div>
      <p class="panel-count">
        <strong>{{ pendingInvitations.length }}</strong>
        <span>Awaiting</span>
      </p>
    </div>

    <ui-query-block :query="props.query">
      <ui-query-field>
        <template #skeleton>
          <div class="invitation-grid">
            <div v-for="i in 2" :key="`invitation-skeleton-${i}`" class="invitation-card-skeleton">
              <div class="invitation-card-skeleton-top">
                <ui-skeleton variant="rounded" width="44px" height="44px" />
                <div class="invitation-card-skeleton-lines">
                  <ui-skeleton variant="rect" width="120px" height="14px" />
                  <ui-skeleton variant="rect" width="160px" height="12px" />
                </div>
              </div>
            </div>
          </div>
        </template>

        <template #default>
          <p v-if="isEmpty" class="text-muted invitations-note">No invitations yet.</p>
          <div v-else class="invitation-grid">
            <ui-card
              v-for="invitation in props.invitations"
              :key="`inv-${invitation.id}`"
              class="invitation-card"
            >
              <div class="invitation-top">
                <user-avatar
                  :avatar="invitation.user.avatar"
                  :username="invitation.user.username"
                  :full-name="invitation.user.full_name || ''"
                  :size="44"
                />

                <div class="invitation-main">
                  <p class="invitation-name">{{ invitation.user.username }}</p>
                  <p class="text-muted invitation-email">{{ invitation.user.email }}</p>
                </div>

                <ui-badge :variant="invitationVariant(invitation.status)">
                  {{ invitation.status }}
                </ui-badge>
              </div>

              <p class="text-muted invitation-date">
                Invited {{ formatDate(invitation.created_at, { showHours: true }) }}
              </p>
            </ui-card>
          </div>
        </template>
      </ui-query-field>
    </ui-query-block>
  </div>
</template>

<script setup lang="ts">
import UiBadge, { type Variants } from '@/components/ui/UiBadge'
import UiCard from '@/components/ui/UiCard'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import { computed } from 'vue'
import { formatDate } from '@/lib/date'
import type { TeamInvitation } from '@/features/teams/types'
import type { QueryLike } from '@/composables/useQueryState'

interface Props {
  invitations: TeamInvitation[]
  query: QueryLike
}

const props = defineProps<Props>()

const isEmpty = computed(() => props.invitations.length === 0)

const pendingInvitations = computed(() =>
  props.invitations.filter((invitation) => invitation.status === 'invited'),
)

const invitationVariant = (status: string): Variants => {
  if (status === 'accepted') return 'green'
  if (status === 'declined') return 'red'
  return 'orange'
}
</script>

<style scoped>
.invitations-panel {
  display: grid;
  gap: 1.25rem;
  min-width: 0;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  min-width: 0;
}

.panel-head h2 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
  font-weight: 800;
}

.panel-head p {
  margin: 0.25rem 0 0;
}

.panel-count {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.7rem;
  margin: 0;
  flex-shrink: 0;
}

.panel-count strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
  font-weight: 800;
}

.panel-count span {
  color: var(--muted-foreground);
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.invitation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
}

.invitation-card {
  height: 100%;
  min-width: 0;
  gap: 0.85rem;
}

.invitation-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.invitation-main {
  flex: 1;
  min-width: 0;
}

.invitation-name {
  margin: 0;
  font-weight: 700;
  min-width: 0;
  overflow-wrap: anywhere;
}

.invitation-email {
  margin: 0.15rem 0 0;
  font-size: 0.84rem;
  overflow-wrap: anywhere;
}

.invitation-date {
  margin-top: 1rem;
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
}

.invitations-note {
  margin: 0;
  padding: 1rem 0;
  text-align: center;
}

.invitation-card-skeleton {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
  padding: 1.2rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
}

.invitation-card-skeleton-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.invitation-card-skeleton-lines {
  display: grid;
  gap: 0.4rem;
}
</style>
