<template>
  <section class="page-shell news-page">
    <news-hero
      :total-news="totalNews"
      :can-manage-news="canManageNews"
      @create="isCreateOpen = true"
    />

    <div class="news-rule" aria-hidden="true"></div>

    <news-list
      :is-loading="isLoadingNews"
      :is-error="isLoadingError"
      :error-code="newsError?.code"
      :items="newsItems"
      :total-news="totalNews"
      :total-pages="totalPages"
      :page-size="pageSize"
      v-model:current-page="currentPage"
      :can-modify="canModifyNews"
      @edit="openEditModal"
      @delete="openDeleteConfirm"
    />

    <create-news-modal v-if="canManageNews" v-model="isCreateOpen" />
    <edit-news-modal v-if="canManageNews" v-model="isEditOpen" :item="editingNews" />

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
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import UiConfirmModal from '@/components/ui/UiConfirmModal.vue'
import { useNotification } from '@/composables/useNotification'
import { useDeleteNews, useListNews } from '@/api/news/news'
import { useGetUserProfile } from '@/api/accounts/accounts'
import NewsHero from '../components/NewsHero.vue'
import NewsList from '../components/NewsList.vue'
import EditNewsModal from '../components/EditNewsModal.vue'
import CreateNewsModal from '../components/CreateNewsModal.vue'
import type { NewsArticleResponse } from '@/api/backendAPINinja.schemas.ts'

const { showNotification } = useNotification()
const route = useRoute()
const { data: user } = useGetUserProfile()

const canManageNews = computed(() => ['admin', 'organizer'].includes(user.value?.role ?? ''))

const isCreateOpen = ref(false)
const isEditOpen = ref(false)
const isDeleteConfirmOpen = ref(false)
const editingNews = ref<NewsArticleResponse | null>(null)
const deletingNewsId = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = 10

const {
  data: news,
  isLoading: isLoadingNews,
  isLoadingError,
  error: newsError,
} = useListNews(computed(() => ({ page: currentPage.value, pageSize })))

const newsItems = computed<NewsArticleResponse[]>(() =>
  (news.value?.items ?? []).map((item) => ({
    ...item,
    created_by: item.created_by ?? null,
  })),
)
const totalNews = computed(() => news.value?.count ?? 0)
const totalPages = computed(() => Math.max(1, Math.ceil(totalNews.value / pageSize)))

const { mutate: deleteNews, isPending: isDeleting } = useDeleteNews()

function canModifyNews(item: NewsArticleResponse) {
  if (user.value?.role === 'admin') return true
  if (user.value?.role === 'organizer') return item.created_by === user.value.id
  return false
}

function openEditModal(item: NewsArticleResponse) {
  if (!canModifyNews(item)) return
  editingNews.value = item
  isEditOpen.value = true
}

function openDeleteConfirm(item: NewsArticleResponse) {
  if (!canModifyNews(item)) return
  deletingNewsId.value = item.id
  isDeleteConfirmOpen.value = true
}

function handleDelete() {
  if (!deletingNewsId.value) return
  deleteNews(
    { articleId: deletingNewsId.value },
    {
      onSuccess() {
        isDeleteConfirmOpen.value = false
        deletingNewsId.value = null
        showNotification('News deleted successfully.', 'success')
      },
      onError(error) {
        showNotification(error?.message, 'error')
      },
    },
  )
}

function scrollToNewsFromHash() {
  const hash = route.hash || ''
  if (!hash.startsWith('#news-')) return
  const el = document.getElementById(hash.slice(1))
  el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

watch(
  [newsItems, () => route.hash],
  async () => {
    await nextTick()
    scrollToNewsFromHash()
  },
  { immediate: true },
)
</script>

<style scoped>
.news-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
}

.news-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

@media (max-width: 760px) {
  .news-page {
    padding: 1rem 1rem 2rem;
  }
}
</style>
