<template>
  <ui-section title="Contact" description="Add optional handles for quick communication.">
    <div class="contact-grid">
      <label class="form-item">
        <p class="form-label">Telegram</p>
        <ui-input
          v-model="form.fields.value.contact_telegram"
          :is-invalid="!!form.errors.value.contact_telegram"
          placeholder="@team_username"
          title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
          @blur="form.validateField('contact_telegram')"
        />
        <small v-if="form.errors.value.contact_telegram" class="text-error">{{
          form.errors.value.contact_telegram
        }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Discord</p>
        <ui-input
          v-model="form.fields.value.contact_discord"
          :is-invalid="!!form.errors.value.contact_discord"
          placeholder="team.username"
          title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
          @blur="form.validateField('contact_discord')"
        />
        <small v-if="form.errors.value.contact_discord" class="text-error">{{
          form.errors.value.contact_discord
        }}</small>
      </label>
    </div>
  </ui-section>
</template>

<script setup lang="ts">
import UiInput from '@/components/ui/UiInput'
import UiSection from '@/components/ui/UiSection'
import type { useForm } from '@/composables/useForm'
import type { TeamCreateFormFields } from '../../composables/useTeamCreateForm'

interface Props {
  form: ReturnType<typeof useForm<TeamCreateFormFields>>
}

const props = defineProps<Props>()
const form = { ...props.form }
</script>

<style scoped>
.contact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  min-width: 0;
}

.form-label {
  margin: 0;
}
</style>
