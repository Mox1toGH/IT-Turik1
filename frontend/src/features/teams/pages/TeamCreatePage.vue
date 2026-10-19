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
      <form class="team-form" @submit.prevent="teamForm.handleFormSubmit">
        <team-identity-fields :form="teamForm.form" />

        <team-contact-fields :form="teamForm.form" />

        <ui-section
          title="Members"
          description="Invite initial members now, or leave this empty for later."
        >
          <label class="form-item">
            <p class="form-label">Add initial members</p>
            <ui-select
              v-model="teamForm.form.fields.value.member_ids!"
              :isLoading="teamForm.isLoadingUsers.value"
              :isError="isLoadingError || !!teamForm.form.errors.value.member_ids"
              :error="`Error while fetching users`"
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

        <div class="form-actions">
          <ui-button asLink variant="secondary" size="lg" to="/teams">Cancel</ui-button>
          <ui-button :disabled="teamForm.isCreatingTeam.value" type="submit" size="lg">
            <loading-icon v-if="teamForm.isCreatingTeam.value" />
            {{ teamForm.isCreatingTeam.value ? 'Creating...' : 'Create team' }}
          </ui-button>
        </div>
      </form>

      <team-create-summary
        :selected-members-count="teamForm.selectedMembersCount.value"
        :contact-summary="teamForm.contactSummary.value"
        :team-name="teamForm.form.fields.value.name"
        :organization="teamForm.form.fields.value.organization"
        :email="teamForm.form.fields.value.email"
        :is-public="teamForm.form.fields.value.is_public"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiButton from '@/components/ui/UiButton'
import UiSection from '@/components/ui/UiSection'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import UiSelect from '@/components/ui/UiSelect'
import TeamIdentityFields from '../components/team-create/TeamIdentityFields.vue'
import TeamContactFields from '../components/team-create/TeamContactFields.vue'
import TeamCreateSummary from '../components/team-create/TeamCreateSummary.vue'
import { useTeamCreateForm } from '../composables/useTeamCreateForm'

const teamForm = useTeamCreateForm()

const isLoadingError = computed(() => Boolean(teamForm.isLoadingError))
</script>

<style scoped>
.team-create-page {
  gap: 2rem;
}

.create-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
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

.create-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.38fr);
  gap: 2rem;
  align-items: start;
}

.team-form {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  min-width: 0;
}

.form-label {
  margin: 0;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

@media (max-width: 980px) {
  .create-layout {
    grid-template-columns: 1fr;
  }
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
