<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div class="head">
          <div>
            <p class="section-eyebrow">Certificates</p>
            <h1 class="section-title">My certificates</h1>
          </div>
          <ui-button variant="secondary" @click="goBack">Back to profile</ui-button>
        </div>
      </template>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <div style="display: grid; gap: 8px">
            <ui-skeleton v-for="i in 3" :key="i" variant="rect" width="100%" />
          </div>
        </template>

        <p v-if="isLoadingError && !isNotFoundError" class="text-muted">
          Failed to load certificates (code: {{ apiError?.code ?? 'unknown' }})
        </p>

        <p v-else-if="!certificates?.length || isNotFoundError" class="text-muted">
          You do not have certificates yet.
        </p>

        <div v-else class="list">
          <ui-card v-for="item in certificates" :key="item.id" class="cert-card">
            <template #header>
              <div class="row-head">
                <strong>{{ item.tournament_name || 'Tournament' }}</strong>
                <span class="meta">#{{ item.certificate_number }}</span>
              </div>
            </template>

            <div class="grid">
              <p><strong>Name:</strong> {{ item.full_name || '-' }}</p>
              <p><strong>Placement:</strong> {{ item.placement || '-' }}</p>
              <p><strong>Team:</strong> {{ item.team_name || '-' }}</p>
              <p><strong>Date:</strong> {{ formatDate(item.created_at) }}</p>
            </div>

            <div class="actions">
              <a :href="item.certificate_url" target="_blank" rel="noopener noreferrer" class="link-btn">
                View PDF
              </a>
              <a
                :href="item.certificate_url"
                :download="`certificate-${item.certificate_number || item.unique_code}.pdf`"
                class="link-btn secondary"
              >
                Download PDF
              </a>
            </div>
          </ui-card>
        </div>
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import { useMyCertificates } from '@/api/queries/certificates'
import { parseApiError } from '@/api/errors'

const router = useRouter()
const { data: certificates, isLoading, isLoadingError, error } = useMyCertificates()
const apiError = computed(() => parseApiError(error.value))
const isNotFoundError = computed(() => apiError.value?.code === 404)

const goBack = () => {
  router.push('/profile')
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('uk-UA')
}
</script>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.list {
  display: grid;
  gap: 12px;
}

.cert-card {
  background: var(--muted);
  color: var(--muted-foreground);
}

.row-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.meta {
  color: var(--color-gray-500);
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 8px;
}

.grid p {
  margin: 0;
}

.actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.link-btn {
  border: 1px solid var(--line-soft);
  border-radius: 10px;
  padding: 8px 12px;
  text-decoration: none;
  font-weight: 600;
  color: var(--brand-700);
  background: white;
}

.link-btn.secondary {
  color: var(--color-gray-700);
}

@media (max-width: 760px) {
  .head {
    flex-direction: column;
    align-items: flex-start;
  }

  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
