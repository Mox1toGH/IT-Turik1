<template>
  <section class="tournament-detail-page page-shell">
    <TournamentHeroCard :tournament-id="id" />

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

        <ManageZoneCard
          v-if="user?.role === 'admin' && currentSection === 'information'"
          :tournament-id="id"
        />
      </div>
    </transition>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiHorizontalScroll from '@/components/ui/UiHorizontalScroll.vue'
import { useRoute, useRouter } from 'vue-router'
import TournamentInfo from '../components/tournament/tabs/TournamentInfo.vue'
import TournamentTeams from '../components/tournament/tabs/TournamentTeams.vue'
import { ref, watch } from 'vue'
import TournamentSchedule from '../components/tournament/tabs/TournamentSchedule.vue'
import TournamentRounds from '../components/tournament/tabs/TournamentRounds.vue'
import JuryAssign from '../components/tournament/tabs/tournament-submissions/JuryAssign.vue'
import TournamentSubmissions from '../components/tournament/tabs/TournamentSubmissions.vue'
import TournamentLeaderboard from '../components/tournament/tabs/TournamentLeaderboard.vue'

import { useGetUserProfile } from '@/api/accounts/accounts'
import { useGetTournament } from '@/api/tournaments/tournaments'
import ManageZoneCard from '../components/tournament/ManageZoneCard.vue'
import TournamentHeroCard from '../components/tournament/TournamentHeroCard.vue'

type Sections = 'information' | 'schedule' | 'rounds' | 'submissions' | 'leaderboard'

const route = useRoute()
const router = useRouter()

const id = Number(route.params.id)

const { data: user } = useGetUserProfile()
const { data: tournament } = useGetTournament(id)

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
  padding:;
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

@media (max-width: 810px) {
  .tournament-detail-page {
    padding: 1rem 1rem 2rem;
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
}
</style>
