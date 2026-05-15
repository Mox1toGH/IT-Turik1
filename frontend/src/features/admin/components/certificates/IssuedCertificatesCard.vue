<template>
  <ui-card class="panel certs-panel">
    <template #header>
      <div class="panel-head">
        <div class="panel-title-row">
          <h2 class="panel-title">Issued Certificates</h2>
          <form class="search-box" @submit.prevent="$emit('search')">
            <ui-input v-model="query" placeholder="Search by full name or verification code..." size="sm" class="ui-input-full" />
            <ui-button type="submit" size="sm" variant="secondary">Search</ui-button>
          </form>
        </div>
        <span class="panel-note">Global management</span>
      </div>
    </template>

    <ui-skeleton-loader :loading="isCertsLoading">
      <template #skeleton><div class="certs-list-skeleton"><ui-skeleton v-for="i in 4" :key="i" variant="rect" width="100%" height="80px" /></div></template>
      <p v-if="isCertsError" class="text-muted">Failed to load certificates.</p>
      <p v-else-if="!certsResponse?.results?.length" class="text-muted">No certificates found.</p>
      <div v-else class="certs-list">
        <div v-for="cert in certsResponse.results" :key="cert.id" class="cert-item">
          <div class="cert-info-main">
            <div class="cert-title-row"><strong>{{ cert.tournament_name || 'Tournament' }}</strong><span class="cert-num">#{{ cert.certificate_number || cert.unique_code }}</span></div>
            <div class="cert-details-grid">
              <span><strong>User:</strong> {{ cert.full_name || cert.username }}</span>
              <span><strong>Placement:</strong> {{ cert.placement || '-' }}</span>
              <span><strong>Team:</strong> {{ cert.team_name || '-' }}</span>
              <span><strong>Date:</strong> {{ formatDate(cert.created_at) }}</span>
            </div>
          </div>
          <div class="cert-item-actions">
            <a :href="cert.certificate_url" target="_blank" class="action-btn-mini" title="View PDF"><ui-badge variant="gray">PDF</ui-badge></a>
            <button class="action-btn-mini" title="Edit certificate" @click="$emit('edit', cert)"><EditIcon class="icon-mini" /></button>
            <button class="action-btn-mini delete" title="Delete certificate" @click="$emit('delete', cert.unique_code)"><TrashIcon class="icon-mini" /></button>
          </div>
        </div>

        <div v-if="totalCertPages > 1" class="pagination">
          <ui-button size="sm" variant="secondary" :disabled="certsPage === 1" @click="$emit('update:certsPage', certsPage - 1)">Prev</ui-button>
          <span class="page-info">Page {{ certsPage }} / {{ totalCertPages }}</span>
          <ui-button size="sm" variant="secondary" :disabled="certsPage === totalCertPages" @click="$emit('update:certsPage', certsPage + 1)">Next</ui-button>
        </div>
      </div>
    </ui-skeleton-loader>
  </ui-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import TrashIcon from '@/icons/TrashIcon.vue'
import EditIcon from '@/icons/EditIcon.vue'

const props = defineProps<{ searchQuery: string; certsPage: number; totalCertPages: number; certsResponse: any; isCertsLoading: boolean; isCertsError: boolean }>()
const emit = defineEmits<{
  (e: 'update:searchQuery', value: string): void
  (e: 'search'): void
  (e: 'update:certsPage', value: number): void
  (e: 'edit', cert: any): void
  (e: 'delete', code: string): void
}>()

const query = computed({ get: () => props.searchQuery, set: (v) => emit('update:searchQuery', v) })

const formatDate = (date: string) => (!date ? '-' : new Date(date).toLocaleDateString('uk-UA'))
</script>

<style scoped>
.panel { background: var(--muted); color: var(--muted-foreground); }
.certs-panel { grid-column: 1 / -1; }
.panel-head { display: flex; justify-content: space-between; align-items: center; gap: 0.75rem; }
.panel-title { margin: 0; font-size: 1rem; }
.panel-note { font-size: 0.8rem; color: var(--color-gray-500); }
.panel-title-row { display: flex; align-items: center; gap: 1rem; flex: 1; }
.search-box { max-width: 450px; flex: 1; display: flex; gap: 8px; }
.ui-input-full { width: 100%; }
.certs-list { display: flex; flex-direction: column; gap: 10px; }
.cert-item { display: flex; justify-content: space-between; align-items: center; padding: 12px; border-radius: 12px; background: var(--background); border: 1px solid var(--line-soft); gap: 1rem; }
.cert-info-main { flex: 1; min-width: 0; }
.cert-title-row { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.cert-num { font-size: 0.8rem; color: var(--color-gray-500); }
.cert-details-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 4px 12px; font-size: 0.85rem; }
.cert-details-grid strong { color: var(--color-gray-500); font-weight: 500; }
.cert-item-actions { display: flex; gap: 6px; }
.action-btn-mini { background: none; border: none; color: var(--muted-foreground); padding: 4px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.action-btn-mini:hover { background: var(--secondary); color: var(--foreground); }
.action-btn-mini.delete:hover { background: #fee2e2; color: #991b1b; }
.icon-mini { width: 14px; height: 14px; }
.certs-list-skeleton { display: grid; gap: 10px; }
.pagination { display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 16px; }
.page-info { font-weight: 600; font-size: 0.9rem; color: var(--color-gray-600); }
@media (max-width: 900px) {
  .panel-title-row { flex-direction: column; align-items: flex-start; }
  .search-box { max-width: 100%; width: 100%; }
  .cert-item { flex-direction: column; align-items: flex-start; }
  .cert-item-actions { width: 100%; justify-content: flex-end; border-top: 1px solid var(--line-soft); padding-top: 10px; }
}
</style>
