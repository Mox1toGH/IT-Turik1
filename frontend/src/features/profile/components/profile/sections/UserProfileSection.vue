<template>
  <section class="page-shell">
    <ui-query-block :query="userQuery" title="profile">
      <ui-card>
        <template #header>
          <div class="head">
            <div>
              <p class="section-eyebrow">User Profile</p>
              <div class="section-title profile-title" role="heading" aria-level="1">
                <ui-query-field>
                  <template #skeleton
                    ><ui-skeleton variant="rect" width="220px" height="36px"
                  /></template>
                  <span>{{ user?.full_name || user?.username || '-' }}</span>
                </ui-query-field>
              </div>
            </div>
            <div class="meta">
              Joined:
              <ui-query-field>
                <template #skeleton
                  ><ui-skeleton variant="rect" width="100px" height="16px"
                /></template>
                <span>{{ user?.created_at ? formatDate(user?.created_at) : 'N/A' }}</span>
              </ui-query-field>
            </div>
          </div>
          <ui-query-field>
            <template #skeleton
              ><ui-skeleton variant="rounded" width="108px" height="108px"
            /></template>
            <user-avatar
              :avatar="user?.avatar"
              :username="user?.username || 'user'"
              :full-name="user?.full_name || ''"
              :size="108"
              :position-key="user?.id ? `image-position:avatar:user:${user.id}` : ''"
            />
          </ui-query-field>
        </template>

        <div class="details">
          <div class="field-row">
            <span class="field-label">Username</span>
            <ui-query-field
              ><template #skeleton><ui-skeleton variant="rect" width="120px" /></template
              ><strong class="item-value value-wrap">{{
                user?.username || '-'
              }}</strong></ui-query-field
            >
          </div>
          <div class="field-row">
            <span class="field-label">Email</span>
            <ui-query-field
              ><template #skeleton><ui-skeleton variant="rect" width="160px" /></template
              ><strong class="item-value value-wrap">{{
                user?.email || '-'
              }}</strong></ui-query-field
            >
          </div>
          <div class="field-row">
            <span class="field-label">Role</span>
            <ui-query-field
              ><template #skeleton><ui-skeleton variant="rect" width="80px" /></template
              ><ui-badge variant="green">{{ user?.role ?? '-' }}</ui-badge></ui-query-field
            >
          </div>
          <div class="field-row">
            <span class="field-label">Full name</span>
            <ui-query-field
              ><template #skeleton><ui-skeleton variant="rect" width="140px" /></template
              ><strong class="item-value value-wrap">{{
                user?.full_name || '-'
              }}</strong></ui-query-field
            >
          </div>
          <div class="field-row">
            <span class="field-label">City</span>
            <ui-query-field
              ><template #skeleton><ui-skeleton variant="rect" width="90px" /></template
              ><strong class="item-value value-wrap">{{
                user?.city || '-'
              }}</strong></ui-query-field
            >
          </div>
          <div class="field-row">
            <span class="field-label">Phone</span>
            <ui-query-field
              ><template #skeleton><ui-skeleton variant="rect" width="120px" /></template
              ><strong class="item-value value-fixed">{{
                user?.phone || '-'
              }}</strong></ui-query-field
            >
          </div>
          <div class="field-row field-row--wide">
            <span class="field-label">Teams</span>
            <div>
              <ui-query-field>
                <template #skeleton>
                  <div class="team-list-skeleton">
                    <ui-skeleton variant="rect" width="140px" height="20px" /><ui-skeleton
                      variant="rect"
                      width="120px"
                      height="20px"
                    />
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
              </ui-query-field>
            </div>
          </div>
        </div>

        <div v-if="user?.active_tournament" class="tournament-overview-row">
          <router-link :to="`/tournaments/${user.active_tournament.id}`" class="overview-link">
            <div class="active-tournament-card">
              <span class="card-text-title">Active tournament</span>
              <div class="active-tournament-content">
                <div>
                  <p class="active-tournament-name">{{ user.active_tournament.name }}</p>
                  <p class="active-tournament-meta">
                    {{ formatDate(user.active_tournament.start_date) }} -
                    {{ formatDate(user.active_tournament.end_date) }}
                  </p>
                </div>
                <ui-button
                  as-link
                  :to="`/users/${userId}/tournaments-history`"
                  variant="secondary"
                  size="sm"
                  class="history-btn"
                  @click.stop
                >
                  Tournament history
                </ui-button>
              </div>
            </div>
          </router-link>
        </div>
      </ui-card>
    </ui-query-block>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiBadge from '@/components/ui/UiBadge'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import { useGetUser } from '@/api/accounts/accounts'
import { formatDate } from '@/lib/date'

const route = useRoute()
const userId = computed(() => Number(route.params.id))
const userQuery = useGetUser(userId)
const { data: user } = userQuery
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
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

.details {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0 1.5rem;
  margin-top: 1rem;
  border-top: 1px solid var(--border);
}

.field-row {
  display: grid;
  gap: 0.3rem;
  align-content: start;
  min-width: 0;
  padding: 0.7rem 0;
}

.details .field-row + .field-row {
  border-top: 1px solid var(--border);
}

.field-label {
  color: var(--muted-foreground);
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 600;
}

.field-row--wide {
  grid-column: 1 / -1;
}

.item-value {
  color: var(--foreground);
  overflow-wrap: anywhere;
}

.team-list {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.team-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 700;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.team-link:hover {
  text-decoration: underline;
  text-underline-offset: 2px;
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
  display: grid;
  gap: 0.6rem;
  padding: 0.9rem;
  border-radius: var(--radius-sm);
  background: var(--subtle);
  min-height: 100%;
}

.card-text-title {
  color: var(--muted-foreground);
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
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

.active-tournament-meta {
  color: var(--muted-foreground);
}

.history-btn {
  align-self: center;
  white-space: nowrap;
}

@media (max-width: 760px) {
  .head {
    flex-direction: column;
    align-items: flex-start;
  }

  .details {
    grid-template-columns: 1fr;
  }

  .tournament-overview-row {
    width: 100%;
    min-width: 0;
  }
}
</style>
