<template>
  <ui-card class="form-panel">
    <div class="panel-header">
      <span class="step-marker">02</span>
      <div>
        <h2>Capacity</h2>
        <p class="text-muted">Control how many teams can enter and how large they must be.</p>
      </div>
    </div>

    <div class="settings-row">
      <label class="form-item">
        <span class="form-label">Max teams</span>
        <ui-number-input
          id="maxTeams"
          v-model.number="form.fields.value.max_teams"
          min="2"
          required
          :isInvalid="!!form.errors.value.max_teams"
          @blur="form.validateField('max_teams')"
        />
        <small v-if="form.errors.value.max_teams" class="text-error">{{
          form.errors.value.max_teams
        }}</small>
      </label>

      <label class="form-item">
        <span class="form-label">Min team members</span>
        <ui-number-input
          id="minTeamMembers"
          v-model.number="form.fields.value.min_team_members"
          min="2"
          required
          :isInvalid="!!form.errors.value.min_team_members"
          @blur="form.validateField('min_team_members')"
        />
        <small v-if="form.errors.value.min_team_members" class="text-error">{{
          form.errors.value.min_team_members
        }}</small>
      </label>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'
import UiNumberInput from '@/components/ui/UiNumberInput'
import type { TournamentFormController } from '../../composables/useTournamentForm'

const props = defineProps<{
  form: TournamentFormController
}>()
const form = { ...props.form }
</script>

<style scoped>
.form-panel {
  display: grid;
  gap: 1rem;
}

.panel-header p {
  margin: 0.25rem 0 0;
}

.settings-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.8rem;
}

@media (max-width: 480px) {
  .settings-row {
    grid-template-columns: 1fr;
  }
}
</style>
