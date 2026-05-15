<template>
  <section class="page-shell">
    <ui-card class="hero-card" :class="{ 'hero-card--with-banner': Boolean(tournament?.banner) }">
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
      <template #header>
        <div class="hero-content">
          <p class="section-eyebrow">Tournaments</p>
          <h1 class="section-title">{{ tournament?.name ?? `Tournament ${id}` }}</h1>
        </div>
      </template>

      <template #footer>
        <div class="hero-actions hero-content">
          <ui-button asLink to="/tournaments" variant="secondary" size="sm" class="tournament-link">
            Back to tournaments
          </ui-button>
        </div>
      </template>
    </ui-card>

    <ui-card>
      <div class="sections">
        <ui-button
          variant="secondary"
          :class="['sections-btn', { active: currentSection === 'information' }]"
          @click="setActiveSection('information')"
          >Information</ui-button
        >
        <ui-button
          variant="secondary"
          :class="['sections-btn', { active: currentSection === 'rounds' }]"
          @click="setActiveSection('rounds')"
          >Rounds</ui-button
        >
        <ui-button
          variant="secondary"
          :disabled="user?.role !== 'admin' && user?.role !== 'team'"
          :class="['sections-btn', { active: currentSection === 'submissions' }]"
          @click="setActiveSection('submissions')"
          >Submissions</ui-button
        >
        <ui-button
          variant="secondary"
          :class="['sections-btn', { active: currentSection === 'schedule' }]"
          @click="setActiveSection('schedule')"
          >Schedule</ui-button
        >
        <ui-button
          variant="secondary"
          :class="['sections-btn', { active: currentSection === 'leaderboard' }]"
          @click="setActiveSection('leaderboard')"
          >Leaderboard</ui-button
        >
      </div>
    </ui-card>

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

.hero-card {
  position: relative;
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 2;
}

.section-title {
  color: var(--foreground);
}

.hero-card--with-banner .section-title {
  color: #fff;
}

.hero-card--with-banner :deep(.ui-card-body),
.hero-card--with-banner :deep(.ui-card-header),
.hero-card--with-banner :deep(.ui-card-footer) {
  color: #fff;
}

.hero-card--with-banner .section-eyebrow {
  color: #f8d7b6;
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
  background: var(--secondary);
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

.tournament-link {
  width: max-content;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.sections {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.sections-btn.active {
  background: var(--primary);
  color: var(--primary-foreground);
}

.tournament-grid {
  display: flex;
  gap: 1rem;
}

.manage-zone {
  margin-top: 1rem;
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
  .tournament-grid {
    flex-direction: column;
  }

  .manage-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
