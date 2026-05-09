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
              <div>
                <h3>{{ item.title }}</h3>
                <p class="meta">
                  {{ item.created_by_name || 'Unknown author' }} · {{ formatDate(item.created_at) }}
                </p>
              </div>
              <div v-if="canModifyNews(item)" class="news-actions">
                <ui-button size="sm" variant="secondary" @click="openEditModal(item)">Edit</ui-button>
                <ui-button size="sm" variant="danger" @click="openDeleteConfirm(item)">Delete</ui-button>
              </div>
            </div>
          </template>

          <div
            class="news-content-wrap"
            :class="{ expanded: isExpanded(item.id) }"
          >
            <news-content-viewer :content="item.content" />
          </div>
          <ui-button
            v-if="isExpandable(item)"
            size="sm"
            variant="secondary"
            @click="toggleExpanded(item.id)"
          >
            {{ isExpanded(item.id) ? 'Show less' : 'Show more' }}
          </ui-button>
        </ui-card>
      </div>
      <div v-if="totalPages > 1" class="pagination-controls">
        <ui-button size="sm" variant="secondary" :disabled="currentPage === 1" @click="prevPage">
          Previous
        </ui-button>
        <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
        <ui-button size="sm" variant="secondary" :disabled="currentPage === totalPages" @click="nextPage">
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
        <label class="notify-row">
          <ui-switch v-model="form.fields.value.send_notification" />
          <span>Send notification to all users</span>
        </label>

        <ui-button type="submit" :disabled="isCreating">
          <loading-icon v-if="isCreating" />
          <span>Create</span>
        </ui-button>
      </form>
    </ui-modal>

    <ui-modal v-if="canManageNews" v-model="isEditOpen" maxWidth="760px" :close-on-backdrop="!isUpdating">
      <template #title>Edit news</template>

      <form class="create-form" @submit.prevent="handleEdit">
        <label class="form-item">
          <span class="form-label">Title</span>
          <ui-input
            v-model="editForm.fields.value.title"
            placeholder="Enter news title"
            :isInvalid="!!editForm.errors.value.title"
            @blur="editForm.validateField('title')"
          />
          <small v-if="editForm.errors.value.title" class="text-error">{{ editForm.errors.value.title }}</small>
        </label>

        <label class="form-item">
          <span class="form-label">Content</span>
          <editor-modal
            v-model="editForm.fields.value.content"
            title="News content"
            addText="Add content"
            editText="Edit content"
            ariaLabel="News content editor"
            @blur="editForm.validateField('content')"
          />
          <small v-if="editForm.errors.value.content" class="text-error">{{
            editForm.errors.value.content
          }}</small>
        </label>
        <label class="notify-row">
          <ui-switch v-model="editForm.fields.value.send_notification" />
          <span>Send notification to all users</span>
        </label>

        <ui-button type="submit" :disabled="isUpdating || !editingNewsId">
          <loading-icon v-if="isUpdating" />
          <span>Save</span>
        </ui-button>
      </form>
    </ui-modal>

    <ui-confirm-modal
      v-model="isDeleteConfirmOpen"
      title="Delete news"
      message="Are you sure you want to delete this news?"
      confirmText="Delete"
      confirmVariant="danger"
      :loading="isDeleting"
      @confirm="handleDelete"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { JSONContent } from '@tiptap/core'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiConfirmModal from '@/components/ui/UiConfirmModal.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSwitch from '@/components/ui/UiSwitch.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import EditorModal from '@/features/tournaments/components/create-round/modals/EditorModal.vue'
import NewsContentViewer from '../components/NewsContentViewer.vue'
import { useProfile } from '@/api/queries/accounts'
import { useCreateNews, useDeleteNews, useNewsList, useUpdateNews } from '@/api/queries/news'
import { useForm } from '@/composables/useForm'
import { CreateNewsSchema } from '@/schemas/news.schema'
import { parseApiError } from '@/api/errors'
import { useNotification } from '@/composables/useNotification'
import type { NewsArticle } from '@/api/dbTypes'

interface CreateNewsForm {
  title: string
  content: JSONContent | null
  send_notification: boolean
}

const form = useForm<CreateNewsForm>(CreateNewsSchema, {
  title: '',
  content: null,
  send_notification: false,
})
const editForm = useForm<CreateNewsForm>(CreateNewsSchema, {
  title: '',
  content: null,
  send_notification: false,
})

const { showNotification } = useNotification()
const { data: user } = useProfile()
const canManageNews = computed(() => ['admin', 'organizer'].includes(user.value?.role ?? ''))
const isCreateOpen = ref(false)
const isEditOpen = ref(false)
const isDeleteConfirmOpen = ref(false)
const editingNewsId = ref<number | null>(null)
const deletingNewsId = ref<number | null>(null)
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
const expandedNewsIds = ref<number[]>([])
const COLLAPSE_TEXT_LIMIT = 280

const { mutate: createNews, isPending: isCreating } = useCreateNews()
const { mutate: updateNews, isPending: isUpdating } = useUpdateNews()
const { mutate: deleteNews, isPending: isDeleting } = useDeleteNews()

function handleCreate() {
  if (!form.validate()) return

  createNews(
    {
      body: {
        title: form.fields.value.title,
        content: form.fields.value.content as JSONContent,
        send_notification: form.fields.value.send_notification,
      },
    },
    {
      onSuccess() {
        form.hydrate({ title: '', content: null, send_notification: false })
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

function canModifyNews(item: NewsArticle) {
  if (user.value?.role === 'admin') return true
  if (user.value?.role === 'organizer') return item.created_by === user.value.id
  return false
}

function openEditModal(item: NewsArticle) {
  if (!canModifyNews(item)) return
  editingNewsId.value = item.id
  editForm.hydrate({
    title: item.title,
    content: item.content as JSONContent,
    send_notification: false,
  })
  isEditOpen.value = true
}

function handleEdit() {
  if (!editingNewsId.value) return
  if (!editForm.validate()) return

  updateNews(
    {
      id: editingNewsId.value,
      body: {
        title: editForm.fields.value.title,
        content: editForm.fields.value.content as JSONContent,
        send_notification: editForm.fields.value.send_notification,
      },
    },
    {
      onSuccess() {
        isEditOpen.value = false
        editingNewsId.value = null
        showNotification('News updated successfully.', 'success')
      },
      onError(error) {
        const parsed = parseApiError(error)
        for (const [field, errors] of Object.entries(parsed?.details || {})) {
          editForm.setError(field as keyof CreateNewsForm, errors?.[0] ?? 'Invalid value')
        }
        showNotification(parsed?.message, 'error')
      },
    },
  )
}

function openDeleteConfirm(item: NewsArticle) {
  if (!canModifyNews(item)) return
  deletingNewsId.value = item.id
  isDeleteConfirmOpen.value = true
}

function handleDelete() {
  if (!deletingNewsId.value) return
  deleteNews(
    { id: deletingNewsId.value },
    {
      onSuccess() {
        isDeleteConfirmOpen.value = false
        deletingNewsId.value = null
        showNotification('News deleted successfully.', 'success')
      },
      onError(error) {
        const parsed = parseApiError(error)
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

function isExpanded(newsId: number) {
  return expandedNewsIds.value.includes(newsId)
}

function toggleExpanded(newsId: number) {
  if (isExpanded(newsId)) {
    expandedNewsIds.value = expandedNewsIds.value.filter((id) => id !== newsId)
    return
  }
  expandedNewsIds.value = [...expandedNewsIds.value, newsId]
}

function extractPlainText(value: unknown): string {
  if (!value || typeof value !== 'object') return ''
  const node = value as { text?: string; content?: unknown[] }
  const ownText = typeof node.text === 'string' ? node.text : ''
  const childText = Array.isArray(node.content)
    ? node.content.map((child) => extractPlainText(child)).join(' ')
    : ''
  return `${ownText} ${childText}`.trim()
}

function isExpandable(item: NewsArticle) {
  return extractPlainText(item.content).length > COLLAPSE_TEXT_LIMIT
}

watch(
  [newsItems],
  () => {
    const currentIds = new Set(newsItems.value.map((item) => item.id))
    expandedNewsIds.value = expandedNewsIds.value.filter((id) => currentIds.has(id))
  },
  { immediate: true },
)
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

.notify-row {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  color: var(--muted-foreground);
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

.news-item-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.8rem;
}

.news-item-head h3 {
  margin: 0;
  font-family: var(--font-display);
}

.news-actions {
  display: flex;
  gap: 0.45rem;
}

.news-content-wrap {
  position: relative;
  max-height: 180px;
  overflow: hidden;
  opacity: 0.96;
  transition: max-height 0.32s ease, opacity 0.24s ease;
  will-change: max-height, opacity;
}

.news-content-wrap:not(.expanded)::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 48px;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0), var(--muted));
}

.news-content-wrap.expanded {
  max-height: 2200px;
  opacity: 1;
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
