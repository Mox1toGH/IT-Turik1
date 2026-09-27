<template>
  <ui-card class="panel certs-panel">
    <template #header>
      <div class="panel-head">
        <div class="panel-title-row">
          <h2 class="panel-title">Issued Certificates</h2>
          <form class="search-box" @submit.prevent="handleSearch">
            <ui-input
              v-model="searchQuery"
              placeholder="Search by full name or verification code..."
              size="sm"
              class="ui-input-full"
            />
            <ui-button type="submit" size="sm" variant="secondary">Search</ui-button>
          </form>
        </div>
        <span class="panel-note">Global management</span>
      </div>
    </template>

    <ui-skeleton-loader :loading="isCertsLoading">
      <template #skeleton
        ><div class="certs-list-skeleton">
          <ui-skeleton v-for="i in 4" :key="i" variant="rect" width="100%" height="80px" /></div
      ></template>
      <p v-if="isCertsError" class="text-muted">Failed to load certificates.</p>
      <p v-else-if="!certsResponse?.results?.length" class="text-muted">No certificates found.</p>
      <div v-else class="certs-list">
        <div v-for="cert in certsResponse.results" :key="cert.id" class="cert-item">
          <div class="cert-info-main">
            <div class="cert-title-row">
              <strong>{{ cert.tournament_name || 'Tournament' }}</strong
              ><span class="cert-num">#{{ cert.certificate_number || cert.unique_code }}</span>
            </div>
            <div class="cert-details-grid">
              <span><strong>User:</strong> {{ cert.full_name }}</span>
              <span><strong>Placement:</strong> {{ cert.placement || '-' }}</span>
              <span><strong>Team:</strong> {{ cert.team_name || '-' }}</span>
              <span><strong>Date:</strong> {{ formatDate(cert.created_at) }}</span>
            </div>
          </div>
          <div class="cert-item-actions">
            <a :href="cert.certificate_url" target="_blank" class="action-btn-mini" title="View PDF"
              ><ui-badge variant="gray">PDF</ui-badge></a
            >
            <button class="action-btn-mini" title="Edit certificate" @click="openEditCert(cert)">
              <EditIcon class="icon-mini" />
            </button>
            <button
              class="action-btn-mini delete"
              title="Delete certificate"
              @click="openDeleteCert(cert.unique_code)"
            >
              <TrashIcon class="icon-mini" />
            </button>
          </div>
        </div>

        <ui-pagination
          v-if="totalCertPages > 1"
          v-model="certsPage"
          :total-items="certsResponse?.count || 0"
          :page-size="certsPageSize"
          :show-summary="false"
        />
      </div>
    </ui-skeleton-loader>
  </ui-card>

  <EditCertificateModal
    v-model:cert="certToEdit"
    :user-options="userOptions"
    :tournament-options="tournamentOptions"
    :team-options="teamOptions"
    :template-options="templateOptions"
  />

  <!-- <UiConfirmModal
    v-model="isDeleteModalOpen"
    title="Delete Template"
    message="Are you sure you want to delete this template? This action cannot be undone."
    confirmText="Delete"
    confirmVariant="danger"
    :loading="isDeleting"
    @confirm="onDeleteConfirm"
  /> -->

  <UiConfirmModal
    v-model="isDeleteCertModalOpen"
    title="Delete Certificate"
    message="Are you sure you want to delete this certificate? This action cannot be undone."
    confirmText="Delete"
    confirmVariant="danger"
    :loading="isDeletingCert"
    @confirm="onDeleteCertConfirm"
  />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiPagination from '@/components/ui/UiPagination.vue'
import TrashIcon from '@/icons/TrashIcon.vue'
import EditIcon from '@/icons/EditIcon.vue'
import { useDeleteCertificate, useListCertificates } from '@/api/certificates/certificates'
import type { Certificate } from '@/api/.ts.schemas'
import { useNotification } from '@/composables/useNotification'
import UiConfirmModal from '@/components/ui/UiConfirmModal.vue'

defineProps<{
  userOptions: Array<{ value: number; label: string }>
  tournamentOptions: Array<{ value: number; label: string }>
  teamOptions: Array<{ value: number; label: string }>
  templateOptions: Array<{ value: number; label: string }>
}>()

const { showNotification } = useNotification()

const certsPage = ref(1)
const certsPageSize = 10
const certsSearch = ref('')
const searchQuery = ref('')

const isDeleteCertModalOpen = ref(false)
const certToDeleteCode = ref<string | null>(null)

const openDeleteCert = (certCode: Certificate['unique_code']) => {
  certToDeleteCode.value = certCode
  isDeleteCertModalOpen.value = true
}

const { mutateAsync: deleteCert, isPending: isDeletingCert } = useDeleteCertificate()

const onDeleteCertConfirm = async () => {
  if (!certToDeleteCode.value) return

  try {
    await deleteCert({ uniqueCode: certToDeleteCode.value })
    showNotification('Certificate deleted successfully.', 'success')
    isDeleteCertModalOpen.value = false
  } catch {
    showNotification('Failed to delete certificate.', 'error')
  }
}

const certToEdit = ref<Certificate | null>(null)
const openEditCert = (cert: Certificate) => {
  certToEdit.value = cert
}

const {
  data: certsResponse,
  isLoading: isCertsLoading,
  isLoadingError: isCertsError,
} = useListCertificates(
  computed(() => ({ page: certsPage.value, pageSize: certsPageSize, search: certsSearch.value })),
)

const totalCertPages = computed(() => {
  const total = certsResponse.value?.count || 0
  return Math.max(1, Math.ceil(total / certsPageSize))
})

const handleSearch = () => {
  certsSearch.value = searchQuery.value
  certsPage.value = 1
}

const formatDate = (date: string) => (!date ? '-' : new Date(date).toLocaleDateString('uk-UA'))
</script>

<style scoped>
.panel {
  background: var(--muted);
  color: var(--muted-foreground);
}
.certs-panel {
  grid-column: 1 / -1;
}
.panel-head {
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}
.panel-title-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}
.search-box {
  max-width: 450px;
  flex: 1;
  display: flex;
  gap: 8px;
}
.ui-input-full {
  width: 100%;
}
.certs-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.cert-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 12px;
  background: var(--background);
  border: 1px solid var(--line-soft);
  gap: 1rem;
}
.cert-info-main {
  flex: 1;
  min-width: 0;
}
.cert-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}
.cert-num {
  font-size: 0.8rem;
  color: var(--color-gray-500);
}
.cert-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 4px 12px;
  font-size: 0.85rem;
}
.cert-details-grid strong {
  color: var(--color-gray-500);
  font-weight: 500;
}
.cert-item-actions {
  display: flex;
  gap: 6px;
}
.certs-list-skeleton {
  display: grid;
  gap: 10px;
}

@media (max-width: 900px) {
  .panel-title-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .search-box {
    max-width: 100%;
    width: 100%;
  }
  .cert-item {
    flex-direction: column;
    align-items: flex-start;
  }
  .cert-item-actions {
    width: 100%;
    justify-content: flex-end;
    border-top: 1px solid var(--line-soft);
    padding-top: 10px;
  }
}
</style>
