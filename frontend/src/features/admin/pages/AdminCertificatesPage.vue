<template>
  <section class="page-shell">
    <section class="page-section certificates-section">
      <header class="page-header">
        <div class="head">
          <div>
            <p class="section-eyebrow">Admin</p>
            <h1 class="section-title">Certificates</h1>
            <p class="section-subtitle">
              Create certificates for users, manage template library, and verify certificate codes.
            </p>
          </div>
          <ui-button as-link to="/admin" variant="secondary">Back to Admin hub</ui-button>
        </div>
      </header>

      <div class="layout">
        <AdminCreateCertificateCard
          :user-options="userOptions"
          :tournament-options="tournamentOptions"
          :team-options="teamOptions"
          :template-options="templateOptions"
        />

        <TemplatesList />

        <CertificateVerifyCard />

        <IssuedCertificatesCard
          :user-options="userOptions"
          :tournament-options="tournamentOptions"
          :team-options="teamOptions"
          :template-options="templateOptions"
        />
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'
import AdminCreateCertificateCard from '@/features/admin/components/certificates/AdminCreateCertificateCard.vue'
import TemplatesList from '@/features/admin/components/certificates/TemplatesList.vue'
import CertificateVerifyCard from '@/features/admin/components/certificates/CertificateVerifyCard.vue'
import IssuedCertificatesCard from '@/features/admin/components/certificates/IssuedCertificatesCard.vue'
import { useListUsers } from '@/api/accounts/accounts'
import { useListTeams } from '@/api/teams/teams'
import { useListTournaments } from '@/api/tournaments/tournaments'
import { useListCertificateTemplates } from '@/api/certificates/certificates'

const { data: users } = useListUsers()
const { data: teams } = useListTeams()
const { data: tournamentsResponse } = useListTournaments(
  computed(() => ({
    page: 1,
    page_size: 200,
    searchQuery: '',
  })),
)

const { data: allTemplatesResponse } = useListCertificateTemplates({ nopage: 'true' })

const userOptions = computed(() =>
  (users.value || []).map((u) => ({
    value: u.id,
    label: `${u.full_name || u.username} (#${u.id})`,
  })),
)

const tournamentOptions = computed(() =>
  (tournamentsResponse.value?.data || []).map((t) => ({
    value: t.id,
    label: `${t.name} (#${t.id})`,
  })),
)

const teamOptions = computed(() => [
  { value: 0, label: 'No team' },
  ...(teams.value || []).map((t) => ({ value: t.id, label: `${t.name} (#${t.id})` })),
])

const templateOptions = computed(() => [
  { value: 0, label: 'Default template' },
  ...(allTemplatesResponse.value?.results || []).map((t) => ({
    value: t.id,
    label: t.is_default ? `${t.name} (default)` : t.name,
  })),
])
</script>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

.layout {
  display: grid;
  gap: 0.85rem;
  margin-top: 0.6rem;
}

@media (max-width: 900px) {
  .head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
