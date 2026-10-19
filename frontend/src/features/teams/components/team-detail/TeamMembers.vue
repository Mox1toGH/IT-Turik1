<template>
  <ui-card :status="props.status" :error-code="props.errorCode">
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
              <div v-for="i in 2" :key="i" class="member-row member-row--skeleton">
                <div style="display: flex; flex-direction: column; gap: 4px; flex: 1">
                  <div style="display: flex; justify-content: space-between; gap: 10px">
                    <ui-skeleton variant="rect" width="100%" />
                    <ui-skeleton variant="rect" width="100px" />
                  </div>

                  <ui-skeleton variant="rect" width="200px" />
                </div>
              </div>
            </div>
          </template>

          <div class="member-list">
            <div
              class="member-row"
              v-for="member in filteredMembers"
              :key="`member-${member.id}`"
            >
              <user-avatar
                :avatar="member.avatar"
                :username="member.username"
                :full-name="member.full_name || ''"
                :size="42"
              />

              <div class="member-main">
                <div class="member-top">
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
import UiBadge from '@/components/ui/UiBadge'
import UiCard from '@/components/ui/UiCard'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import type { CardErrorCode, CardStatus } from '@/composables/useCardState'
import { computed } from 'vue'
import type { TeamResponse, UserResponse } from '@/api/backendAPINinja.schemas'

interface Props {
  team?: TeamResponse
  user?: UserResponse
  loading: boolean
  status: CardStatus
  errorCode: CardErrorCode
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
</script>

<style scoped>
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
  gap: 0;
}

.member-row {
  display: flex;
  gap: 0.7rem;
  align-items: center;
  padding: 0.7rem 0;
}

.member-row + .member-row {
  border-top: 1px solid var(--border);
}

.member-row--skeleton {
  border-top: 0;
}

.member-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.member-name,
.member-email {
  margin: 0;
}

.member-name {
  font-weight: 700;
  min-width: 0;
  overflow-wrap: anywhere;
}

.member-main {
  flex: 1;
  min-width: 0;
}

.member-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 700;
}

.member-link:hover {
  text-decoration: underline;
  text-underline-offset: 2px;
}

.member-email {
  font-size: 0.84rem;
  overflow-wrap: anywhere;
}
</style>
