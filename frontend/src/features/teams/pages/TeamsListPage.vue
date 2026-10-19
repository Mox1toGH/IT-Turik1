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
        <ui-button v-if="user?.role === 'team'" asLink to="/teams/create" size="lg">
          <span class="create-plus text-2xl" aria-hidden="true">+</span>
          Create team
        </ui-button>
      </div>
    </header>

    <div class="teams-rule" aria-hidden="true"></div>

    <ui-tabs v-model="activeTab" :items="tabItems" query-key="tab">
      <template #my>
        <team-my-teams />
      </template>

      <template #all>
        <teams-other-teams />
      </template>

      <template #invitations>
        <team-invatations @browse-teams="activeTab = 'all'" />
      </template>
    </ui-tabs>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiButton from '@/components/ui/UiButton'
import UiTabs, { type TabItem } from '@/components/ui/UiTabs'
import TeamInvatations from '../components/teams-list/TeamInvatations.vue'
import TeamMyTeams from '../components/teams-list/TeamMyTeams.vue'
import TeamsOtherTeams from '../components/teams-list/TeamsOtherTeams.vue'
import { useGetUserProfile } from '@/api/accounts/accounts.ts'
import { useListTeamInvitations } from '@/api/teams/teams'

const { data: user } = useGetUserProfile()

const activeTab = ref('my')

// The invitations query stays at page level (same key as the tab panel, so no
// extra fetch): the pending count is needed outside the tab for the tab badge.
const { data: inboxInvitations } = useListTeamInvitations()
const pendingCount = computed(
  () => inboxInvitations.value?.items.filter((invitation) => invitation.status === 'invited').length ?? 0,
)

const tabItems = computed<TabItem[]>(() => [
  { value: 'my', label: 'My teams' },
  { value: 'all', label: 'All teams' },
  {
    value: 'invitations',
    label: 'Invitations',
    count: pendingCount.value > 0 ? pendingCount.value : undefined,
  },
])
</script>

<style scoped>
.teams-page {
  gap: 1.4rem;
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
  color: var(--muted-foreground);
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

.create-plus {
  font-weight: 800;
  line-height: 1;
}

.teams-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--border);
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
