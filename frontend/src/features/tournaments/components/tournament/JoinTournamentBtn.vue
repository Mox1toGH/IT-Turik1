<template>
  <template v-if="user?.role === 'team' && (hasEligibleTeams || props.registeredTeamId)">
    <ui-button v-if="!props.registeredTeamId" :disabled="isPending" @click="open">
      <LoadingIcon v-if="isPending" class="team-spinner" />
      <span>Join Tournament</span>
    </ui-button>

    <ui-button v-else :disabled="isPending" variant="danger" @click="handleLeave">
      <LoadingIcon v-if="isPending" class="team-spinner" />
      <span>Leave Tournament</span>
    </ui-button>

    <ui-modal v-model="isOpen">
      <template #title>
        <h3>Select team</h3>
      </template>

      <div v-if="isLoadingTeams" class="team-loading">
        <LoadingIcon />
      </div>

      <template v-else>
        <ui-input v-model="search" type="text" placeholder="Search teams..." autocomplete="off" />

        <ul v-if="filteredTeams" class="team-list">
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
          <p>
            {{ teams?.length ? 'No teams match your search.' : 'No eligible teams found.' }}
          </p>
        </ui-card>
      </template>
    </ui-modal>
  </template>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useNotification } from '@/composables/useNotification'
import UiInput from '@/components/ui/UiInput.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { useGetUserProfile } from '@/api/accounts/accounts'
import {
  useListEligibleTeamsForTournament,
  useRegisterTeamForTournament,
  useUnregisterTeamFromTournament,
} from '@/api/tournaments/tournaments'

interface Props {
  tournamentId: number
  registeredTeamId?: number | null
}

const props = defineProps<Props>()
const { showNotification } = useNotification()
const { data: user } = useGetUserProfile()

const isOpen = ref(false)
const search = ref('')

const { data: teams, isLoading: isLoadingTeams } = useListEligibleTeamsForTournament(
  props.tournamentId,
)
const { mutate: register, isPending } = useRegisterTeamForTournament()
const { mutate: leave } = useUnregisterTeamFromTournament()
const hasEligibleTeams = computed(() => (teams.value?.length ?? 0) > 0)

const filteredTeams = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return teams.value ?? []
  return teams.value?.filter((team) => team.name.toLowerCase().includes(query))
})

watch(isOpen, (val) => {
  if (!val) search.value = ''
})

function open() {
  isOpen.value = true
}

function close() {
  isOpen.value = false
}

function handleJoin(teamId: number) {
  if (isPending.value) return
  register(
    { id: props.tournamentId, data: { team_id: teamId } },
    {
      onSuccess: () => close(),
      onError: (error) => {
        showNotification(error?.message, 'error')
      },
    },
  )
}

function handleLeave() {
  if (!props.registeredTeamId || isPending.value) return
  leave(
    {
      id: props.tournamentId,
      data: {
        team_id: props.registeredTeamId,
      },
    },
    {
      onError: (error) => {
        showNotification(error?.message, 'error')
      },
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

.team-empty {
  background: var(--muted);
  border: 1px dashed var(--border);
}

.team-search:focus {
  border-color: var(--primary);
}

.team-search::placeholder {
  color: color-mix(in srgb, var(--foreground) 42%, transparent);
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

.team-spinner {
  flex-shrink: 0;
}

.team-empty {
  margin: 0;
  padding: 0.75rem;
  font-size: 0.875rem;
  text-align: center;
  color: color-mix(in srgb, var(--foreground) 45%, transparent);
}
</style>
