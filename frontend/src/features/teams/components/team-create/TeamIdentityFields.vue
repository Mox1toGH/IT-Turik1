<template>
  <ui-section
    title="Identity"
    description="Add the essentials people will see in the team directory."
  >
    <div class="identity-grid">
      <label class="form-item">
        <p class="form-label">Team name</p>
        <ui-input
          v-model="form.fields.value.name"
          :is-invalid="!!form.errors.value.name"
          required
          placeholder="Enter team name"
          @blur="form.validateField('name')"
        />
        <small v-if="form.errors.value.name" class="text-error">{{
          form.errors.value.name
        }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Team email</p>
        <ui-input
          v-model="form.fields.value.email"
          :is-invalid="!!form.errors.value.email"
          type="email"
          required
          placeholder="team@example.com"
          @blur="form.validateField('email')"
        />
        <small v-if="form.errors.value.email" class="text-error">{{
          form.errors.value.email
        }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Organization</p>
        <ui-input
          v-model="form.fields.value.organization"
          :is-invalid="!!form.errors.value.organization"
          placeholder="School, company, or community"
          @blur="form.validateField('organization')"
        />
        <small v-if="form.errors.value.organization" class="text-error">{{
          form.errors.value.organization
        }}</small>
      </label>

      <label class="form-label toggle-field">
        <span>Team visibility</span>
        <div class="visibility-control">
          <span class="visibility-label">Private</span>
          <ui-switch
            v-model="form.fields.value.is_public"
            :aria-checked="form.fields.value.is_public ? 'true' : 'false'"
            :aria-label="`Team visibility: ${form.fields.value.is_public ? 'Public' : 'Private'}`"
            @blur="form.validateField('is_public')"
          />
          <span class="visibility-label">Public</span>
        </div>
        <small v-if="form.errors.value.is_public" class="text-error">{{
          form.errors.value.is_public
        }}</small>
      </label>
    </div>
  </ui-section>
</template>

<script setup lang="ts">
import UiInput from '@/components/ui/UiInput'
import UiSection from '@/components/ui/UiSection'
import UiSwitch from '@/components/ui/UiSwitch'
import type { useForm } from '@/composables/useForm'
import type { TeamCreateFormFields } from '../../composables/useTeamCreateForm'

interface Props {
  form: ReturnType<typeof useForm<TeamCreateFormFields>>
}

const props = defineProps<Props>()
const form = { ...props.form }
</script>

<style scoped>
.identity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.form-label {
  margin: 0;
}

.toggle-field {
  display: grid;
  gap: 0.45rem;
  align-content: start;
}

.visibility-control {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  border: 1px solid var(--border);
  background: var(--subtle);
  padding: 0.75rem 0.85rem;
  border-radius: var(--radius-sm);
  min-height: 44px;
}

.visibility-label {
  font-size: 0.86rem;
  user-select: none;
}
</style>
