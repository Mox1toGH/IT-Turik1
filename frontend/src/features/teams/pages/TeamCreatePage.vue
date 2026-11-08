<template>
  <section class="team-create-page page-shell">
    <page-back-link to="/teams" label="Back to teams" />
    <header class="create-hero">
      <div>
        <p class="section-eyebrow">Teams</p>
        <h1>Create new team</h1>
        <p class="section-subtitle">Add the team details and choose members to invite.</p>
      </div>
    </header>

    <form class="team-form" @submit.prevent="teamForm.handleFormSubmit">
      <ui-card class="team-form-panel">
        <ui-section
          title="Identity"
          description="Add the essentials people will see in the team directory."
        >
          <div class="identity-grid">
            <label class="form-item">
              <p class="form-label">Team name</p>
              <ui-input
                v-model="teamForm.form.fields.value.name"
                :is-invalid="!!teamForm.form.errors.value.name"
                required
                placeholder="Enter team name"
                @blur="teamForm.form.validateField('name')"
              />
              <small v-if="teamForm.form.errors.value.name" class="text-error">{{
                teamForm.form.errors.value.name
              }}</small>
            </label>

            <label class="form-item">
              <p class="form-label">Team email</p>
              <ui-input
                v-model="teamForm.form.fields.value.email"
                :is-invalid="!!teamForm.form.errors.value.email"
                type="email"
                required
                placeholder="team@example.com"
                @blur="teamForm.form.validateField('email')"
              />
              <small v-if="teamForm.form.errors.value.email" class="text-error">{{
                teamForm.form.errors.value.email
              }}</small>
            </label>

            <label class="form-item">
              <p class="form-label">Organization</p>
              <ui-input
                v-model="teamForm.form.fields.value.organization"
                :is-invalid="!!teamForm.form.errors.value.organization"
                placeholder="School, company, or community"
                @blur="teamForm.form.validateField('organization')"
              />
              <small v-if="teamForm.form.errors.value.organization" class="text-error">{{
                teamForm.form.errors.value.organization
              }}</small>
            </label>

            <label class="form-label toggle-field">
              <span>Team visibility</span>
              <div class="visibility-control">
                <span class="visibility-label">Private</span>
                <ui-switch
                  v-model="teamForm.form.fields.value.is_public"
                  :aria-checked="teamForm.form.fields.value.is_public ? 'true' : 'false'"
                  :aria-label="`Team visibility: ${teamForm.form.fields.value.is_public ? 'Public' : 'Private'}`"
                  @blur="teamForm.form.validateField('is_public')"
                />
                <span class="visibility-label">Public</span>
              </div>
              <small v-if="teamForm.form.errors.value.is_public" class="text-error">{{
                teamForm.form.errors.value.is_public
              }}</small>
            </label>
          </div>
        </ui-section>
      </ui-card>

      <ui-card class="team-form-panel">
        <ui-section title="Contact" description="Add optional handles for quick communication.">
          <div class="contact-grid">
            <label class="form-item">
              <p class="form-label">Telegram</p>
              <ui-input
                v-model="teamForm.form.fields.value.contact_telegram"
                :is-invalid="!!teamForm.form.errors.value.contact_telegram"
                placeholder="@team_username"
                title="Telegram username: 5-32 characters, start with a letter, letters/digits/_"
                @blur="teamForm.form.validateField('contact_telegram')"
              />
              <small v-if="teamForm.form.errors.value.contact_telegram" class="text-error">{{
                teamForm.form.errors.value.contact_telegram
              }}</small>
            </label>

            <label class="form-item">
              <p class="form-label">Discord</p>
              <ui-input
                v-model="teamForm.form.fields.value.contact_discord"
                :is-invalid="!!teamForm.form.errors.value.contact_discord"
                placeholder="team.username"
                title="Discord username: 2-32 characters, letters/digits/._ with optional #1234"
                @blur="teamForm.form.validateField('contact_discord')"
              />
              <small v-if="teamForm.form.errors.value.contact_discord" class="text-error">{{
                teamForm.form.errors.value.contact_discord
              }}</small>
            </label>
          </div>
        </ui-section>
      </ui-card>

      <ui-card class="team-form-panel">
        <ui-section title="Members" description="Invite members now, or add them later.">
          <label class="form-item">
            <p class="form-label">Initial members</p>
            <ui-select
              v-model="teamForm.form.fields.value.member_ids!"
              :isLoading="teamForm.isLoadingUsers.value"
              :isError="isLoadingError"
              :error="'Could not load users.'"
              :multiple="true"
              :options="
                teamForm.createCandidateUsers.value?.map((u) => ({
                  value: u.id,
                  label: `${u.username} (${u.email})`,
                }))
              "
              placeholder="Select members"
              @blur="teamForm.form.validateField('member_ids')"
            />
            <small v-if="teamForm.form.errors.value.member_ids" class="text-error">{{
              teamForm.form.errors.value.member_ids
            }}</small>
          </label>
        </ui-section>
      </ui-card>

      <div class="form-actions">
        <ui-button :disabled="teamForm.isCreatingTeam.value" type="submit" size="lg">
          <LoaderCircle class="animate-spin" v-if="teamForm.isCreatingTeam.value" />
          {{ teamForm.isCreatingTeam.value ? 'Creating...' : 'Create team' }}
        </ui-button>
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import PageBackLink from '@/components/shared/PageBackLink.vue'
import UiCard from '@/components/ui/UiCard'
import UiInput from '@/components/ui/UiInput'
import UiSection from '@/components/ui/UiSection'
import { LoaderCircle } from 'lucide-vue-next'
import UiSelect from '@/components/ui/UiSelect'
import UiSwitch from '@/components/ui/UiSwitch'
import { useTeamCreateForm } from '../composables/useTeamCreateForm'

const teamForm = useTeamCreateForm()

const isLoadingError = computed(
  () => teamForm.isLoadingError.value && teamForm.createCandidateUsers.value === undefined,
)
</script>

<style scoped>
.team-create-page {
  gap: 2rem;
}

.create-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
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

.team-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  min-width: 0;
  width: 100%;
}

.form-label {
  margin: 0;
}

.identity-grid,
.contact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.contact-grid {
  min-width: 0;
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

.form-actions {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 760px) {
  .team-create-page {
    padding: 1rem 1rem 2rem;
  }

  .create-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .create-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .form-actions {
    flex-direction: column-reverse;
    align-items: stretch;
  }
}
</style>
