<template>
  <section class="tournament-detail-page page-shell">
    <header
      class="tournament-hero"
      :class="{ 'tournament-hero--with-banner': Boolean(tournament?.banner) }"
    >
      <button
        v-if="user?.role === 'admin'"
        class="banner-edit-btn"
        type="button"
        aria-label="Edit tournament banner"
        @click="isBannerModalOpen = true"
      >
        <avatar-edit-icon />
      </button>
      <div v-if="tournament?.banner" class="hero-banner" :style="heroBannerStyle" />
      <div v-if="tournament?.banner" class="hero-overlay" />

      <div class="hero-content tournament-hero-copy">
        <div class="breadcrumb-label">
          <span>Workspace</span>
          <span aria-hidden="true">/</span>
          <span>Tournament</span>
        </div>

        <h1 class="text-6xl">{{ tournament?.name ?? `Tournament ${id}` }}</h1>
        <p class="section-subtitle text-xl">
          Review tournament information, rounds, teams, and results.
        </p>
      </div>

      <div class="hero-actions hero-content">
        <ui-card variant="stat" class="tournament-stat-card">
          <span class="text-sm">Status:</span>
          <strong class="text-base">{{ tournament?.status ?? 'Loading' }}</strong>
        </ui-card>

        <ui-button asLink to="/tournaments" variant="secondary" size="lg" class="tournament-link">
          Back to tournaments
        </ui-button>
      </div>
    </header>

    <div class="tournament-rule" aria-hidden="true"></div>

    <nav class="sections-card" aria-label="Tournament sections">
      <ui-horizontal-scroll role="tablist" content-class="sections">
        <button
          type="button"
          role="tab"
          :aria-selected="currentSection === 'information'"
          :class="['sections-btn', { active: currentSection === 'information' }]"
          @click="setActiveSection('information')"
        >
          Information
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="currentSection === 'rounds'"
          :class="['sections-btn', { active: currentSection === 'rounds' }]"
          @click="setActiveSection('rounds')"
        >
          Rounds
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="currentSection === 'submissions'"
          :aria-disabled="user?.role !== 'admin' && user?.role !== 'team'"
          :disabled="user?.role !== 'admin' && user?.role !== 'team'"
          :class="['sections-btn', { active: currentSection === 'submissions' }]"
          @click="setActiveSection('submissions')"
        >
          Submissions
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="currentSection === 'schedule'"
          :class="['sections-btn', { active: currentSection === 'schedule' }]"
          @click="setActiveSection('schedule')"
        >
          Schedule
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="currentSection === 'leaderboard'"
          :class="['sections-btn', { active: currentSection === 'leaderboard' }]"
          @click="setActiveSection('leaderboard')"
        >
          Leaderboard
        </button>
      </ui-horizontal-scroll>
    </nav>

    <transition name="fade" mode="out-in">
      <div :key="currentSection">
        <div class="tournament-grid" v-if="currentSection === 'information'">
          <TournamentInfo :tournament-id="id" />
          <TournamentTeams :tournament-id="id" />
        </div>

        <TournamentRounds :tournament-id="id" v-if="currentSection === 'rounds'" />
        <TournamentSchedule
          :tournament-id="id"
          :tournament-status="tournament?.status ?? 'draft'"
          v-if="currentSection === 'schedule'"
        />
        <TournamentLeaderboard :tournament-id="id" v-if="currentSection === 'leaderboard'" />

        <template
          v-if="
            currentSection === 'submissions' && (user?.role === 'admin' || user?.role === 'team')
          "
        >
          <TournamentSubmissions :tournament-id="id" v-if="user?.role === 'team'" />
          <JuryAssign
            :tournament-id="id"
            :tournament-status="tournament?.status ?? 'draft'"
            v-if="user?.role === 'admin'"
          />
        </template>

        <ui-card
          v-if="
            currentSection === 'submissions' &&
            user &&
            user.role !== 'team' &&
            user.role !== 'admin'
          "
        >
          <p>Submissions are available for team members and admins.</p>
        </ui-card>

        <ui-card
          v-if="user?.role === 'admin' && currentSection === 'information'"
          class="manage-zone"
        >
          <div>
            <div class="manage-row">
              <div>
                <h3>Edit tournament</h3>
                <p class="text-muted">Update tournament details in edit workspace.</p>
              </div>
              <ui-button asLink variant="secondary" size="sm" :to="`/tournaments/${id}/edit`">
                Edit tournament
              </ui-button>
            </div>

            <div>
              <div class="danger-zone-header">
                <danger-icon />
                <span>Danger Zone</span>
              </div>

              <div class="danger-zone-box">
                <div class="manage-row danger-zone-row">
                  <div>
                    <h3>Delete tournament</h3>
                    <p class="text-muted">
                      This action permanently deletes the tournament and cannot be undone.
                    </p>
                  </div>

                  <DeleteTournamentModal
                    :tournament-id="id"
                    :tournament-name="tournament?.name ?? `Tournament ${id}`"
                    @deleted="onTournamentDeleted"
                  />
                </div>
              </div>
            </div>
          </div>
        </ui-card>
      </div>
    </transition>

    <ui-modal v-model="isBannerModalOpen" @close="resetBannerState">
      <template #title>
        <h3>Tournament banner</h3>
      </template>

      <div class="banner-modal-body">
        <div
          v-if="bannerPreviewUrl"
          class="banner-preview-frame"
          @pointerdown="onBannerPreviewPointerDown"
        >
          <img
            :src="bannerPreviewUrl"
            alt="Tournament banner preview"
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
          :disabled="isBannerUpdating || !tournament?.banner"
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
import DangerIcon from '@/icons/DangerIcon.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiHorizontalScroll from '@/components/ui/UiHorizontalScroll.vue'
import { useRoute, useRouter } from 'vue-router'
import TournamentInfo from '../components/tournament/TournamentInfo.vue'
import TournamentTeams from '../components/tournament/TournamentTeams.vue'
import { computed, ref, watch } from 'vue'
import TournamentSchedule from '../components/tournament/TournamentSchedule.vue'
import TournamentRounds from '../components/tournament/TournamentRounds.vue'
import JuryAssign from '../components/tournament/tournament-submissions/JuryAssign.vue'
import TournamentSubmissions from '../components/tournament/TournamentSubmissions.vue'
import TournamentLeaderboard from '../components/tournament/TournamentLeaderboard.vue'
import DeleteTournamentModal from '../components/tournament/modals/DeleteTournamentModal.vue'
import { useNotification } from '@/composables/useNotification'
import {
  clearImagePosition,
  readImagePosition,
  toObjectPosition,
  writeImagePosition,
} from '@/lib/imagePosition'
import { useGetUserProfile } from '@/api/accounts/accounts'
import {
  useDeleteTournamentBanner,
  useGetTournament,
  useUpdateTournamentBanner,
} from '@/api/tournaments/tournaments'

type Sections = 'information' | 'schedule' | 'rounds' | 'submissions' | 'leaderboard'

const route = useRoute()
const router = useRouter()
const id = Number(route.params.id)

const { data: user } = useGetUserProfile()
const { data: tournament } = useGetTournament(id)
const { showNotification } = useNotification()
const isBannerModalOpen = ref(false)
const selectedBanner = ref<File | null>(null)
const selectedBannerUrl = ref('')
const bannerPositionX = ref(50)
const bannerPositionY = ref(50)
const { mutate: updateBanner, isPending: isUpdatingBanner } = useUpdateTournamentBanner()
const { mutate: removeTournamentBanner, isPending: isRemovingBanner } = useDeleteTournamentBanner()
const isBannerUpdating = computed(() => isUpdatingBanner.value || isRemovingBanner.value)
const bannerPreviewUrl = computed(() => selectedBannerUrl.value || tournament.value?.banner || '')
const bannerPositionKey = computed(() => `image-position:banner:tournament:${id}`)
const bannerObjectPosition = computed(() =>
  toObjectPosition({ x: bannerPositionX.value, y: bannerPositionY.value }),
)
const heroBannerStyle = computed(() =>
  tournament.value?.banner
    ? {
        backgroundImage: `url(${tournament.value.banner})`,
        backgroundPosition: bannerObjectPosition.value,
      }
    : {},
)

const currentSection = ref<Sections>('information')

const sectionQueryKey = 'section'
const allSections: Sections[] = ['information', 'schedule', 'rounds', 'submissions', 'leaderboard']

function parseSectionFromQuery(value: unknown): Sections | null {
  const raw = Array.isArray(value) ? value[0] : value
  if (typeof raw !== 'string') return null
  return allSections.includes(raw as Sections) ? (raw as Sections) : null
}

const initialSection = parseSectionFromQuery(route.query[sectionQueryKey])
if (initialSection) currentSection.value = initialSection

const setActiveSection = (section: Sections) => {
  currentSection.value = section
}

const onTournamentDeleted = () => {
  showNotification('Tournament deleted successfully.', 'success')
  router.push('/tournaments')
}

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
    { id, data: { banner: selectedBanner.value } },
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
  removeTournamentBanner(
    { id },
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

watch(
  () => route.query[sectionQueryKey],
  (value) => {
    const section = parseSectionFromQuery(value)
    if (section && section !== currentSection.value) currentSection.value = section
  },
)

watch(
  () => currentSection.value,
  (section) => {
    const currentQuerySection = parseSectionFromQuery(route.query[sectionQueryKey])
    if (currentQuerySection === section) return

    void router.replace({
      query: {
        ...route.query,
        [sectionQueryKey]: section,
      },
    })
  },
)
</script>

<style scoped>
.fade-enter-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}

.fade-leave-active {
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.tournament-detail-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.tournament-hero {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
  overflow: hidden;
  min-height: 220px;
  padding: 1.5rem;
  border: 1px solid var(--line-soft);
  border-radius: 20px;
  background: var(--card);
}

.hero-content {
  position: relative;
  z-index: 2;
}

.tournament-hero-copy {
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

.tournament-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.tournament-hero .section-subtitle {
  margin: 0.45rem 0 0;
  max-width: 780px;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.tournament-hero--with-banner h1,
.tournament-hero--with-banner .section-subtitle {
  color: #fff;
}

.tournament-hero--with-banner .breadcrumb-label {
  color: rgba(255, 255, 255, 0.78);
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
  background: linear-gradient(135deg, rgba(5, 11, 23, 0.78), rgba(5, 11, 23, 0.42));
}

.banner-edit-btn {
  position: absolute;
  top: 0.9rem;
  right: 0.9rem;
  z-index: 3;
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 999px;
  border: 1px solid var(--line-soft);
  background: var(--secondary);
  color: var(--secondary-foreground);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.banner-edit-btn:hover {
  border-color: var(--brand-500);
  color: var(--brand-700);
}

.tournament-link {
  width: max-content;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
  gap: 1rem;
}

.tournament-stat-card {
  display: flex;
}

.tournament-stat-card strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
  text-transform: capitalize;
}

.tournament-stat-card span {
  color: var(--muted-foreground);
  font-weight: 700;
  white-space: nowrap;
}

.tournament-hero--with-banner .tournament-stat-card {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.tournament-hero--with-banner .tournament-stat-card strong,
.tournament-hero--with-banner .tournament-stat-card span {
  color: #fff;
}

.tournament-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.sections-card {
  overflow: hidden;
  border: 1px solid var(--line-soft);
  border-radius: 14px;
  background: var(--card);
}

.sections-btn {
  position: relative;
  flex: 0 0 auto;
  min-height: 42px;
  padding: 0.55rem 0.85rem;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: var(--muted-foreground);
  font: inherit;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  white-space: nowrap;
  cursor: pointer;
  transition:
    background 0.18s ease,
    color 0.18s ease,
    box-shadow 0.18s ease;
}

.sections-btn:hover {
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  color: var(--foreground);
}

.sections-btn:focus-visible {
  box-shadow: 0 0 0 2px var(--ring);
}

.sections-btn.active {
  background: var(--primary);
  color: var(--primary-foreground);
  box-shadow: 0 8px 20px color-mix(in srgb, var(--primary) 22%, transparent);
}

.sections-btn:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.sections-btn:disabled:hover {
  background: transparent;
  color: var(--muted-foreground);
}

.tournament-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.7fr);
  gap: 1rem;
  align-items: start;
}

.manage-zone {
  margin-top: 1rem;
  padding: 1.25rem;
  border-color: var(--line-soft);
  background: var(--card);
}

.manage-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.9rem;
}

.manage-row:not(:last-child) {
  margin-bottom: 1rem;
  padding-bottom: 1rem;
}

.manage-row h3 {
  font-size: 1rem;
}

.manage-row p {
  margin-top: 0.3rem;
}

.danger-zone-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.8rem;
  margin: 0.2rem 0 0;
  background: color-mix(in srgb, var(--destructive) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--destructive) 20%, transparent);
  border-radius: 8px;
  color: color-mix(in srgb, var(--destructive) 80%, transparent);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.danger-zone-icon {
  width: 0.95rem;
  height: 0.95rem;
  flex-shrink: 0;
}

.danger-zone-box {
  margin-top: 0.6rem;
  padding: 1rem;
  border: 1px solid color-mix(in srgb, var(--destructive) 20%, transparent);
  border-radius: 10px;
  background: color-mix(in srgb, var(--destructive) 10%, transparent);
}

.danger-zone-row h3 {
  color: color-mix(in srgb, var(--destructive) 80%, transparent);
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

@media (max-width: 810px) {
  .tournament-detail-page {
    padding: 1rem 1rem 2rem;
  }

  .tournament-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
    min-height: 0;
    padding: 1.2rem;
  }

  .tournament-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .tournament-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
  }

  .sections-card {
    margin-inline: -1rem;
    border-inline: 0;
    border-radius: 0;
  }

  .sections-card :deep(.sections) {
    padding-inline: 1rem;
  }

  .sections-btn {
    min-height: 40px;
    padding-inline: 0.75rem;
  }

  .tournament-grid {
    grid-template-columns: 1fr;
  }

  .manage-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
