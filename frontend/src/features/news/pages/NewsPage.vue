<template>
  <section class="page-shell news-page">
    <ui-card>
      <template #header>
        <div>
          <div class="top-header">
            <p class="section-eyebrow">News</p>
            <ui-badge>Total posts: {{ news?.length ?? 0 }}</ui-badge>
          </div>
          <h1>News board</h1>
          <p class="section-subtitle">Important updates, announcements, and platform changes.</p>
        </div>
      </template>

      <template #footer>
        <div class="hero-actions" v-if="canManageNews">
          <ui-button @click="isCreateOpen = !isCreateOpen" variant="secondary">
            {{ isCreateOpen ? 'Hide editor' : 'Create news' }}
          </ui-button>
        </div>
      </template>
    </ui-card>

    <ui-card v-if="canManageNews && isCreateOpen" class="create-card">
      <template #header>
        <div class="section-head">
          <h2>Create news</h2>
          <span class="text-muted">Admins and organizers only</span>
        </div>
      </template>
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
    </ui-card>

    <ui-card v-if="isLoadingNews">
      <template #header>
        <div class="section-head">
          <h2>Latest posts</h2>
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

    <ui-card v-else-if="!news?.length">
      <template #header>
        <div class="section-head">
          <h2>Latest posts</h2>
        </div>
      </template>
      <p class="text-muted">No news yet.</p>
    </ui-card>

    <ui-card v-else>
      <template #header>
        <div class="section-head">
          <h2>Latest posts</h2>
          <span class="text-muted">{{ news?.length ?? 0 }} published</span>
        </div>
      </template>
      <div class="news-grid">
        <ui-card v-for="item in news" :key="item.id" class="news-item">
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
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { JSONContent } from '@tiptap/core'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
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
const isCreateOpen = ref(true)

const {
  data: news,
  isLoading: isLoadingNews,
  isLoadingError,
  error: newsError,
} = useNewsList()
const parsedError = computed(() => parseApiError(newsError.value))

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

.hero-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  align-items: center;
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
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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
</style>
