<template>
  <ui-card>
    <ui-query-state :query="props.query" title="team members">
    <div class="members-sections">
      <section class="members-section">
        <header class="section-subhead">
          <h3>Members</h3>
          <span class="text-muted">{{ filteredMembers?.length }} people</span>
        </header>

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
      </section>
    </div>
    </ui-query-state>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge'
import UiCard from '@/components/ui/UiCard'
import UiQueryState from '@/components/ui/UiQueryState'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import type { QueryLike } from '@/composables/useQueryState'
import { computed } from 'vue'
import type { Team } from '@/features/teams/types'

interface Props {
  team?: Team
  query: QueryLike
  loading: boolean
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
