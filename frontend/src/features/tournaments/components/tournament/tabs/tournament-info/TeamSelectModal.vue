<template>
  <ui-modal v-model="isOpen">
    <template #title>
      <h3>Select team</h3>
    </template>

    <div v-if="isLoadingTeams" class="team-loading">
      <LoadingIcon />
    </div>

    <template v-else>
      <ui-input v-model="search" type="text" placeholder="Search teams..." autocomplete="off" />

      <ul v-if="filteredTeams.length" class="team-list">
        <li
          v-for="team in filteredTeams"
          :key="team.id"
          class="team-item"
          :class="{ disabled: isPending }"
          @click="handleJoin(team.id)"
        >
          <span class="team-name">{{ team.name }}</span>
          <ui-badge>{{ team.members_count }}</ui-badge>
        </li>
      </ul>

      <ui-card v-else class="team-empty">
        <p>{{ teams?.length ? 'No teams match your search.' : 'No eligible teams found.' }}</p>
      </ui-card>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiCard from '@/components/ui/UiCard.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useNotification } from '@/composables/useNotification'
import {
  useListEligibleTeamsForTournament,
  useRegisterTeamForTournament,
} from '@/api/tournaments/tournaments'

const props = defineProps<{ tournamentId: number }>()
const isOpen = defineModel<boolean>({ default: false })

const { showNotification } = useNotification()
const search = ref('')

const { data: teams, isLoading: isLoadingTeams } = useListEligibleTeamsForTournament(
  props.tournamentId,
)
const { mutate: register, isPending } = useRegisterTeamForTournament()

const filteredTeams = computed(() => {
  const query = search.value.trim().toLowerCase()
  const all = teams.value ?? []
  if (!query) return all
  return all.filter((team) => team.name.toLowerCase().includes(query))
})

watch(isOpen, (val) => {
  if (!val) search.value = ''
})

function handleJoin(teamId: number) {
  if (isPending.value) return
  register(
    { id: props.tournamentId, data: { team_id: teamId } },
    {
      onSuccess: () => (isOpen.value = false),
      onError: (error) => showNotification(error?.message, 'error'),
    },
  )
}
</script>

<style scoped>
.team-loading {
  display: flex;
  justify-content: center;
  padding: 1.5rem;
}

.team-list {
  list-style: none;
  background: var(--muted);
  padding: 0;
  border-radius: var(--radius);
  max-height: 400px;
  overflow-y: auto;
}

.team-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.1s ease;
}

.team-item:hover:not(.disabled) {
  background: color-mix(in srgb, var(--foreground) 5%, transparent);
}

.team-item.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.team-name {
  font-size: 0.875rem;
}

.team-empty {
  background: var(--muted);
  border: 1px dashed var(--border);
  margin: 0;
  padding: 0.75rem;
  font-size: 0.875rem;
  text-align: center;
  color: color-mix(in srgb, var(--foreground) 45%, transparent);
}
</style>
