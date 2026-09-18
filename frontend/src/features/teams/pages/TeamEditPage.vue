<template>
  <section class="page-shell teams-edit-page">
    <header class="edit-hero">
      <div class="edit-hero-copy">
        <div class="breadcrumb-label">
          <span>Workspace</span>
          <span aria-hidden="true">/</span>
          <span>Teams</span>
          <span aria-hidden="true">/</span>
          <span>Edit</span>
        </div>

        <ui-skeleton-loader :loading="isLoadingTeamInfo">
          <template #skeleton>
            <ui-skeleton variant="rect" height="48px" width="320px" />
          </template>

          <h1 :title="team?.name">Edit {{ truncateText(team?.name ?? 'team', 45) }}</h1>
        </ui-skeleton-loader>

        <p class="section-subtitle">
          Update team identity, contact channels, and member access from one workspace.
        </p>
      </div>

      <div class="hero-actions">
        <ui-skeleton-loader :loading="isLoadingTeamInfo">
          <template #skeleton>
            <ui-skeleton variant="rect" width="148px" height="45px" />
          </template>

          <ui-card variant="stat" class="edit-stat-card">
            <strong>{{ team?.members.length ?? 0 }}</strong>
            <span>Members</span>
          </ui-card>
        </ui-skeleton-loader>

        <ui-skeleton-loader :loading="isLoadingTeamInfo">
          <template #skeleton>
            <ui-skeleton variant="rect" width="148px" height="45px" />
          </template>

          <ui-card variant="stat" class="edit-stat-card">
            <span>Visibility:</span>
            <strong>{{ team?.is_public ? 'Public' : 'Private' }}</strong>
          </ui-card>
        </ui-skeleton-loader>

        <ui-button
          asLink
          variant="secondary"
          size="lg"
          class="back-btn"
          :to="team ? `/teams/${team.id}` : '/teams'"
          >Back to team</ui-button
        >
      </div>
    </header>

    <div class="teams-rule" aria-hidden="true"></div>

    <div class="workspace-grid" v-if="team">
      <team-edit-form :is-error="isError" :loading="isLoadingTeamInfo" :team="team" />

      <team-manage-members :is-error="isError" :loading="isLoadingTeamInfo" :team="team" />
    </div>
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { computed, watchEffect } from 'vue'
import TeamEditForm from '../components/team-edit/TeamEditForm.vue'
import { useRoute, useRouter } from 'vue-router'
import TeamManageMembers from '../components/team-edit/TeamManageMembers.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import { truncateText } from '@/lib/utils'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useGetTeam } from '@/api/teams/teams'

const route = useRoute()
const router = useRouter()

const { data: user } = useGetUserProfile()

const teamId = computed(() => Number(route.params.id))
const { data: team, isLoading: isLoadingTeamInfo, isError } = useGetTeam(teamId.value)

watchEffect(() => {
  if (user.value && team.value) {
    if (team.value.captain_id !== user.value.id) {
      router.push('/')
    }
  }
})
</script>

<style scoped>
.teams-edit-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.edit-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.edit-hero-copy {
  min-width: 0;
}

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--accent-strong);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.edit-hero h1 {
  margin: 0;
  max-width: 760px;
  overflow: hidden;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-weight: 800;
  text-overflow: ellipsis;
}

.section-subtitle {
  max-width: 680px;
  margin: 0.55rem 0 0;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
}

.edit-stat-card {
  display: flex;
}

.edit-stat-card strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  line-height: var(--text-2xl--line-height);
  font-weight: 800;
}

.edit-stat-card span {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
  white-space: nowrap;
}

.teams-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.back-btn {
  width: max-content;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 1.08fr 0.92fr;
  gap: 1rem;
  align-items: start;
}

@media (max-width: 980px) {
  .workspace-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .teams-edit-page {
    padding: 1rem 1rem 2rem;
  }

  .edit-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .edit-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
  }
}
</style>
