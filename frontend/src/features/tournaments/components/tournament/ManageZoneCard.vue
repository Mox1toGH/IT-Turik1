<template>
  <management-action-card
    title="Delete tournament"
    description="Permanently delete this tournament and its associated data. This cannot be undone."
    danger
  >
    <template #action>
      <ui-button
        :disabled="isLoading"
        size="sm"
        variant="danger"
        @click="isDeleteModalOpen = true"
      >
        Delete tournament
      </ui-button>
    </template>
    <delete-tournament-modal v-model="isDeleteModalOpen" :tournament-id="props.tournamentId" />
  </management-action-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UiButton from '@/components/ui/UiButton'
import ManagementActionCard from '@/components/shared/ManagementActionCard.vue'
import DeleteTournamentModal from './modals/DeleteTournamentModal.vue'
import { useGetTournament } from '@/api/tournaments/tournaments'

const props = defineProps<{ tournamentId: number }>()
const isDeleteModalOpen = ref(false)
const { isLoading } = useGetTournament(props.tournamentId)
</script>
