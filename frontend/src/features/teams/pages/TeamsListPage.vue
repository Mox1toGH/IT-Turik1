<template>
  <section class="teams-page page-shell">
    <header class="teams-hero">
      <div class="teams-hero-copy">
        <div class="breadcrumb-label">
          <span>Workspace</span>
          <span aria-hidden="true">/</span>
          <span>Teams</span>
        </div>

        <h1 class="text-6xl">Team directory</h1>
        <p class="section-subtitle text-xl">
          Open a team workspace to view details, edit info, and manage members.
        </p>
      </div>

      <div class="hero-actions">
        <ui-skeleton-loader :loading="isLoadingTeams">
          <template #skeleton>
            <ui-skeleton variant="rect" width="148px" height="64px" />
          </template>

          <ui-card variant="stat" class="teams-stat-card">
            <span class="text-sm">Total teams:</span>
            <strong class="text-xl">{{ teams?.length ?? 0 }}</strong>
          </ui-card>
        </ui-skeleton-loader>

        <ui-button v-if="user?.role === 'team'" asLink to="/teams/create" size="lg">
          <span class="create-plus text-2xl" aria-hidden="true">+</span>
          Create team
        </ui-button>
      </div>
    </header>

    <div class="teams-rule" aria-hidden="true"></div>

    <team-invatations />

    <team-my-teams />

    <teams-other-teams id="other-teams" />
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import TeamInvatations from '../components/teams-list/TeamInvatations.vue'
import TeamMyTeams from '../components/teams-list/TeamMyTeams.vue'
import TeamsOtherTeams from '../components/teams-list/TeamsOtherTeams.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { useListTeams } from '@/api/teams/teams'
import { useGetUserProfile } from '@/api/accounts/accounts'

const { data: teams, isLoading: isLoadingTeams } = useListTeams()
const { data: user } = useGetUserProfile()
</script>

<style scoped>
.teams-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.teams-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.teams-hero-copy {
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

.teams-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.teams-hero .section-subtitle {
  margin: 0.45rem 0 0;
  max-width: 780px;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
}

.teams-stat-card {
  display: flex;
}

.teams-stat-card strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}

.teams-stat-card span {
  color: var(--muted-foreground);
  font-weight: 700;
  white-space: nowrap;
}

.create-plus {
  font-weight: 800;
  line-height: 1;
}

.teams-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

@media (max-width: 760px) {
  .teams-page {
    padding: 1rem 1rem 2rem;
  }

  .teams-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .teams-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .teams-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
  }
}
</style>
