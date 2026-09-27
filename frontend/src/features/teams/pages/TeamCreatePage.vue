<template>
  <section class="team-create-page page-shell">
    <header class="create-hero">
      <div>
        <p class="section-eyebrow">Team workspace</p>
        <h1>Create new team</h1>
        <p class="section-subtitle">
          Set up the team profile, contact channels, and optional starting members.
        </p>
      </div>

      <ui-button asLink class="back-link" variant="default" size="lg" to="/teams">
        Back to teams
      </ui-button>
    </header>

    <div class="create-layout">
      <form class="team-form" @submit.prevent="handleFormSubmit">
        <ui-card class="form-panel identity-panel">
          <div class="panel-header">
            <span class="step-marker">01</span>
            <div>
              <h2>Identity</h2>
              <p class="text-muted">Add the essentials people will see in the team directory.</p>
            </div>
          </div>

          <div class="teams-rule" aria-hidden="true"></div>
          <div class="teams-rule" aria-hidden="true"></div>

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
        </ui-card>

        <ui-card class="form-panel">
          <div class="panel-header">
            <span class="step-marker">02</span>
            <div>
              <h2>Contact</h2>
              <p class="text-muted">Add optional handles for quick communication.</p>
            </div>
          </div>

          <div class="teams-rule" aria-hidden="true"></div>

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
        </ui-card>

        <ui-card class="form-panel">
          <div class="panel-header">
            <span class="step-marker">03</span>
            <div>
              <h2>Members</h2>
              <p class="text-muted">Invite initial members now, or leave this empty for later.</p>
            </div>
          </div>

          <div class="teams-rule" aria-hidden="true"></div>

          <label class="form-item">
            <p class="form-label">Add initial members</p>
            <ui-select
              v-model="form.fields.value.member_ids!"
              :isLoading="isLoadingUsers"
              :isError="isLoadingError || !!form.errors.value.member_ids"
              :error="`Error while fetching users (code: ${usersError?.code})`"
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
        </ui-card>

        <div class="form-actions">
          <ui-button asLink variant="secondary" size="lg" to="/teams">Cancel</ui-button>
          <ui-button :disabled="isCreatingTeam" type="submit" size="lg">
            <loading-icon v-if="isCreatingTeam" />
            {{ isCreatingTeam ? 'Creating...' : 'Create team' }}
          </ui-button>
        </div>
      </form>

      <aside class="summary-panel" aria-label="Team summary">
        <ui-card variant="stat" class="summary-stat">
          <strong>{{ selectedMembersCount }}</strong>
          <span>Initial members</span>
        </ui-card>

        <ui-card class="summary-card">
          <p class="section-eyebrow">Draft summary</p>
          <h2>{{ form.fields.value.name || 'Untitled team' }}</h2>
          <p class="summary-description text-muted">
            {{ form.fields.value.organization || 'Organization will appear here when added.' }}
          </p>

          <div class="summary-list">
            <div>
              <span>Visibility</span>
              <strong>{{ form.fields.value.is_public ? 'Public' : 'Private' }}</strong>
            </div>
            <div>
              <span>Email</span>
              <strong>{{ form.fields.value.email || 'Not set' }}</strong>
            </div>
            <div>
              <span>Contact</span>
              <strong>{{ contactSummary }}</strong>
            </div>
          </div>
        </ui-card>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import { useNotification } from '@/composables/useNotification'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiSwitch from '@/components/ui/UiSwitch.vue'
import { useForm } from '@/composables/useForm'
import { CreateTeamSchema } from '@/schemas/teams.schema'
import { useCreateTeam, type CreateTeamMutationBody } from '@/api/teams/teams'
import { useGetUserProfile, useListUsers } from '@/api/accounts/accounts'

const router = useRouter()
const { showNotification } = useNotification()

type Form = CreateTeamMutationBody

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

const { data: user } = useGetUserProfile()

const createCandidateUsers = computed(() => {
  return users.value?.filter((u) => {
    if (u.id === user.value?.id) return false
    return [u.username, u.email, u.full_name || ''].join(' ').toLowerCase()
  })
})

const selectedMembersCount = computed(() => form.fields.value.member_ids?.length ?? 0)
const contactSummary = computed(() => {
  if (form.fields.value.contact_telegram && form.fields.value.contact_discord) return '2 channels'
  if (form.fields.value.contact_telegram || form.fields.value.contact_discord) return '1 channel'
  return 'Not set'
})

const { data: users, isLoading: isLoadingUsers, error: usersError, isLoadingError } = useListUsers()
const { mutate: createTeam, isPending: isCreatingTeam } = useCreateTeam()

const handleFormSubmit = () => {
  if (!form.validate()) return

  createTeam(
    { data: form.fields.value },
    {
      onSuccess: (data) => {
        showNotification('Team created successfully.', 'success')
        resetForm()

        router.push(`/teams/${data.id}`)
      },
      onError: (error) => {
        for (const [field, errors] of Object.entries(error?.details || {})) {
          form.setError(field as keyof Form, errors?.[0] ?? 'Invalid value')
        }

        showNotification(error.message, 'error')
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

.team-create-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.create-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
  padding: 1.5rem;
  border: 1px solid var(--line-soft);
  border-radius: 20px;
}

.create-hero h1 {
  margin: 0.35rem 0 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-weight: 800;
}

.create-hero .section-subtitle {
  max-width: 680px;
  margin: 0.45rem 0 0;
}

.back-link {
  flex: 0 0 auto;
}

.create-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.38fr);
  gap: 1rem;
  align-items: start;
}

.team-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-panel.card {
  display: grid;
  gap: 1rem;
}

.contact-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

.identity-panel,
.contact-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.identity-panel .panel-header {
  grid-column: 1 / -1;
}

.form-label {
  margin: 0;
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
  min-height: 44px;
}

.visibility-label {
  font-size: 0.86rem;
  user-select: none;
}

.form-actions {
  position: sticky;
  bottom: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 0.8rem;
  border: 1px solid var(--line-soft);
  border-radius: 16px;
  backdrop-filter: blur(12px);
}

.summary-panel {
  position: sticky;
  top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

.summary-stat {
  justify-content: flex-start;
}

.summary-stat strong {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  line-height: var(--text-2xl--line-height);
  font-weight: 800;
}

.summary-stat span {
  color: var(--muted-foreground);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.summary-card.card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-radius: 18px;
  border-color: var(--line-soft);
}

.summary-card h2 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
  font-weight: 800;
}

.summary-description {
  display: -webkit-box;
  min-height: 3.2rem;
  margin: 0;
  overflow: hidden;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.summary-list {
  display: grid;
  gap: 0.65rem;
  padding-top: 0.15rem;
}

.summary-list div {
  display: grid;
  grid-template-columns: minmax(0, 0.8fr) minmax(0, 1fr);
  gap: 0.75rem;
  padding: 0.8rem;
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  background: color-mix(in srgb, var(--card) 92%, var(--foreground) 8%);
}

.summary-list span {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
}

.summary-list strong {
  overflow: hidden;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

@media (max-width: 980px) {
  .create-layout {
    grid-template-columns: 1fr;
  }

  .summary-panel {
    position: static;
  }
}

@media (max-width: 760px) {
  .team-create-page {
    padding: 1rem 1rem 2rem;
  }

  .create-hero {
    flex-direction: column;
    align-items: flex-start;
    padding: 1.2rem;
  }

  .create-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .identity-panel,
  .contact-grid {
    grid-template-columns: 1fr;
  }

  .form-actions {
    position: static;
    flex-direction: column-reverse;
  }
}
</style>
