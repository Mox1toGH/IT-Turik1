<template>
  <section class="page-shell news-page">
    <ui-card>
      <template #header>
        <div class="news-hero">
          <div class="top-header">
            <p class="section-eyebrow">News</p>
            <ui-badge>Total posts: {{ totalNews }}</ui-badge>
          </div>
          <div class="title-row">
            <h1>News board</h1>
          </div>
          <div class="subtitle-row">
            <p class="section-subtitle">Important updates, announcements, and platform changes.</p>
            <div class="create-news-action" v-if="canManageNews">
              <ui-button @click="isCreateOpen = true" variant="secondary">Create news</ui-button>
            </div>
          </div>
        </div>
      </template>
    </ui-card>

    <ui-card v-if="isLoadingNews">
      <template #header>
        <div class="section-head">
          <h2>Latest news</h2>
        </div>
      </template>
      <ui-skeleton-loader :loading="isLoadingNews">
        <template #skeleton>
          <div class="news-grid">
            <ui-card class="news-item" v-for="i in 2" :key="i">
              <template #header>
                <ui-skeleton variant="rect" width="65%" />
                <ui-skeleton variant="rect" width="45%" />
              </template>
              <ui-skeleton variant="rect" height="90px" width="100%" />
            </ui-card>
          </div>
        </template>
      </ui-skeleton-loader>
    </ui-card>

    <ui-card v-else-if="isLoadingError" :isError="true">
      <template #error>
        <div class="error-box">
          <p>Failed to fetch news (code: {{ parsedError?.code }})</p>
        </div>
      </template>
    </ui-card>

    <ui-card v-else-if="!newsItems.length">
      <template #header>
        <div class="section-head">
          <h2>Latest news</h2>
        </div>
      </template>
      <p class="text-muted">No news yet.</p>
    </ui-card>

    <ui-card v-else>
      <template #header>
        <div class="section-head">
          <h2>Latest news</h2>
          <span class="text-muted">{{ totalNews }} published</span>
        </div>
      </template>
      <div class="news-grid">
        <ui-card v-for="item in newsItems" :key="item.id" class="news-item">
          <template #header>
            <div class="news-item-head">
              <h3>{{ item.title }}</h3>
              <p class="meta">
                {{ item.created_by_name || 'Unknown author' }} · {{ formatDate(item.created_at) }}
              </p>
            </div>
          </template>

          <news-content-viewer :content="item.content" />
        </ui-card>
      </div>
      <div v-if="totalPages > 1" class="pagination-controls">
        <ui-button size="sm" variant="secondary" :disabled="currentPage === 1" @click="prevPage">
          Previous
        </ui-button>
        <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
        <ui-button
          size="sm"
          variant="secondary"
          :disabled="currentPage === totalPages"
          @click="nextPage"
        >
          Next
        </ui-button>
      </div>
    </ui-card>

    <ui-modal v-if="canManageNews" v-model="isCreateOpen" maxWidth="760px" :close-on-backdrop="!isCreating">
      <template #title>Create news</template>

      <div class="section-head">
        <span class="text-muted">Admins and organizers only</span>
      </div>

      <form class="create-form" @submit.prevent="handleCreate">
        <label class="form-item">
          <span class="form-label">Title</span>
          <ui-input
            v-model="form.fields.value.title"
            placeholder="Enter news title"
            :isInvalid="!!form.errors.value.title"
            @blur="form.validateField('title')"
          />
          <small v-if="form.errors.value.title" class="text-error">{{ form.errors.value.title }}</small>
        </label>

        <label class="form-item">
          <span class="form-label">Content</span>
          <editor-modal
            v-model="form.fields.value.content"
            title="News content"
            addText="Add content"
            editText="Edit content"
            ariaLabel="News content editor"
            @blur="form.validateField('content')"
          />
          <small v-if="form.errors.value.content" class="text-error">{{
            form.errors.value.content
          }}</small>
        </label>

        <ui-button type="submit" :disabled="isCreating">
          <loading-icon v-if="isCreating" />
          <span>Create</span>
        </ui-button>
      </form>
    </ui-modal>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { JSONContent } from '@tiptap/core'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import EditorModal from '@/features/tournaments/components/create-round/modals/EditorModal.vue'
import NewsContentViewer from '../components/NewsContentViewer.vue'
import { useProfile } from '@/api/queries/accounts'
import { useCreateNews, useNewsList } from '@/api/queries/news'
import { useForm } from '@/composables/useForm'
import { CreateNewsSchema } from '@/schemas/news.schema'
import { parseApiError } from '@/api/errors'
import { useNotification } from '@/composables/useNotification'

interface CreateNewsForm {
  title: string
  content: JSONContent | null
}

const form = useForm<CreateNewsForm>(CreateNewsSchema, {
  title: '',
  content: null,
})

const { showNotification } = useNotification()
const { data: user } = useProfile()
const canManageNews = computed(() => ['admin', 'organizer'].includes(user.value?.role ?? ''))
const isCreateOpen = ref(false)
const currentPage = ref(1)
const pageSize = 10

const {
  data: news,
  isLoading: isLoadingNews,
  isLoadingError,
  error: newsError,
} = useNewsList({ page: currentPage, pageSize })
const parsedError = computed(() => parseApiError(newsError.value))
const newsItems = computed(() => news.value?.results ?? [])
const totalNews = computed(() => news.value?.count ?? 0)
const totalPages = computed(() => Math.max(1, Math.ceil(totalNews.value / pageSize)))

const { mutate: createNews, isPending: isCreating } = useCreateNews()

function handleCreate() {
  if (!form.validate()) return

  createNews(
    {
      body: {
        title: form.fields.value.title,
        content: form.fields.value.content as JSONContent,
      },
    },
    {
      onSuccess() {
        form.hydrate({ title: '', content: null })
        isCreateOpen.value = false
        showNotification('News created successfully.', 'success')
      },
      onError(error) {
        const parsed = parseApiError(error)
        for (const [field, errors] of Object.entries(parsed?.details || {})) {
          form.setError(field as keyof CreateNewsForm, errors?.[0] ?? 'Invalid value')
        }
        showNotification(parsed?.message, 'error')
      },
    },
  )
}

function formatDate(value: string | Date) {
  const date = typeof value === 'string' ? new Date(value) : value
  return date.toLocaleString()
}

function prevPage() {
  if (currentPage.value > 1) currentPage.value -= 1
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value += 1
}
</script>

<style scoped>
.news-page {
  display: grid;
  gap: 1rem;
}

.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
}

.create-news-action {
  display: flex;
  justify-content: flex-end;
}

.news-hero h1 {
  margin: 0;
}

.subtitle-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
}

.subtitle-row .section-subtitle {
  margin: 0;
}

@media (max-width: 720px) {
  .title-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .subtitle-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .create-news-action {
    justify-content: flex-start;
  }
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
}

.create-form {
  display: grid;
  gap: 0.8rem;
}

.news-grid {
  display: grid;
  gap: 0.9rem;
  grid-template-columns: 1fr;
}

.news-item {
  display: grid;
  gap: 0.8rem;
  padding: 0.95rem;
  background: var(--muted);
}

.news-item-head h3 {
  margin: 0;
  font-family: var(--font-display);
}

.meta {
  margin: 0.35rem 0 0;
  color: var(--muted-foreground);
  font-size: 0.92rem;
}

.error-box {
  display: flex;
  height: 140px;
  justify-content: center;
  align-items: center;
}

.text-error {
  color: var(--destructive);
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.95rem;
}

.page-info {
  font-size: 0.92rem;
  color: var(--muted-foreground);
}
</style>
