<template>
  <ui-card class="form-panel basics-panel">
    <div class="panel-header">
      <span class="step-marker">01</span>
      <div>
        <h2>Basics</h2>
        <p class="text-muted">Name the tournament and describe what teams are joining.</p>
      </div>
    </div>

    <label class="form-item">
      <span class="form-label">Tournament name</span>
      <ui-input
        id="tournamentName"
        v-model="form.fields.value.name"
        placeholder="Enter tournament name"
        required
        :isInvalid="!!form.errors.value.name"
        @blur="form.validateField('name')"
      />
      <small v-if="form.errors.value.name" class="text-error">{{
        form.errors.value.name
      }}</small>
    </label>

    <label class="form-item description-field">
      <span class="form-label">Description</span>
      <ui-text-area
        id="tournamentDescription"
        v-model="form.fields.value.description"
        class="description-input"
        required
        :isInvalid="!!form.errors.value.description"
        @blur="form.validateField('description')"
      />
      <small v-if="form.errors.value.description" class="text-error">{{
        form.errors.value.description
      }}</small>
    </label>
  </ui-card>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'
import UiInput from '@/components/ui/UiInput'
import UiTextArea from '@/components/ui/UiTextArea'
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

.basics-panel {
  grid-template-columns: minmax(0, 0.85fr) minmax(320px, 1.15fr);
}

.basics-panel .panel-header {
  grid-column: 1 / -1;
}

.panel-header p {
  margin: 0.25rem 0 0;
}

.description-input {
  min-height: 190px;
  height: 100%;
}

@media (max-width: 980px) {
  .basics-panel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .description-input {
    height: 150px;
  }
}
</style>
