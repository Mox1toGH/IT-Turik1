<template>
  <UiCard class="manage-zone">
    <div>
      <div class="manage-row">
        <div>
          <h3>Edit tournament</h3>
          <p class="text-muted">Update tournament details in edit workspace.</p>
        </div>
        <UiButton
          asLink
          variant="secondary"
          size="sm"
          :to="`/tournaments/${props.tournamentId}/edit`"
        >
          Edit tournament
        </UiButton>
      </div>

      <div>
        <div class="danger-zone-header">
          <DangerIcon />
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

            <UiButton
              :disabled="isLoading"
              size="sm"
              variant="danger"
              @click="isDeleteModalOpen = true"
              >Delete</UiButton
            >

            <DeleteTournamentModal
              v-model="isDeleteModalOpen"
              :tournament-id="props.tournamentId"
            />
          </div>
        </div>
      </div>
    </div>
  </UiCard>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import UiCard from '@/components/ui/UiCard.vue'
import DeleteTournamentModal from './modals/DeleteTournamentModal.vue'
import UiButton from '@/components/ui/UiButton.vue'
import DangerIcon from '@/icons/DangerIcon.vue'

import { useGetTournament } from '@/api/tournaments/tournaments.ts'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()

const isDeleteModalOpen = ref(false)

const { isLoading } = useGetTournament(props.tournamentId)
</script>

<style scoped>
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

@media (max-width: 810px) {
  .manage-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
