<template>
  <div class="overview-content">
    <ProfileMiniCard :user="user" :is-loading="isLoading" @edit-profile="openEditProfile" />
    <EditProfileModal ref="editProfileModal" />

    <ui-card variant="stat" class="balance-card">
      <template #header>
        <span class="card-label">Points balance:</span>
      </template>
      <ui-skeleton-loader :loading="isPointsLoading">
        <template #skeleton>
          <ui-skeleton variant="rect" width="5rem" />
        </template>
        <p class="balance-value text-xl">{{ pointsBalance?.balance ?? 0 }}</p>
      </ui-skeleton-loader>
    </ui-card>

    <ui-card variant="panel" class="details-section" aria-labelledby="profile-details-title">
      <div>
        <p class="section-eyebrow">Profile details</p>
        <h1 id="profile-details-title" class="text-3xl">Your information</h1>
      </div>

      <div class="details-grid">
        <ui-card v-for="field in profileFields" :key="field.label" class="field-card">
          <span class="field-label">{{ field.label }}</span>
          <ui-skeleton-loader :loading="isLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="80%" />
            </template>
            <ui-badge v-if="field.label === 'Role'" variant="green">{{ field.value }}</ui-badge>
            <strong v-else class="field-value">{{ field.value }}</strong>
          </ui-skeleton-loader>
        </ui-card>
      </div>
    </ui-card>

    <ui-card v-if="user?.teams?.length" variant="panel" class="supporting-section">
      <div class="section-heading compact-heading">
        <div>
          <p class="section-eyebrow">Membership</p>
          <h2 class="text-3xl">Your teams</h2>
        </div>
      </div>
      <div class="team-list">
        <router-link
          v-for="team in user.teams"
          :key="team.id"
          :to="`/teams/${team.id}`"
          class="team-link"
        >
          <TeamIcon />
          {{ team.name }}
          <ArrowRight />
        </router-link>
      </div>
    </ui-card>

    <ui-card v-if="user?.active_tournament" variant="panel" class="supporting-section">
      <div class="section-heading compact-heading">
        <div>
          <p class="section-eyebrow">Current event</p>
          <h2 class="text-3xl">Active tournament</h2>
        </div>
      </div>
      <router-link :to="`/tournaments/${user.active_tournament.id}`" class="tournament-link">
        <span>
          <strong>{{ user.active_tournament.name }}</strong>
          <small>
            {{ formatDate(user.active_tournament.start_date) }} -
            {{ formatDate(user.active_tournament.end_date) }}
          </small>
        </span>
        <ArrowRight />
      </router-link>
    </ui-card>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import ArrowRight from '@/icons/ArrowRight.vue'
import TeamIcon from '@/icons/TeamIcon.vue'
import type { User } from '@/api/.ts.schemas'
import { useGetMyPointsBalance } from '@/api/points/points'
import { formatDate } from '@/lib/date'
import ProfileMiniCard from '../ProfileMiniCard.vue'
import EditProfileModal from '../modals/EditProfile/EditProfileModal.vue'

const props = defineProps<{
  user?: User
  isLoading?: boolean
}>()

const { data: pointsBalance, isLoading: isPointsLoading } = useGetMyPointsBalance()
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
.overview-content,
.details-section,
.supporting-section {
  display: grid;
  gap: 1rem;
}

.balance-card {
  justify-content: flex-start;
  margin-bottom: 0.4rem;
}

.balance-value {
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.details-section h1,
.section-heading h1,
.section-heading h2 {
  margin: 1.2rem 0 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.compact-heading {
  align-items: start;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
}

.field-card {
  min-height: 78px;
  padding: 1rem;
  gap: 0.45rem;
  border-color: var(--line-soft);
  background: var(--background);
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

.field-card :deep(.badge) {
  width: max-content;
  padding: 0.15rem 0.55rem;
  text-transform: uppercase;
}

.team-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
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
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  background: var(--background);
  transition: background 0.2s ease;
}

.team-link {
  min-height: 54px;
  padding: 0.8rem 1rem;
}

.team-link:hover,
.tournament-link:hover {
  background: var(--secondary);
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
  .details-grid,
  .team-list {
    grid-template-columns: 1fr;
  }

  .section-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .edit-details-link {
    align-self: stretch;
  }
}
</style>
