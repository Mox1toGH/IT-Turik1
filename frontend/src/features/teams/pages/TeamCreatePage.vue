<template>
  <section class="team-create-page page-shell">
    <header class="create-hero">
      <div>
        <p class="section-eyebrow">Teams</p>
        <h1>Create new team</h1>
        <p class="section-subtitle">Add the team details and choose members to invite.</p>
      </div>

      <ui-button asLink class="back-link" variant="secondary" to="/teams">
        Back to teams
      </ui-button>
    </header>

    <form class="team-form" @submit.prevent="teamForm.handleFormSubmit">
      <team-identity-fields :form="teamForm.form" />

      <team-contact-fields :form="teamForm.form" />

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
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiSection from '@/components/ui/UiSection'
import { LoaderCircle } from 'lucide-vue-next'
import UiSelect from '@/components/ui/UiSelect'
import TeamIdentityFields from '../components/team-create/TeamIdentityFields.vue'
import TeamContactFields from '../components/team-create/TeamContactFields.vue'
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

.back-link {
  flex: 0 0 auto;
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
