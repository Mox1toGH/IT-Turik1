<template>
  <ui-card class="panel form-panel" variant="form">
    <template #header>
      <div class="panel-header">
        <span class="step-marker">01</span>
        <div>
          <h2>Team profile</h2>
          <p class="text-muted">Core identity and contact details for the team directory.</p>
        </div>
        <ui-badge variant="green" class="access-badge">Captain access</ui-badge>
      </div>
    </template>

    <div class="teams-rule" aria-hidden="true"></div>

    <form class="form-grid" @submit.prevent="handleSubmit">
      <section class="form-section-grid identity-section">
        <div class="section-heading">
          <span class="section-number">Identity</span>
          <p class="text-muted">Public details shown across team pages.</p>
        </div>

        <label class="form-item">
          <p class="form-label">Team name</p>
          <ui-skeleton-loader :loading="props.loading" style="width: 100%">
            <template #skeleton>
              <ui-skeleton variant="rect" height="45px" width="100%" />
            </template>

            <ui-input
              v-model="form.fields.value.name"
              required
              :disabled="isSavingChanges"
              :isInvalid="!!form.errors.value.name"
              style="width: 100%"
              @blur="form.validateField('name')"
            />
            <small v-if="form.errors.value.name" class="text-error">{{
              form.errors.value.name
            }}</small>
          </ui-skeleton-loader>
        </label>

        <label class="form-item">
          <p class="form-label">Team email</p>
          <ui-skeleton-loader :loading="props.loading" style="width: 100%">
            <template #skeleton>
              <ui-skeleton variant="rect" height="45px" width="100%" />
            </template>

            <ui-input
              v-model="form.fields.value.email"
              type="email"
              required
              :disabled="isSavingChanges"
              :isInvalid="!!form.errors.value.email"
              style="width: 100%"
              @blur="form.validateField('email')"
            />
            <small v-if="form.errors.value.email" class="text-error">{{
              form.errors.value.email
            }}</small>
          </ui-skeleton-loader>
        </label>

        <label class="form-item">
          <p class="form-label">Organization</p>
          <ui-skeleton-loader :loading="props.loading" style="width: 100%">
            <template #skeleton>
              <ui-skeleton variant="rect" height="45px" width="100%" />
            </template>

            <ui-input
              v-model="form.fields.value.organization"
              :disabled="isSavingChanges"
              :isInvalid="!!form.errors.value.organization"
              style="width: 100%"
              @blur="form.validateField('organization')"
            />
            <small v-if="form.errors.value.organization" class="text-error">{{
              form.errors.value.organization
            }}</small>
          </ui-skeleton-loader>
        </label>
      </section>

      <div class="teams-rule" aria-hidden="true"></div>

      <section class="form-section-grid contact-section">
        <div class="section-heading">
          <span class="section-number">Contact</span>
          <p class="text-muted">Optional channels members can use to coordinate.</p>
        </div>

        <label class="form-item">
          <p class="form-label">Telegram</p>
          <ui-skeleton-loader :loading="props.loading" style="width: 100%">
            <template #skeleton>
              <ui-skeleton variant="rect" height="45px" width="100%" />
            </template>

            <ui-input
              v-model="form.fields.value.contact_telegram"
              title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
              :disabled="isSavingChanges"
              :isInvalid="!!form.errors.value.contact_telegram"
              style="width: 100%"
              @blur="form.validateField('contact_telegram')"
            />
            <small v-if="form.errors.value.contact_telegram" class="text-error">{{
              form.errors.value.contact_telegram
            }}</small>
          </ui-skeleton-loader>
        </label>

        <label class="form-item">
          <p class="form-label">Discord</p>
          <ui-skeleton-loader :loading="props.loading" style="width: 100%">
            <template #skeleton>
              <ui-skeleton variant="rect" height="45px" width="100%" />
            </template>

            <ui-input
              v-model="form.fields.value.contact_discord"
              title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
              :disabled="isSavingChanges"
              :isInvalid="!!form.errors.value.contact_discord"
              style="width: 100%"
              @blur="form.validateField('contact_discord')"
            />
            <small v-if="form.errors.value.contact_discord" class="text-error">{{
              form.errors.value.contact_discord
            }}</small>
          </ui-skeleton-loader>
        </label>
      </section>

      <ui-card class="form-actions" variant="actions">
        <ui-button
          type="submit"
          size="lg"
          :disabled="isSavingChanges || props.loading || props.isError"
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
      </ui-card>
    </form>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import { useNotification } from '@/composables/useNotification'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import { useForm } from '@/composables/useForm'
import { EditTeamSchema } from '@/schemas/teams.schema'
import { useUpdateTeam } from '@/api/teams/teams'
import type { TeamResponse } from '@/api/backendAPINinja.schemas'

interface Props {
  team?: TeamResponse
  loading: boolean
  isError?: boolean
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
.teams-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.access-badge {
  white-space: nowrap;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.form-section-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.section-heading {
  grid-column: 1 / -1;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
}

.section-heading p {
  margin: 0;
  text-align: right;
}

.section-number {
  color: var(--accent-strong);
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.full-width {
  grid-column: 1 / -1;
}

.form-actions.card {
  margin-top: 0.1rem;
  flex-direction: row;
  justify-content: flex-end;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border: 1px solid var(--line-soft);
}

@media (max-width: 760px) {
  .panel-header {
    flex-wrap: wrap;
  }

  .form-section-grid {
    grid-template-columns: 1fr;
  }

  .section-heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 0.35rem;
  }

  .section-heading p {
    text-align: left;
  }

  .form-actions.card {
    position: static;
    flex-direction: column-reverse;
    align-items: stretch;
  }
}
</style>
