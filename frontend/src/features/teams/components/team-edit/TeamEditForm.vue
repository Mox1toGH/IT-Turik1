<template>
  <ui-card class="panel form-panel">
    <header class="panel-head">
      <h2>Team profile settings</h2>
      <ui-badge variant="green">Captain access</ui-badge>
    </header>

    <form class="form-grid" @submit.prevent="handleSubmit">
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

      <div class="form-actions full-width">
        <ui-button type="submit" :disabled="isSavingChanges || props.loading || props.isError">
          <loading-icon v-if="isSavingChanges" />
          Save changes
        </ui-button>
        <ui-button asLink variant="secondary" :to="`/teams/${team?.id}`" :disabled="props.loading"
          >Cancel</ui-button
        >
      </div>
    </form>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import { useNotification } from '@/composables/useNotification'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import type { GetTeamInfoResponse } from '@/api/services/teams/types'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUpdateTeamInfo } from '@/api/queries/teams'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import { useForm } from '@/composables/useForm'
import { EditTeamSchema } from '@/schemas/teams.schema'

interface Props {
  team?: GetTeamInfoResponse
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

const { mutate: updateTeam } = useUpdateTeamInfo()

const handleSubmit = () => {
  if (!props.team || !form.validate()) return

  updateTeam(
    { teamId: props.team.id, body: form.fields.value },
    {
      onSuccess: () => {
        router.push(`/teams/${props.team?.id}`)
      },
      onError: (err) => {
        showNotification(
          err.response ? 'Unable to update team.' : 'Server connection error.',
          'error',
        )
      },
    },
  )
}
</script>

<style scoped>
.panel {
  border: 1px solid var(--line-soft);
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  margin-bottom: 0.9rem;
}

.panel-head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.15rem;
}

.lock-note {
  margin-top: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.full-width {
  grid-column: 1 / -1;
}

.form-actions {
  display: flex;
  gap: 0.6rem;
  align-items: center;
}

@media (max-width: 760px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
