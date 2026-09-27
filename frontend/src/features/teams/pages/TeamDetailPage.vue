<template>
  <section class="page-shell teams-detail-page">
    <header class="team-detail-hero">
      <div class="team-detail-copy">
        <div class="breadcrumb-label">
          <span>Workspace</span>
          <span aria-hidden="true">/</span>
          <span>Teams</span>
          <span aria-hidden="true">/</span>
          <span>Details</span>
        </div>

        <ui-skeleton-loader :loading="isInfoLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" height="48px" width="320px" />
          </template>

          <h1 :title="team?.name">
            {{ truncateText(team?.name ?? 'Team details', 45) }}
          </h1>
        </ui-skeleton-loader>

        <div class="hero-contacts">
          <ui-skeleton-loader :loading="isInfoLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="120px" />
            </template>
            <a
              v-if="team?.contact_telegram"
              :href="telegramLink(team.contact_telegram)"
              class="contact-pill"
            >
              <telegram-icon class="contact-icon" />
              <ui-badge>@{{ team?.contact_telegram }}</ui-badge>
            </a>
            <span v-else class="contact-pill muted">No Telegram</span>
          </ui-skeleton-loader>

          <ui-skeleton-loader :loading="isInfoLoading">
            <template #skeleton>
              <ui-skeleton variant="rect" width="120px" />
            </template>
            <a
              v-if="team?.contact_discord"
              class="contact-pill"
              :href="discordLink(team.contact_discord)"
            >
              <discord-icon class="contact-icon" />
              <ui-badge>{{ team.contact_discord }}</ui-badge>
            </a>

            <span v-else class="contact-pill muted">No Discord</span>
          </ui-skeleton-loader>
        </div>
      </div>

      <div class="hero-actions">
        <ui-skeleton-loader :loading="isInfoLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="148px" height="45px" />
          </template>

          <ui-card variant="stat" class="detail-stat-card">
            <strong class="text-xl">{{ team?.members.length ?? 0 }}</strong>
            <span class="text-sm">Members</span>
          </ui-card>
        </ui-skeleton-loader>

        <ui-skeleton-loader :loading="isInfoLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="148px" height="45px" />
          </template>

          <ui-card variant="stat" class="detail-stat-card">
            <span class="text-sm">Visibility:</span>
            <strong class="text-xl">{{ team?.is_public ? 'Public' : 'Private' }}</strong>
          </ui-card>
        </ui-skeleton-loader>

        <ui-button asLink variant="secondary" size="lg" to="/teams">Back to teams</ui-button>
      </div>
    </header>

    <div class="teams-rule" aria-hidden="true"></div>

    <section
      v-if="team?.banner || (isCaptain && !isInfoLoading)"
      class="team-banner-panel"
      :class="{ 'team-banner-panel--empty': !team?.banner }"
    >
      <div v-if="team?.banner" class="hero-banner" :style="heroBannerStyle" />
      <button
        v-if="isCaptain && !isInfoLoading"
        class="banner-edit-overlay"
        type="button"
        @click="isBannerModalOpen = true"
      >
        <avatar-edit-icon />
        {{ team?.banner ? 'Edit banner' : 'Add banner' }}
      </button>
    </section>

    <ui-card v-if="activeTournament" class="active-tournament-card">
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
          <p :title="activeTournament.name">
            {{ truncateText(activeTournament.name, 20) }}
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

    <div class="workspace-grid">
      <team-base-info
        :team="team"
        :loading="isInfoLoading"
        :loading-error="isInfoLoadingError"
        :is-captain="isCaptain"
        @deleted="router.push('/teams')"
        @leave="router.push('/teams')"
      />

      <ui-card class="panel members-panel">
        <div class="members-workspace">
          <div class="panel-header">
            <span class="step-marker">02</span>
            <div>
              <h2>Members</h2>
              <p class="text-muted">Search accepted members, requests, and invitations.</p>
            </div>
          </div>

          <ui-input
            v-model="searchInput"
            placeholder="Search by username or email"
            :disabled="isInfoLoading || isInfoLoadingError"
          />

          <team-members
            :team="team"
            :user="user"
            :search-filter="searchInput"
            :loading-error="isInfoLoadingError"
            :loading="isInfoLoading || isProfileLoading"
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
      </ui-card>
    </div>

    <ui-skeleton-loader :loading="isInfoLoading">
      <team-manage-zone
        :team="team"
        :loading="isInfoLoading"
        :is-captain="isCaptain"
        @update-team="(newTeamValue) => (team = newTeamValue)"
      />
    </ui-skeleton-loader>

    <ui-modal v-model="isBannerModalOpen" @close="resetBannerState">
      <template #title>
        <h3>Team banner</h3>
      </template>

      <div class="banner-modal-body">
        <div
          v-if="bannerPreviewUrl"
          class="banner-preview-frame"
          @pointerdown="onBannerPreviewPointerDown"
        >
          <img
            :src="bannerPreviewUrl"
            alt="Team banner preview"
            class="banner-preview"
            :style="{ objectPosition: bannerObjectPosition }"
          />
        </div>
        <div v-else class="banner-empty">No banner</div>

        <p v-if="bannerPreviewUrl" class="position-hint">Drag image to choose banner position</p>
        <ui-file-drop v-model="selectedBanner" accept="image/*" />
      </div>

      <template #footer>
        <ui-button size="sm" variant="secondary" @click="resetBannerState">Cancel</ui-button>
        <ui-button
          size="sm"
          variant="secondary"
          :disabled="isBannerUpdating || !team?.banner"
          @click="removeBanner"
        >
          Remove
        </ui-button>
        <ui-button size="sm" :disabled="isBannerUpdating || !selectedBanner" @click="saveBanner">
          <loading-icon v-if="isBannerUpdating" />
          Save
        </ui-button>
      </template>
    </ui-modal>
  </section>
</template>

<script setup lang="ts">
import AvatarEditIcon from '@/icons/AvatarEditIcon.vue'
import DiscordIcon from '@/icons/DiscordIcon.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import TelegramIcon from '@/icons/TelegramIcon.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import TeamBaseInfo from '../components/team-detail/TeamBaseInfo.vue'
import TeamMembers from '../components/team-detail/TeamMembers.vue'
import TeamManageZone from '../components/team-detail/TeamManageZone.vue'
import TeamJoinRequests from '../components/team-detail/TeamJoinRequests.vue'
import TeamInvitations from '../components/team-detail/TeamInvitations.vue'
import { useRoute, useRouter } from 'vue-router'
import { computed, ref, watch } from 'vue'
import { discordLink, telegramLink } from '../lib/team-links'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import { truncateText } from '@/lib/utils'
import { formatDate } from '@/lib/date'
import { useNotification } from '@/composables/useNotification'
import {
  clearImagePosition,
  readImagePosition,
  toObjectPosition,
  writeImagePosition,
} from '@/lib/imagePosition'
import { useGetTeam, useDeleteTeamBanner, useTeamBannerUpdate } from '@/api/teams/teams'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useGetTeamActiveTournament } from '@/api/tournaments/tournaments'
import UiFileDrop from '@/components/ui/UiFileDrop.vue'

const router = useRouter()
const route = useRoute()
const teamId = Number(route.params.id)

const searchInput = ref('')
const { data: user, isLoading: isProfileLoading } = useGetUserProfile()
const {
  data: team,
  isLoading: isInfoLoading,
  isLoadingError: isInfoLoadingError,
} = useGetTeam(teamId)

const { data: activeTournament } = useGetTeamActiveTournament(
  { team_id: teamId },
  {
    query: { enabled: team.value?.is_in_active_tournament },
  },
)

const isCaptain = computed(() => team.value?.captain_id === user.value?.id)
const isBannerModalOpen = ref(false)
const selectedBanner = ref<File[]>([])
const selectedBannerUrl = ref('')
const bannerPositionX = ref(50)
const bannerPositionY = ref(50)
const { showNotification } = useNotification()

const { mutate: updateBanner, isPending: isUpdatingBanner } = useTeamBannerUpdate()
const { mutate: removeTeamBanner, isPending: isRemovingBanner } = useDeleteTeamBanner()
const isBannerUpdating = computed(() => isUpdatingBanner.value || isRemovingBanner.value)

const bannerPreviewUrl = computed(() => {
  if (selectedBannerUrl.value) return selectedBannerUrl.value
  return team.value?.banner || ''
})
const bannerPositionKey = computed(() => `image-position:banner:team:${teamId}`)
const bannerObjectPosition = computed(() =>
  toObjectPosition({ x: bannerPositionX.value, y: bannerPositionY.value }),
)

const heroBannerStyle = computed(() => {
  if (!team.value?.banner) return {}
  return {
    backgroundImage: `url(${team.value.banner})`,
    backgroundPosition: bannerObjectPosition.value,
  }
})

const closeBannerModal = () => {
  isBannerModalOpen.value = false
}

const resetBannerState = () => {
  selectedBanner.value = []
  const saved = readImagePosition(bannerPositionKey.value)
  bannerPositionX.value = saved.x
  bannerPositionY.value = saved.y
  if (selectedBannerUrl.value) {
    URL.revokeObjectURL(selectedBannerUrl.value)
    selectedBannerUrl.value = ''
  }
  closeBannerModal()
}

const saveBanner = () => {
  if (!selectedBanner.value) return
  writeImagePosition(bannerPositionKey.value, {
    x: bannerPositionX.value,
    y: bannerPositionY.value,
  })
  updateBanner(
    { id: teamId, data: { banner: selectedBanner.value[0] } },
    {
      onSuccess: () => {
        showNotification('Banner updated.', 'success')
        resetBannerState()
      },
      onError: (error) => {
        showNotification(error.message, 'error')
      },
    },
  )
}

const removeBanner = () => {
  removeTeamBanner(
    { id: teamId },
    {
      onSuccess: () => {
        clearImagePosition(bannerPositionKey.value)
        showNotification('Banner removed.', 'success')
        resetBannerState()
      },
      onError: (error) => {
        showNotification(error.message, 'error')
      },
    },
  )
}

const onBannerPreviewPointerDown = (event: PointerEvent) => {
  const target = event.currentTarget as HTMLElement | null
  if (!target) return
  target.setPointerCapture(event.pointerId)

  const applyPositionFromPointer = (pointerEvent: PointerEvent) => {
    const rect = target.getBoundingClientRect()
    if (!rect.width || !rect.height) return
    bannerPositionX.value = ((pointerEvent.clientX - rect.left) / rect.width) * 100
    bannerPositionY.value = ((pointerEvent.clientY - rect.top) / rect.height) * 100
  }

  applyPositionFromPointer(event)

  const handleMove = (pointerEvent: PointerEvent) => applyPositionFromPointer(pointerEvent)
  const handleUp = (pointerEvent: PointerEvent) => {
    applyPositionFromPointer(pointerEvent)
    writeImagePosition(bannerPositionKey.value, {
      x: bannerPositionX.value,
      y: bannerPositionY.value,
    })
    target.removeEventListener('pointermove', handleMove)
    target.removeEventListener('pointerup', handleUp)
    target.removeEventListener('pointercancel', handleUp)
  }

  target.addEventListener('pointermove', handleMove)
  target.addEventListener('pointerup', handleUp)
  target.addEventListener('pointercancel', handleUp)
}

watch(selectedBanner, (files) => {
  const firstFile = files[0]

  if (selectedBannerUrl.value) {
    URL.revokeObjectURL(selectedBannerUrl.value)
    selectedBannerUrl.value = ''
  }
  if (firstFile) {
    selectedBannerUrl.value = URL.createObjectURL(firstFile)
  }
})

watch(
  bannerPositionKey,
  (key) => {
    const saved = readImagePosition(key)
    bannerPositionX.value = saved.x
    bannerPositionY.value = saved.y
  },
  { immediate: true },
)
</script>

<style scoped>
.teams-detail-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.team-detail-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.team-detail-copy {
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

.team-detail-hero h1 {
  margin: 0;
  max-width: 760px;
  overflow: hidden;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
  text-overflow: ellipsis;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
}

.detail-stat-card strong {
  font-weight: 800;
}

.detail-stat-card span {
  color: var(--muted-foreground);
  font-weight: 700;
  white-space: nowrap;
}

.teams-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.team-banner-panel {
  position: relative;
  min-height: 220px;
  overflow: hidden;
  border: 1px solid var(--line-soft);
  border-radius: 20px;
  background: var(--card);
}

.team-banner-panel--empty {
  display: flex;
  min-height: 150px;
  align-items: center;
  justify-content: center;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--primary) 10%, transparent), transparent 44%),
    var(--card);
}

.hero-banner {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  z-index: 0;
}

.banner-edit-overlay {
  position: absolute;
  right: 1rem;
  bottom: 1rem;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-height: 40px;
  padding: 0.55rem 0.8rem;
  border: 1px solid var(--line-soft);
  border-radius: 999px;
  background: color-mix(in srgb, var(--card) 92%, transparent);
  color: var(--foreground);
  font-weight: 800;
  cursor: pointer;
  backdrop-filter: blur(12px);
}

.hero-contacts {
  display: flex;
  gap: 0.7rem;
  flex-wrap: wrap;
  margin-top: 0.8rem;
}

.contact-icon {
  width: 1.3rem;
  height: 1.3rem;
  color: var(--brand-700);
}

.contact-pill {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--foreground);
  text-decoration: none;
}

.muted {
  color: var(--muted-foreground);
}

.active-tournament-card.card {
  gap: 1rem;
  border-color: var(--line-soft);
  border-radius: 18px;
}

.active-tournament {
  display: flex;
  align-items: center;
  border-radius: 12px;
  overflow: hidden;
}

.active-tournament-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
  height: 100%;
  padding: 0.95rem 1.1rem;
  background: color-mix(in srgb, var(--card) 92%, var(--foreground) 8%);
}

.active-tournament-info:not(:last-child) {
  border-right: 1px solid var(--line-soft);
}

.active-tournament-badge,
.active-tournament-link {
  width: max-content;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 0.95fr 1.25fr;
  gap: 1rem;
}

.panel.card {
  border: 1px solid var(--line-soft);
  border-radius: 18px;
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
  border-radius: 0.6rem;
  border: 1px solid var(--line-soft);
}

.banner-preview-frame {
  overflow: hidden;
  cursor: move;
}

.position-hint {
  margin: 0;
  color: var(--color-gray-500);
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
  color: var(--color-gray-500);
  font-size: 0.85rem;
}

@media (max-width: 720px) {
  .teams-detail-page {
    padding: 1rem 1rem 2rem;
  }

  .team-detail-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .team-detail-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
  }

  .workspace-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .member-side {
    align-items: flex-start;
  }

  .status-tags {
    justify-content: flex-start;
  }

  .active-tournament {
    flex-direction: column;
    align-items: stretch;
    border: 0;
    border-radius: 0;
    overflow: visible;
  }

  .active-tournament-info {
    padding: 0.85rem;
    border: 1px solid var(--line-soft);
    border-radius: 12px;
  }
}
</style>
