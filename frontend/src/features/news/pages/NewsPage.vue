<template>
  <section class="page-shell news-page">
    <news-hero
      :total-news="totalNews"
      :can-manage-news="canManageNews"
      @create="isCreateOpen = true"
    />

    <div class="news-rule" aria-hidden="true"></div>

    <news-list
      :query="newsQuery"
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
import UiConfirmModal from '@/components/ui/UiConfirmModal'
import { useNotification } from '@/composables/useNotification'
import { useDeleteNews, useListNews } from '@/api/news/news'
import { useGetUserProfile } from '@/api/accounts/accounts'
import NewsHero from '../components/NewsHero.vue'
import NewsList from '../components/NewsList.vue'
import EditNewsModal from '../components/EditNewsModal.vue'
import CreateNewsModal from '../components/CreateNewsModal.vue'
import type { NewsArticle } from '../types'
import { hasRole, hasAnyRole } from '@/shared/lib/permissions'

const { showNotification } = useNotification()
const route = useRoute()
const { data: user } = useGetUserProfile()

const canManageNews = computed(() => hasAnyRole(user.value, ['admin', 'organizer']))

const isCreateOpen = ref(false)
const isEditOpen = ref(false)
const isDeleteConfirmOpen = ref(false)
const editingNews = ref<NewsArticle | null>(null)
const deletingNewsId = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = 10

const newsQuery = useListNews(computed(() => ({ page: currentPage.value, pageSize })))
const { data: news } = newsQuery

const newsItems = computed<NewsArticle[]>(() => news.value?.items ?? [])
const totalNews = computed(() => news.value?.count ?? 0)
const totalPages = computed(() => Math.max(1, Math.ceil(totalNews.value / pageSize)))

const { mutate: deleteNews, isPending: isDeleting } = useDeleteNews()

function canModifyNews(item: NewsArticle) {
  if (hasRole(user.value, 'admin')) return true
  if (hasRole(user.value, 'organizer')) return item.created_by === user.value?.id
  return false
}

function openEditModal(item: NewsArticle) {
  if (!canModifyNews(item)) return
  editingNews.value = item
  isEditOpen.value = true
}

function openDeleteConfirm(item: NewsArticle) {
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
}

.news-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--border);
}

@media (max-width: 760px) {
  .news-page {
    padding: 1rem 1rem 2rem;
  }
}
</style>
