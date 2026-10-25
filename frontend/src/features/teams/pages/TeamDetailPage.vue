<template>
  <section class="page-shell teams-detail-page">
    <team-header :team="team" :loading="isInfoLoading" />

    <div class="teams-rule" aria-hidden="true"></div>

    <ui-tabs :items="tabItems" query-key="tab">
      <template #overview>
        <div class="overview-grid">
          <team-base-info
            :team="team"
            :query="teamQuery"
            :is-captain="isCaptain"
            @deleted="router.push('/teams')"
            @leave="router.push('/teams')"
          />

          <team-banner-section
            :team="team"
            :query="teamQuery"
            :is-captain="isCaptain"
            :hero-banner-style="banner.heroBannerStyle.value"
            @open="banner.isBannerModalOpen.value = true"
          />
        </div>
      </template>

      <template #members>
        <ui-section
          title="Members"
          description="Search accepted members, requests, and invitations."
        >
          <div class="members-workspace">
            <ui-input
              v-model="searchInput"
              placeholder="Search by username or email"
              :disabled="isInfoLoading"
            />

            <team-members
              :team="team"
              :user="user"
              :members="members"
              :query="membersQuery"
              :search-filter="searchInput"
              :is-captain="isCaptain"
            />

            <template v-if="isCaptain && !isInfoLoading">
              <team-join-requests
                :team-id="teamId"
                :search-filter="searchInput"
                :is-captain="isCaptain"
              />
              <team-invitations
                :team-id="teamId"
                :search-filter="searchInput"
                :is-captain="isCaptain"
              />
            </template>
          </div>
        </ui-section>
      </template>

      <template v-if="activeTournament" #tournaments>
        <ui-card class="active-tournament-card">
          <template #header>
            <div class="panel-header">
              <span class="step-marker">Live</span>
              <div>
                <p class="section-eyebrow">Active tournament</p>
                <h2>Tournament dashboard</h2>
              </div>
            </div>
          </template>

          <div class="active-tournament">
            <div class="active-tournament-info">
              <p class="text-muted">Tournament name:</p>
              <p class="active-tournament-name">
                <ui-truncate :text="activeTournament.name" />
              </p>
            </div>

            <div class="active-tournament-info">
              <p class="text-muted">Start date:</p>
              <p>{{ formatDate(activeTournament.start_date, { showHours: true }) }}</p>
            </div>

            <div class="active-tournament-info">
              <p class="text-muted">Status:</p>
              <ui-badge variant="primary" class="active-tournament-badge">{{
                activeTournament.status
              }}</ui-badge>
            </div>
          </div>

          <template #footer>
            <ui-button
              asLink
              size="sm"
              class="active-tournament-link"
              :to="`/tournaments/${activeTournament.id}`"
              >Go to tournament dashboard</ui-button
            >
          </template>
        </ui-card>
      </template>

      <template v-if="isCaptain" #settings>
        <ui-query-block :query="teamQuery">
          <ui-query-field>
            <template #skeleton>
              <ui-skeleton variant="rect" width="100%" height="72px" />
            </template>
            <team-manage-zone
              :team="team"
              :loading="isInfoLoading"
              :is-captain="isCaptain"
              @update-team="(newTeamValue) => (team = newTeamValue)"
            />
          </ui-query-field>
        </ui-query-block>
      </template>
    </ui-tabs>

    <ui-modal v-model="banner.isBannerModalOpen.value" @close="banner.resetBannerState">
      <template #title>
        <h3>Team banner</h3>
      </template>

      <div class="banner-modal-body">
        <div
          v-if="banner.bannerPreviewUrl.value"
          class="banner-preview-frame"
          @pointerdown="banner.onBannerPreviewPointerDown"
        >
          <img
            :src="banner.bannerPreviewUrl.value"
            alt="Team banner preview"
            class="banner-preview"
            :style="{ objectPosition: banner.bannerObjectPosition.value }"
          />
        </div>
        <div v-else class="banner-empty">No banner</div>

        <p v-if="banner.bannerPreviewUrl.value" class="position-hint">
          Drag image to choose banner position
        </p>
        <ui-file-drop v-model="banner.selectedBanner.value" accept="image/*" />
      </div>

      <template #footer>
        <ui-button size="sm" variant="secondary" @click="banner.resetBannerState">Cancel</ui-button>
        <ui-button
          size="sm"
          variant="secondary"
          :disabled="banner.isBannerUpdating.value || !team?.banner"
          @click="isBannerRemoveConfirmOpen = true"
        >
          Remove
        </ui-button>
        <ui-button
          size="sm"
          :disabled="banner.isBannerUpdating.value || !banner.selectedBanner.value.length"
          @click="banner.saveBanner"
        >
          <LoaderCircle class="animate-spin" v-if="banner.isBannerUpdating.value" />
          Save
        </ui-button>
      </template>
    </ui-modal>
    <ui-confirm-modal
      v-model="isBannerRemoveConfirmOpen"
      title="Remove team banner?"
      confirm-text="Remove banner"
      confirm-variant="danger"
      :loading="banner.isBannerUpdating.value"
      @confirm="confirmRemoveTeamBanner"
    >
      <template #message>
        <p>The current <ui-badge variant="red">team banner</ui-badge> will be removed.</p>
      </template>
    </ui-confirm-modal>
  </section>
</template>

<script setup lang="ts">
import { LoaderCircle } from 'lucide-vue-next'
import UiModal from '@/components/ui/UiModal'
import UiConfirmModal from '@/components/ui/UiConfirmModal'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import { UiQueryBlock } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiSection from '@/components/ui/UiSection'
import UiTabs, { type TabItem } from '@/components/ui/UiTabs'
import UiTruncate from '@/components/ui/UiTruncate'
import TeamHeader from '../components/team-detail/TeamHeader.vue'
import TeamBannerSection from '../components/team-detail/TeamBannerSection.vue'
import TeamBaseInfo from '../components/team-detail/TeamBaseInfo.vue'
import TeamMembers from '../components/team-detail/TeamMembers.vue'
import TeamManageZone from '../components/team-detail/TeamManageZone.vue'
import TeamJoinRequests from '../components/team-detail/TeamJoinRequests.vue'
import TeamInvitations from '../components/team-detail/TeamInvitations.vue'
import { useTeamBanner } from '../composables/useTeamBanner'
import { useRoute, useRouter } from 'vue-router'
import { computed, ref } from 'vue'
import UiBadge from '@/components/ui/UiBadge'
import UiInput from '@/components/ui/UiInput'
import { formatDate } from '@/lib/date'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useGetTeam, useListTeamMembers } from '@/api/teams/teams'
import { useGetTeamActiveTournament } from '@/api/tournaments/tournaments'
import UiFileDrop from '@/components/ui/UiFileDrop'

const router = useRouter()
const route = useRoute()
const teamId = Number(route.params.id)

const searchInput = ref('')
const isBannerRemoveConfirmOpen = ref(false)
const { data: user } = useGetUserProfile()
const teamQuery = useGetTeam(teamId)
const { data: team, isLoading: isInfoLoading } = teamQuery
const membersQuery = useListTeamMembers(teamId, {
  query: { enabled: computed(() => route.query.tab === 'members') },
})
const { data: members } = membersQuery

const { data: activeTournament } = useGetTeamActiveTournament(
  { team_id: teamId },
  {
    query: { enabled: team.value?.is_in_active_tournament },
  },
)

const isCaptain = computed(() => team.value?.captain_id === user.value?.id)

const banner = useTeamBanner(teamId, team)

function confirmRemoveTeamBanner() {
  isBannerRemoveConfirmOpen.value = false
  banner.removeBanner()
}

const tabItems = computed<TabItem[]>(() => {
  const items: TabItem[] = [
    { value: 'overview', label: 'Overview' },
    { value: 'members', label: 'Members' },
  ]
  if (activeTournament.value) items.push({ value: 'tournaments', label: 'Tournaments' })
  if (isCaptain.value) items.push({ value: 'settings', label: 'Settings' })
  return items
})
</script>

<style scoped>
.teams-detail-page {
  grid-template-columns: minmax(0, 1fr);
  min-width: 0;
  gap: 1.4rem;
}

.teams-detail-page > *,
.overview-grid > * {
  min-width: 0;
}

.teams-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--border);
}

.overview-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(260px, 0.85fr);
  gap: 1rem;
  align-items: start;
}

@media (max-width: 900px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
}

.active-tournament-card.card {
  gap: 1rem;
  border-color: var(--border);
}

.active-tournament {
  display: flex;
  align-items: center;
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.active-tournament-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
  height: 100%;
  min-width: 0;
  padding: 0.95rem 1.1rem;
  background: var(--subtle);
}

.active-tournament-info:not(:last-child) {
  border-right: 1px solid var(--border);
}

.active-tournament-name {
  margin: 0;
  min-width: 0;
}

.active-tournament-badge,
.active-tournament-link {
  width: max-content;
}

.members-workspace {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.banner-modal-body {
  display: grid;
  gap: 0.75rem;
}

.banner-preview-frame,
.banner-empty {
  width: 100%;
  max-width: 480px;
  aspect-ratio: 16 / 5;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.banner-preview-frame {
  overflow: hidden;
  cursor: move;
}

.position-hint {
  margin: 0;
  color: var(--muted-foreground);
  font-size: 0.82rem;
}

.banner-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  user-select: none;
  pointer-events: none;
}

.banner-empty {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--muted-foreground);
  font-size: 0.85rem;
}

@media (max-width: 720px) {
  .teams-detail-page {
    padding: 1rem 1rem 2rem;
  }
}

@media (max-width: 640px) {
  .active-tournament {
    flex-direction: column;
    align-items: stretch;
    border: 0;
    border-radius: 0;
    overflow: visible;
  }

  .active-tournament-info {
    padding: 0.85rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
  }
}
</style>
