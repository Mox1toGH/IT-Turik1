<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div class="head">
          <div>
            <p class="section-eyebrow">Certificates</p>
            <h1 class="section-title">My certificates</h1>
          </div>
          <div class="head-actions">
            <ui-button variant="secondary" @click="openVerifyPage">Verify certificate</ui-button>
            <ui-button variant="secondary" @click="goBack">Back to profile</ui-button>
          </div>
        </div>
      </template>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <div style="display: grid; gap: 8px">
            <ui-skeleton v-for="i in 3" :key="i" variant="rect" width="100%" />
          </div>
        </template>

        <p v-if="isLoadingError && !isNotFoundError" class="text-muted">
          Failed to load certificates (code: {{ error?.code ?? 'unknown' }})
        </p>

        <p v-else-if="!certificates?.results?.length || isNotFoundError" class="text-muted">
          You do not have certificates yet.
        </p>

        <div v-else class="list">
          <ui-card v-for="item in certificates.results" :key="item.id" class="cert-card">
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
              <p class="verification-code">
                <strong>Verification code:</strong> {{ item.unique_code }}
              </p>
            </div>

            <div class="actions">
              <a
                :href="item.certificate_url"
                target="_blank"
                rel="noopener noreferrer"
                class="link-btn"
              >
                View PDF
              </a>
              <button
                type="button"
                class="link-btn secondary"
                @click="
                  downloadCertificate(
                    item.certificate_url,
                    item.certificate_number || item.unique_code,
                  )
                "
              >
                Download PDF
              </button>
            </div>
          </ui-card>

          <div v-if="totalPages > 1" class="pagination">
            <ui-button variant="secondary" :disabled="currentPage === 1" @click="prevPage"
              >Prev</ui-button
            >
            <span class="page-info">Page {{ currentPage }} / {{ totalPages }}</span>
            <ui-button variant="secondary" :disabled="currentPage === totalPages" @click="nextPage"
              >Next</ui-button
            >
          </div>
        </div>
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import { useListCertificates } from '@/api/certificates/certificates'
import { AXIOS_INSTANCE } from '@/lib/apiClient'
const router = useRouter()
const currentPage = ref(1)
const pageSize = 6
const {
  data: certificates,
  isLoading,
  isLoadingError,
  error,
} = useListCertificates(
  computed(() => ({
    page: currentPage.value,
    pageSize,
  })),
)
const isNotFoundError = computed(() => String(error.value?.code || '') === '404')

const totalPages = computed(() => {
  const total = certificates.value?.count || 0
  return Math.max(1, Math.ceil(total / pageSize))
})

const goBack = () => {
  router.push('/profile')
}

const openVerifyPage = () => {
  router.push('/certificates/verify')
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('uk-UA')
}

const downloadCertificate = async (url: string, code: string) => {
  const response = await AXIOS_INSTANCE.get(url, { responseType: 'blob' })
  const blobUrl = window.URL.createObjectURL(response.data)
  const link = document.createElement('a')
  link.href = blobUrl
  link.download = `certificate-${code}.pdf`
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(blobUrl)
}

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value -= 1
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value += 1
}
</script>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.head-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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

.verification-code {
  grid-column: 1 / -1;
  word-break: break-all;
}

.actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 6px;
}

.page-info {
  font-weight: 600;
  color: var(--color-gray-600);
}

.link-btn {
  border: 1px solid var(--line-soft);
  border-radius: 10px;
  padding: 8px 12px;
  text-decoration: none;
  font-weight: 600;
  color: var(--foreground);
  background: var(--background);
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease;
}

.link-btn.secondary {
  color: var(--muted-foreground);
}

.link-btn:hover {
  background: color-mix(in srgb, var(--background) 88%, var(--foreground));
  border-color: color-mix(in srgb, var(--line-soft) 65%, var(--foreground));
}

@media (max-width: 760px) {
  .head {
    flex-direction: column;
    align-items: flex-start;
  }

  .head-actions {
    width: 100%;
  }

  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
