<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div>
          <p class="section-eyebrow">Tournaments</p>
          <h1>Tournament {{ id }}</h1>
        </div>
      </template>

      <template #footer>
        <ui-button asLink to="/" variant="secondary" size="sm" class="tournament-link">
          Back to tournaments
        </ui-button>
      </template>
    </ui-card>

    <ui-card>
      <div class="sections">
        <div
          variant="secondary"
          :class="['sections-btn', { active: currentSection === 'information' }]"
          @click="setActiveSection('information')"
        >
          Information
        </div>
        <div
          variant="secondary"
          :class="['sections-btn', { active: currentSection === 'rounds' }]"
          @click="setActiveSection('rounds')"
        >
          Rounds
        </div>
        <div
          variant="secondary"
          :disabled="user?.role !== 'admin' && user?.role !== 'team'"
          :class="['sections-btn', { active: currentSection === 'submissions' }]"
          @click="setActiveSection('submissions')"
        >
          Submissions
        </div>
        <div
          variant="secondary"
          :class="['sections-btn', { active: currentSection === 'schedule' }]"
          @click="setActiveSection('schedule')"
        >
          Schedule
        </div>
        <div
          variant="secondary"
          :class="['sections-btn', { active: currentSection === 'leaderboard' }]"
          @click="setActiveSection('leaderboard')"
        >
          Leaderboard
        </div>
      </div>
    </ui-card>

    <div class="tournament-grid" v-if="currentSection === 'information'">
      <TournamentInfo :tournament-id="id" />
      <TournamentTeams :tournament-id="id" />
    </div>

    <TournamentRounds :tournament-id="id" v-if="currentSection === 'rounds'" />
    <TournamentSchedule :tournament-id="id" v-if="currentSection === 'schedule'" />
    <TournamentLeaderboard :tournament-id="id" v-if="currentSection === 'leaderboard'" />

    <template
      v-if="currentSection === 'submissions' && (user?.role === 'admin' || user?.role === 'team')"
    >
      <TournamentSubmissions :tournament-id="id" v-if="user?.role === 'team'" />
      <JuryAssign :tournament-id="id" v-if="user?.role === 'admin'" />
    </template>

    <ui-card
      v-if="
        currentSection === 'submissions' && user && user.role !== 'team' && user.role !== 'admin'
      "
    >
      <p>Submissions are available for team members and admins.</p>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { useRoute, useRouter } from 'vue-router'
import TournamentInfo from '../components/tournament/TournamentInfo.vue'
import TournamentTeams from '../components/tournament/TournamentTeams.vue'
import { ref, watch } from 'vue'
import TournamentSchedule from '../components/tournament/TournamentSchedule.vue'
import TournamentRounds from '../components/tournament/TournamentRounds.vue'
import JuryAssign from '../components/tournament/tournament-submissions/JuryAssign.vue'
import TournamentSubmissions from '../components/tournament/TournamentSubmissions.vue'
import { useProfile } from '@/api/queries/accounts'
import TournamentLeaderboard from '../components/tournament/TournamentLeaderboard.vue'

type Sections = 'information' | 'schedule' | 'rounds' | 'submissions' | 'leaderboard'

const route = useRoute()
const router = useRouter()
const id = Number(route.params.id) || 1

const { data: user } = useProfile()

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
.tournament-link {
  width: max-content;
}

.sections {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  border-bottom: 2px solid var(--border);
}

.sections-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem;
  padding-bottom: 0.8rem;
  border-bottom: 2px solid transparent;
  font-weight: 600;
  transition: all 0.2s ease;
}

.sections-btn:hover {
  cursor: pointer;
}

.sections-btn.active,
.sections-btn:hover {
  border-bottom: 2px solid var(--primary);
  color: var(--primary);
}

.tournament-grid {
  display: flex;
  gap: 1rem;
}

@media (max-width: 810px) {
  .tournament-grid {
    flex-direction: column;
  }
}
</style>
