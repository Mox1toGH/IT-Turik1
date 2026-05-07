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
        <ui-button asLink to="/tournaments" variant="secondary" size="sm" class="tournament-link">
          Back to tournaments
        </ui-button>
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

    <div class="tournament-grid" v-if="currentSection === 'information'">
      <TournamentInfo :tournament-id="id" />
      <TournamentTeams :tournament-id="id" />
    </div>

    <TournamentRounds :tournament-id="id" v-if="currentSection === 'rounds'" />
    <TournamentSchedule :tournament-id="id" v-if="currentSection === 'schedule'" />
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

type Sections = 'information' | 'schedule' | 'rounds' | 'submissions' | 'leaderboard'

const route = useRoute()
const router = useRouter()
const id = Number(route.params.id) || 1

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

@media (max-width: 810px) {
  .tournament-grid {
    flex-direction: column;
  }
}
</style>
