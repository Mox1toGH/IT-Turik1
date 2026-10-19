<template>
  <ui-card class="panel form-panel">
    <template #header>
      <div class="panel-header">
        <div>
          <h2>Team profile</h2>
          <p class="text-muted">Core identity and contact details for the team directory.</p>
        </div>
      </div>
    </template>

    <form class="edit-form" @submit.prevent="handleSubmit">
      <section class="form-section-grid identity-section">
        <div class="section-heading">
          <h3 class="section-title">Identity</h3>
          <p class="text-muted">Public details shown across team pages.</p>
        </div>

        <label class="form-item">
          <p class="form-label">Team name</p>
          <ui-input
              v-model="form.fields.value.name"
              required
              :disabled="isSavingChanges"
              :isInvalid="!!form.errors.value.name"
              style="width: 100%"
              @blur="form.validateField('name')"
            /><small v-if="form.errors.value.name" class="text-error">{{
              form.errors.value.name
            }}</small>
        </label>

        <label class="form-item">
          <p class="form-label">Team email</p>
          <ui-input
              v-model="form.fields.value.email"
              type="email"
              required
              :disabled="isSavingChanges"
              :isInvalid="!!form.errors.value.email"
              style="width: 100%"
              @blur="form.validateField('email')"
            /><small v-if="form.errors.value.email" class="text-error">{{
              form.errors.value.email
            }}</small>
        </label>

        <label class="form-item">
          <p class="form-label">Organization</p>
          <ui-input
              v-model="form.fields.value.organization"
              :disabled="isSavingChanges"
              :isInvalid="!!form.errors.value.organization"
              style="width: 100%"
              @blur="form.validateField('organization')"
            /><small v-if="form.errors.value.organization" class="text-error">{{
              form.errors.value.organization
            }}</small>
        </label>
      </section>

      <section class="form-section-grid contact-section">
        <div class="section-heading">
          <h3 class="section-title">Contact</h3>
          <p class="text-muted">Optional channels members can use to coordinate.</p>
        </div>

        <label class="form-item">
          <p class="form-label">Telegram</p>
          <ui-input
              v-model="form.fields.value.contact_telegram"
              title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
              :disabled="isSavingChanges"
              :isInvalid="!!form.errors.value.contact_telegram"
              style="width: 100%"
              @blur="form.validateField('contact_telegram')"
            /><small v-if="form.errors.value.contact_telegram" class="text-error">{{
              form.errors.value.contact_telegram
            }}</small>
        </label>

        <label class="form-item">
          <p class="form-label">Discord</p>
          <ui-input
              v-model="form.fields.value.contact_discord"
              title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
              :disabled="isSavingChanges"
              :isInvalid="!!form.errors.value.contact_discord"
              style="width: 100%"
              @blur="form.validateField('contact_discord')"
            /><small v-if="form.errors.value.contact_discord" class="text-error">{{
              form.errors.value.contact_discord
            }}</small>
        </label>
      </section>

      <div class="form-actions">
        <ui-button
          type="submit"
          size="lg"
          :disabled="isSavingChanges || props.loading || props.status === 'error'"
        >
          <loading-icon v-if="isSavingChanges" />
          Save changes
        </ui-button>
        <ui-button
          asLink
          variant="secondary"
          size="lg"
          :to="`/teams/${team?.id}`"
          :disabled="props.loading"
          >Cancel</ui-button
        >
      </div>
    </form>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiInput from '@/components/ui/UiInput'
import { useNotification } from '@/composables/useNotification'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { useForm } from '@/composables/useForm'
import { EditTeamSchema } from '@/schemas/teams.schema'
import { useUpdateTeam } from '@/api/teams/teams'
import type { QueryStatus } from '@/composables/useQueryState'
import type { QueryLike } from '@/composables/useQueryState'
import type { Team } from '@/features/teams/types'

interface Props {
  team?: Team
  loading: boolean
  status: QueryStatus
  query: QueryLike
}

const props = defineProps<Props>()
const router = useRouter()
const { showNotification } = useNotification()

const form = useForm(EditTeamSchema, {
  name: props.team?.name ?? '',
  email: props.team?.email ?? '',
  organization: props.team?.organization ?? '',
  contact_telegram: props.team?.contact_telegram ?? '',
  contact_discord: props.team?.contact_discord ?? '',
})

const isSavingChanges = ref(false)

const { mutate: updateTeam } = useUpdateTeam()

const handleSubmit = () => {
  if (!props.team || !form.validate()) return
  isSavingChanges.value = true

  updateTeam(
    { pk: props.team.id, data: form.fields.value },
    {
      onSuccess: () => {
        showNotification('Team updated successfully.', 'success')
        router.push(`/teams/${props.team?.id}`)
      },
      onError: (error) => {
        showNotification(error.message, 'error')
      },
      onSettled: () => {
        isSavingChanges.value = false
      },
    },
  )
}
</script>

<style scoped>
.access-badge {
  margin-left: auto;
  white-space: nowrap;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.form-section-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.form-section-grid + .form-section-grid {
  padding-top: 1.15rem;
  border-top: 1px solid var(--border);
}

.section-heading {
  grid-column: 1 / -1;
  display: grid;
  gap: 0.15rem;
}

.section-heading p {
  margin: 0;
}

.section-title {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
  font-weight: 800;
}

.form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.1rem;
  border-top: 1px solid var(--border);
  padding-top: 1rem;
}

@media (max-width: 760px) {
  .panel-header {
    flex-wrap: wrap;
  }

  .access-badge {
    margin-left: 0;
  }

  .form-section-grid {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
