<template>
  <div class="overview-content">
    <ProfileMiniCard :user="user" :is-loading="isLoading" @edit-profile="openEditProfile" />
    <EditProfileModal ref="editProfileModal" />

    <ui-section
      divider
      title="Your information"
      description="Profile details"
      aria-labelledby="profile-details-title"
    >
      <ui-query-block :query="props.query">
        <div class="details-grid">
          <div v-for="field in profileFields" :key="field.label" class="field-row">
            <span class="field-label">{{ field.label }}</span>
            <ui-query-field>
              <template #skeleton
                ><ui-skeleton variant="rect" width="120px" height="18px"
              /></template>
              <ui-badge v-if="field.label === 'Role'" variant="green">{{ field.value }}</ui-badge>
              <strong v-else class="field-value">{{ field.value }}</strong>
            </ui-query-field>
          </div>
        </div>
      </ui-query-block>
    </ui-section>

    <ui-section v-if="user?.teams?.length" divider title="Your teams" description="Membership">
      <div class="team-list">
        <router-link
          v-for="team in user.teams"
          :key="team.id"
          :to="`/teams/${team.id}`"
          class="team-link"
        >
          <Users :size="28" />
          {{ team.name }}
          <ChevronRight :size="24" />
        </router-link>
      </div>
    </ui-section>

    <ui-section
      v-if="user?.active_tournament"
      divider
      title="Active tournament"
      description="Current event"
    >
      <router-link :to="`/tournaments/${user.active_tournament.id}`" class="tournament-link">
        <span>
          <strong>{{ user.active_tournament.name }}</strong>
          <small>
            {{ formatDate(user.active_tournament.start_date) }} -
            {{ formatDate(user.active_tournament.end_date) }}
          </small>
        </span>
        <ChevronRight :size="24" />
      </router-link>
    </ui-section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiBadge from '@/components/ui/UiBadge'
import UiSection from '@/components/ui/UiSection'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { ChevronRight, Users } from 'lucide-vue-next'
import { formatDate } from '@/lib/date'
import ProfileMiniCard from '../ProfileMiniCard.vue'
import EditProfileModal from '../modals/EditProfile/EditProfileModal.vue'
import type { UserResponse } from '@/api/backendAPINinja.schemas.ts'
import type { QueryLike } from '@/composables/useQueryState'

const props = defineProps<{
  user?: UserResponse
  isLoading?: boolean
  query: QueryLike
}>()

const editProfileModal = ref<InstanceType<typeof EditProfileModal> | null>(null)

const profileFields = computed(() => [
  { label: 'Username', value: props.user?.username || '-' },
  { label: 'Email', value: props.user?.email || '-' },
  { label: 'Full name', value: props.user?.full_name || '-' },
  { label: 'City', value: props.user?.city || '-' },
  { label: 'Phone', value: props.user?.phone || '-' },
  { label: 'Role', value: props.user?.role || '-' },
])

const openEditProfile = () => {
  editProfileModal.value?.open()
}
</script>

<style scoped>
.overview-content {
  display: grid;
  gap: 2.25rem;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.field-row {
  display: grid;
  align-items: center;
  gap: 0.45rem;
  padding: 0.8rem;
  background-color: var(--card);
  border-radius: var(--radius);
}

.field-label {
  color: var(--muted-foreground);
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
}

.field-value {
  overflow-wrap: anywhere;
  color: var(--foreground);
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
  font-weight: 800;
}

.team-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.8rem;
}

.team-link,
.tournament-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  min-width: 0;
  color: var(--foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  text-decoration: none;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--card);
}

.team-link {
  min-height: 54px;
  padding: 0.8rem 1rem;
}

.team-link:hover,
.tournament-link:hover {
  background: var(--hover);
}

.team-link :deep(svg:first-child),
.team-link > :deep(svg:last-child),
.tournament-link > :deep(svg) {
  width: 1rem;
  height: 1rem;
  flex: 0 0 auto;
  color: var(--muted-foreground);
}

.tournament-link {
  padding: 0.85rem 1rem;
}

.tournament-link span {
  display: grid;
  gap: 0.25rem;
}

.tournament-link small {
  color: var(--muted-foreground);
}

@media (max-width: 560px) {
  .team-list {
    grid-template-columns: 1fr;
  }
}
</style>
