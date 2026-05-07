<template>
  <section class="page-shell teams-page">
    <ui-card>
      <template #header>
        <div>
          <p class="section-eyebrow">Teams</p>
          <h1 class="section-title">Create new team</h1>
          <p class="section-subtitle">Create a team and optionally add initial members.</p>
          <ui-button asLink class="back-link" variant="secondary" size="sm" to="/teams"
            >Back to teams list</ui-button
          >
        </div>
      </template>

      <form class="form-grid" @submit.prevent="handleFormSubmit">
        <label class="form-item">
          <p class="form-label">Team name</p>
          <ui-input
            v-model="form.fields.value.name"
            :is-invalid="!!form.errors.value.name"
            required
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

        <label class="form-item">
          <p class="form-label">Add initial members</p>
          <ui-select
            v-model="form.fields.value.member_ids"
            :isLoading="isLoadingUsers"
            :isError="isLoadingError || !!form.errors.value.member_ids"
            :error="`Error while fetching users (code: ${getUsersError?.code})`"
            :multiple="true"
            :options="
              createCandidateUsers?.map((u) => ({
                value: u.id,
                label: `${u.username} (${u.email})`,
              }))
            "
            placeholder="Select members"
            @blur="form.validateField('member_ids')"
          />
          <small v-if="form.errors.value.member_ids" class="text-error">{{
            form.errors.value.member_ids
          }}</small>
        </label>

        <ui-button class="full-width" :disabled="isCreatingTeam" type="submit">
          <loading-icon v-if="isCreatingTeam" />
          Create team
        </ui-button>
      </form>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import { useNotification } from '@/composables/useNotification'
import type { CreateTeamBody } from '@/api/services/teams/types'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCreateTeam } from '@/api/queries/teams'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useProfile, useUsers } from '@/api/queries/accounts'
import UiSelect from '@/components/ui/UiSelect.vue'
import { parseApiError } from '@/api/errors'
import UiSwitch from '@/components/ui/UiSwitch.vue'
import { useForm } from '@/composables/useForm'
import { CreateTeamSchema } from '@/schemas/teams.schema'

const router = useRouter()
const { showNotification } = useNotification()

type Form = CreateTeamBody

const form = useForm<Form>(CreateTeamSchema, {
  name: '',
  email: '',
  organization: '',
  contact_telegram: '',
  contact_discord: '',
  is_public: false,
  member_ids: [],
})

const resetForm = () => {
  form.reset()
}

const { data: user } = useProfile()

const createCandidateUsers = computed(() => {
  return users.value?.filter((u) => {
    if (u.id === user.value?.id) return false
    return [u.username, u.email, u.full_name || ''].join(' ').toLowerCase()
  })
})

const { data: users, isLoading: isLoadingUsers, error: usersError, isLoadingError } = useUsers()
const getUsersError = computed(() => parseApiError(usersError.value))

const { mutate: createTeam, isPending: isCreatingTeam } = useCreateTeam()

const handleFormSubmit = () => {
  if (!form.validate()) return

  createTeam(
    { body: form.fields.value },
    {
      onSuccess: (data) => {
        showNotification('Team created successfully.', 'success')
        resetForm()

        router.push(`/teams/${data.id}`)
      },
      onError: (error) => {
        const parsedError = parseApiError(error)
        for (const [field, errors] of Object.entries(parsedError?.details || {})) {
          form.setError(field as keyof Form, errors?.[0] ?? 'Invalid value')
        }
      },
    },
  )
}
</script>

<style scoped>
.teams-page {
  gap: 1.2rem;
}

.back-link {
  margin-top: 0.8rem;
  display: inline-block;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.full-width {
  grid-column: 1 / -1;
}

.toggle-field {
  display: grid;
  gap: 0.45rem;
}

.visibility-control {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  border: 1px solid var(--border);
  background: var(--input);
  padding: 0.75rem 0.85rem;
  border-radius: 12px;
}

.visibility-label {
  font-size: 0.86rem;
  user-select: none;
}

@media (max-width: 760px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
