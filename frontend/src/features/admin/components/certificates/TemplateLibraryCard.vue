<template>
  <ui-card class="panel">
    <template #header>
      <div class="panel-head">
        <h2 class="panel-title">Template Library</h2>
        <span class="panel-note">Upload and preview</span>
      </div>
    </template>

    <form class="template-form" @submit.prevent="$emit('upload')">
      <div class="form-item">
        <label class="form-label">Template name</label
        ><ui-input v-model="localTemplateForm.name" required placeholder="Summer Cup 2026" />
      </div>
      <div class="form-item">
        <label class="form-label">Image</label
        ><input
          class="file-input"
          type="file"
          accept="image/*"
          @change="$emit('file-change', $event)"
          required
        />
      </div>
      <label class="check"
        ><input v-model="localTemplateForm.is_default" type="checkbox" />Make default
        template</label
      >
      <ui-button type="submit" :disabled="isUploading" class="submit">{{
        isUploading ? 'Uploading...' : 'Upload Template'
      }}</ui-button>
    </form>

    <ui-skeleton-loader :loading="isTemplatesLoading">
      <template #skeleton
        ><div class="templates-grid">
          <ui-skeleton v-for="i in 3" :key="i" variant="rect" width="100%" /></div
      ></template>
      <p v-if="isTemplatesError" class="text-muted">Failed to load templates.</p>
      <p v-else-if="!paginatedTemplates.length" class="text-muted">No templates uploaded yet.</p>
      <div v-else>
        <div class="templates-grid">
          <ui-card v-for="tpl in paginatedTemplates" :key="tpl.id" class="template-card">
            <template #header>
              <div class="template-head">
                <div class="template-info">
                  <strong>{{ tpl.name }}</strong>
                  <ui-badge
                    :variant="tpl.is_default ? 'green' : 'gray'"
                    class="status-badge-mini"
                    >{{ tpl.is_default ? 'Default' : 'Template' }}</ui-badge
                  >
                </div>
                <div class="mini-actions">
                  <button
                    class="action-btn-mini"
                    title="Edit template"
                    @click.stop="$emit('edit', tpl)"
                  >
                    <EditIcon class="icon-mini" />
                  </button>
                  <button
                    class="action-btn-mini delete"
                    title="Delete template"
                    @click.stop="$emit('delete', tpl.id)"
                  >
                    <TrashIcon class="icon-mini" />
                  </button>
                </div>
              </div>
            </template>
            <img v-if="tpl.image_url" :src="tpl.image_url" :alt="tpl.name" class="preview" />
          </ui-card>
        </div>

        <div v-if="totalTemplatePages > 1" class="pagination">
          <ui-button
            size="sm"
            variant="secondary"
            :disabled="templatesPage === 1"
            @click="$emit('prev-page')"
            >Prev</ui-button
          >
          <span class="page-info">Page {{ templatesPage }} / {{ totalTemplatePages }}</span>
          <ui-button
            size="sm"
            variant="secondary"
            :disabled="templatesPage === totalTemplatePages"
            @click="$emit('next-page')"
            >Next</ui-button
          >
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
import type { CertificateTemplate } from '@/api/.ts.schemas'

const props = defineProps<{
  templateForm: { name: string; file: File | null; is_default: boolean }
  isUploading: boolean
  isTemplatesLoading: boolean
  isTemplatesError: boolean
  paginatedTemplates: CertificateTemplate[]
  templatesPage: number
  totalTemplatePages: number
}>()

const emit = defineEmits<{
  (e: 'update:templateForm', value: typeof props.templateForm): void
  (e: 'file-change', event: Event): void
  (e: 'upload'): void
  (e: 'edit', tpl: CertificateTemplate): void
  (e: 'delete', id: number): void
  (e: 'prev-page'): void
  (e: 'next-page'): void
}>()

const localTemplateForm = computed({
  get: () => props.templateForm,
  set: (v) => emit('update:templateForm', v),
})
</script>

<style scoped>
.panel {
  background: var(--muted);
  color: var(--muted-foreground);
}
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}
.panel-title {
  margin: 0;
  font-size: 1rem;
}
.panel-note {
  font-size: 0.8rem;
  color: var(--color-gray-500);
}
.template-form {
  display: grid;
  gap: 0.65rem;
}
.form-item {
  display: grid;
  gap: 0.4rem;
}
.form-label {
  font-size: 0.85rem;
  font-weight: 600;
}
.submit {
  width: fit-content;
}
.file-input {
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  padding: 0.6rem 0.8rem;
  background: var(--background);
  color: var(--foreground);
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s ease;
}
.file-input:hover {
  border-color: var(--primary);
}
.file-input::file-selector-button {
  background: var(--primary);
  color: var(--primary-foreground);
  border: none;
  border-radius: 8px;
  padding: 0.4rem 0.8rem;
  margin-right: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}
.file-input::file-selector-button:hover {
  opacity: 0.85;
}
.check {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 0.9rem;
}
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.65rem;
  margin-top: 0.65rem;
}
.template-card {
  background: color-mix(in srgb, var(--background) 92%, var(--muted));
}
.template-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}
.template-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
}
.template-info strong {
  word-break: break-word;
  font-size: 0.95rem;
  line-height: 1.2;
}
.status-badge-mini {
  width: fit-content;
  font-size: 10px;
  padding: 2px 8px;
}
.mini-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  min-width: 44px;
}
.action-btn-mini {
  background: none;
  border: none;
  color: var(--muted-foreground);
  padding: 4px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.action-btn-mini:hover {
  background: var(--secondary);
  color: var(--foreground);
}
.action-btn-mini.delete:hover {
  background: #fee2e2;
  color: #991b1b;
}
.icon-mini {
  width: 14px;
  height: 14px;
}
.preview {
  width: 100%;
  max-height: 220px;
  object-fit: contain;
  border-radius: 10px;
  border: 1px solid var(--line-soft);
  background: #fff;
}
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 16px;
}
.page-info {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--color-gray-600);
}
</style>
