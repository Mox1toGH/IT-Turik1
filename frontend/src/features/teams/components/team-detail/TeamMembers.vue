<template>
  <ui-card title="Members">
    <div class="members-sections">
      <section class="members-section">
        <header v-if="props.members" class="section-subhead">
          <span class="text-muted">{{ filteredMembers?.length }} people</span>
        </header>

        <ui-query-block :query="props.query" title="team members">
          <ui-query-field>
            <template #skeleton>
              <div class="member-list">
                <div
                  v-for="i in 2"
                  :key="`member-skeleton-${i}`"
                  class="member-card"
                >
                  <ui-skeleton variant="rounded" width="44px" height="44px" />
                  <div class="member-main">
                    <div class="member-top">
                      <ui-skeleton variant="rect" width="120px" height="24px" />
                      <ui-skeleton variant="rounded" width="64px" height="29px" />
                    </div>
                    <ui-skeleton variant="rect" width="190px" height="20px" />
                  </div>
                </div>
              </div>
            </template>

            <div class="member-list">
              <article
                class="member-card"
                v-for="member in filteredMembers"
                :key="`member-${member.id}`"
              >
                <user-avatar
                  :avatar="member.avatar"
                  :username="member.username"
                  :full-name="member.full_name || ''"
                  :size="44"
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
              </article>

              <p v-if="filteredMembers?.length === 0" class="text-muted">
                No accepted members match your search.
              </p>
            </div>
          </ui-query-field>
        </ui-query-block>
      </section>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge'
import UiCard from '@/components/ui/UiCard'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import type { QueryLike } from '@/composables/useQueryState'
import { computed } from 'vue'
import type { Team } from '@/features/teams/types'

interface Props {
  team?: Team
  members?: Team['members']
  query: QueryLike
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
  props.members?.filter((m) => matches([m.username, m.email, m.full_name])),
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
  gap: 0.75rem;
  padding: 1px;
}

.member-card {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 0.8rem;
  padding: 0.9rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--background);
  transition:
    border-color 0.18s ease,
    background-color 0.18s ease;
}

.member-card:hover {
  border-color: var(--primary);
  background: var(--muted);
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

@media (prefers-reduced-motion: reduce) {
  .member-card {
    transition: none;
  }
}
</style>
