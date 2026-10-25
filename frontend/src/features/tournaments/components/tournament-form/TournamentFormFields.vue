<template>
  <form class="tournament-form" @submit.prevent="$emit('submit')">
    <tournament-basics-fields :form="form" />
    <tournament-capacity-fields :form="form" />
    <tournament-schedule-fields :form="form" />

    <div class="form-actions">
      <ui-button type="submit" size="lg" :disabled="isPending">
        {{ isPending ? pendingText : submitText }}
      </ui-button>
    </div>
  </form>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'
import TournamentBasicsFields from './TournamentBasicsFields.vue'
import TournamentCapacityFields from './TournamentCapacityFields.vue'
import TournamentScheduleFields from './TournamentScheduleFields.vue'
import type { TournamentFormController } from '../../composables/useTournamentForm'

defineProps<{
  form: TournamentFormController
  isPending: boolean
  submitText: string
  pendingText: string
}>()

defineEmits<{
  submit: []
}>()
</script>

<style scoped>
.tournament-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  min-width: 0;
  width: 100%;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}
</style>
