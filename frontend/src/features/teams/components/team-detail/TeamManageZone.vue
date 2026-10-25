<template>
  <div v-if="isCaptain" class="team-management-actions">
    <management-action-card
      title="Edit team"
      description="Update the team profile and manage members in the team workspace."
    >
      <template #action>
        <ui-button as-link variant="secondary" :to="`/teams/${team?.id}/edit`">
          Edit team
        </ui-button>
      </template>
    </management-action-card>

    <management-action-card
      v-if="!team?.is_in_active_tournament"
      title="Team visibility"
      :description="team?.is_public
        ? 'Anyone can find this team and request to join.'
        : 'Only invited members can see this team.'"
    >
      <template #action>
        <team-visibility-modal
          :team="props.team"
          @changed-team-visibility="(newTeamValue) => emit('updateTeam', newTeamValue)"
        />
      </template>
    </management-action-card>

    <management-action-card
      title="Delete team"
      description="Permanently delete this team and its associated data. This cannot be undone."
      danger
    >
      <template #action>
        <delete-team-modal
          :disabled="props.loading"
          :team="props.team"
          @deleted="router.push('/teams')"
        />
      </template>
    </management-action-card>
  </div>
</template>

<script setup lang="ts">
import DeleteTeamModal from './modals/DeleteTeamModal.vue'
import TeamVisibilityModal from './modals/TeamVisibilityModal.vue'
import ManagementActionCard from '@/components/shared/ManagementActionCard.vue'
import UiButton from '@/components/ui/UiButton'
import { useRouter } from 'vue-router'
import type { Team } from '@/features/teams/types'

interface Props {
  team?: Team
  loading: boolean
  isCaptain: boolean
}

const props = defineProps<Props>()
const router = useRouter()

const emit = defineEmits<{
  (e: 'updateTeam', newTeamValue: Team): void
}>()
</script>

<style scoped>
.team-management-actions {
  display: grid;
  gap: 0.85rem;
}
</style>
