<template>
  <section class="page-shell teams-detail-page">
    <ui-card class="hero-card" :class="{ 'hero-card--with-banner': Boolean(team?.banner) }">
      <button
        v-if="isCaptain && !isInfoLoading"
        class="banner-edit-btn"
        type="button"
        @click="isBannerModalOpen = true"
        aria-label="Edit team banner"
      >
        <avatar-edit-icon />
      </button>
      <div v-if="team?.banner" class="hero-banner" :style="heroBannerStyle" />
      <div v-if="team?.banner" class="hero-overlay" />

      <template #header>
        <div class="hero-top hero-content">
          <div>
            <p class="section-eyebrow">Team workspace</p>
            <ui-skeleton-loader class="section-title" :loading="isInfoLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" height="30px" width="200px" />
              </template>

              <h1 class="section-title" :title="team?.name">
                {{ truncateText(team?.name ?? 'Team details', 45) }}
              </h1>
            </ui-skeleton-loader>
          </div>

          <div class="hero-contacts">
            <ui-skeleton-loader :loading="isInfoLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" width="100px" />
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
                <ui-skeleton variant="rect" width="100px" />
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
      </template>

      <template #footer>
        <div class="hero-actions hero-content">
          <ui-button asLink variant="secondary" size="sm" to="/teams">Back to teams</ui-button>
        </div>
      </template>
    </ui-card>

    <ui-card v-if="activeTournament">
      <template #header>
        <p class="section-eyebrow">Active tournament</p>
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

      <ui-card class="panel">
        <div style="display: flex; flex-direction: column; gap: 20px">
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
        <input type="file" accept="image/*" @change="onBannerChange" />
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
import { useGetTeam, useDeleteTeamBanner, useUpdateTeamBanner } from '@/api/teams/teams'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useGetTeamActiveTournament } from '@/api/tournaments/tournaments'

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
const selectedBanner = ref<File | null>(null)
const selectedBannerUrl = ref('')
const bannerPositionX = ref(50)
const bannerPositionY = ref(50)
const { showNotification } = useNotification()

const { mutate: updateBanner, isPending: isUpdatingBanner } = useUpdateTeamBanner()
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
  selectedBanner.value = null
  const saved = readImagePosition(bannerPositionKey.value)
  bannerPositionX.value = saved.x
  bannerPositionY.value = saved.y
  if (selectedBannerUrl.value) {
    URL.revokeObjectURL(selectedBannerUrl.value)
    selectedBannerUrl.value = ''
  }
  closeBannerModal()
}

const onBannerChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  selectedBanner.value = target.files?.[0] || null
}

const saveBanner = () => {
  if (!selectedBanner.value) return
  writeImagePosition(bannerPositionKey.value, {
    x: bannerPositionX.value,
    y: bannerPositionY.value,
  })
  updateBanner(
    { id: teamId, data: { banner: selectedBanner.value } },
    {
      onSuccess: () => {
        showNotification('Banner updated.', 'success')
        resetBannerState()
      },
      onError: () => {
        showNotification('Failed to update banner.', 'error')
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
      onError: () => {
        showNotification('Failed to remove banner.', 'error')
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

watch(selectedBanner, (file) => {
  if (selectedBannerUrl.value) {
    URL.revokeObjectURL(selectedBannerUrl.value)
    selectedBannerUrl.value = ''
  }
  if (file) {
    selectedBannerUrl.value = URL.createObjectURL(file)
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
.hero-card {
  position: relative;
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 2;
}

.hero-card--with-banner :deep(.ui-card-body),
.hero-card--with-banner :deep(.ui-card-header),
.hero-card--with-banner :deep(.ui-card-footer) {
  color: #fff;
}

.hero-card--with-banner .section-eyebrow {
  color: #f8d7b6;
}

.hero-card--with-banner .contact-icon {
  color: #fff;
}

.hero-banner {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  z-index: 0;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  z-index: 1;
  background: linear-gradient(135deg, rgba(5, 11, 23, 0.8), rgba(5, 11, 23, 0.45));
}

.banner-edit-btn {
  position: absolute;
  bottom: 0.9rem;
  right: 0.9rem;
  z-index: 3;
  width: 2.1rem;
  height: 2.1rem;
  border-radius: 999px;
  border: 1px solid var(--line-soft);
  background: #ffffff;
  color: var(--color-gray-700);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.banner-edit-btn:hover {
  border-color: var(--brand-500);
  color: var(--brand-700);
}

.hero-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.hero-contacts {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  justify-items: end;
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
}

.hero-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.active-tournament {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.active-tournament-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
  padding: 0 2rem;
  border-left: 2px solid var(--border);
  border-top: none;
  border-bottom: none;
}

.active-tournament-info:last-child {
  border-right: 2px solid var(--border);
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

.panel {
  border: 1px solid var(--line-soft);
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
  .hero-contacts {
    justify-items: start;
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
  }

  .active-tournament-info {
    padding: 0.75rem 0;
    border-left: none;
    border-right: none !important;
    border-top: none;
    border-bottom: 2px solid var(--border);
  }
}
</style>
