<template>
  <ui-card :is-error="props.loadingError">
    <template #error>
      <div style="display: flex; justify-content: center; align-items: center; height: 200px">
        <p>Failed to fetch team members</p>
      </div>
    </template>

    <div class="members-sections">
      <section class="members-section">
        <header class="section-subhead">
          <h3>Members</h3>
          <ui-skeleton-loader :loading="props.loading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="80px" />
            </template>

            <span class="text-muted">{{ filteredMembers?.length }} people</span>
          </ui-skeleton-loader>
        </header>

        <ui-skeleton-loader :loading="props.loading">
          <template #skeleton>
            <div class="member-list">
              <ui-card v-for="i in 2" :key="i" class="card-item">
                <div style="display: flex; flex-direction: column; gap: 4px">
                  <div style="display: flex; justify-content: space-between; gap: 10px">
                    <ui-skeleton variant="rect" width="100%" />
                    <ui-skeleton variant="rect" width="100px" />
                  </div>

                  <ui-skeleton variant="rect" width="200px" />
                </div>
              </ui-card>
            </div>
          </template>

          <div class="member-list">
            <ui-card
              class="card-item"
              v-for="member in filteredMembers"
              :key="`member-${member.id}`"
            >
              <div class="member-row">
                <div v-if="member.avatar" class="member-avatar-wrap">
                  <img :src="member.avatar" :alt="`${member.username} avatar`" class="member-avatar" />
                </div>
                <div v-else class="member-avatar member-avatar-fallback">
                  {{ getMemberInitials(member.full_name || member.username) }}
                </div>

                <div class="member-main">
                <div style="display: flex; justify-content: space-between">
                  <p class="member-name">
                    <RouterLink :to="`/users/${member.id}`" class="member-link">
                      {{ member.username }}
                    </RouterLink>
                  </p>

                  <ui-badge v-if="member.id === props.team?.captain_id" variant="green"
                    >Captain</ui-badge
                  >
                  <ui-badge v-else variant="gray">Member</ui-badge>
                </div>

                <p class="text-muted member-email">{{ member.email }}</p>
                </div>
              </div>
            </ui-card>

            <p v-if="filteredMembers?.length === 0" class="text-muted">
              No accepted members match your search.
            </p>
          </div>
        </ui-skeleton-loader>
      </section>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import type { GetProfileResponse } from '@/api/services/accounts/types'
import type { GetTeamInfoResponse } from '@/api/services/teams/types'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { computed } from 'vue'

interface Props {
  team?: GetTeamInfoResponse
  user?: GetProfileResponse
  loading: boolean
  loadingError?: boolean
  searchFilter?: string
  isCaptain: boolean
}

const props = defineProps<Props>()

const matches = (parts: (string | undefined)[]) => {
  const q = props.searchFilter?.trim().toLowerCase()
  if (!q) return true
  return parts.some((p) => p?.toLowerCase().includes(q))
}

const filteredMembers = computed(() =>
  props.team?.members.filter((m) => matches([m.username, m.email, m.full_name])),
)

const getMemberInitials = (name: string) => {
  const parts = name.trim().split(/\s+/).filter(Boolean)
  if (!parts.length) return '?'
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
}
</script>

<style scoped>
.panel {
  border: 1px solid var(--line-soft);
  height: 100%;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  margin-bottom: 0.9rem;
}

.panel-head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.15rem;
}

.card-item {
  background-color: var(--muted);
}

.members-sections {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.members-section {
  display: grid;
  gap: 0.65rem;
}

.section-subhead {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.8rem;
}

.section-subhead h3 {
  margin: 0;
  font-size: 1rem;
}

.member-list {
  overflow-y: auto;
  max-height: 300px;
  display: grid;
  gap: 0.55rem;
  grid-template-rows: auto;
}

.member-name,
.member-email {
  margin: 0;
}

.member-name {
  font-weight: 700;
}

.member-row {
  display: flex;
  gap: 0.7rem;
  align-items: center;
}

.member-main {
  flex: 1;
  min-width: 0;
}

.member-avatar-wrap {
  width: 42px;
  height: 42px;
}

.member-avatar {
  width: 42px;
  height: 42px;
  border-radius: 999px;
  object-fit: cover;
  border: 1px solid var(--line-soft);
  flex-shrink: 0;
}

.member-avatar-fallback {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--color-gray-700);
  font-weight: 700;
  background: color-mix(in srgb, var(--brand-100) 40%, white);
}

.member-link {
  color: var(--brand-700);
  text-decoration: none;
  font-weight: 700;
}

.member-email {
  font-size: 0.84rem;
}

.member-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.45rem;
}

@media (max-width: 640px) {
  .member-side {
    align-items: flex-start;
  }
}
</style>
