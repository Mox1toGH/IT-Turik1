<template>
  <ui-modal v-model="open" maxWidth="520px">
    <template #title>
      <div class="modal-head">
        <h3 class="panel-title">Edit Template</h3>
        <p class="panel-note">Update the name, image, or default status.</p>
      </div>
    </template>

    <form id="editTemplateForm" class="template-form" @submit.prevent="submit">
      <div class="form-row">
        <div class="form-item">
          <label class="form-label">Template name</label>
          <ui-input v-model="form.name" required placeholder="Summer Cup 2026" />
        </div>

        <label class="check">
          <ui-switch v-model="form.is_default" />
          Make default template
        </label>
      </div>

      <div class="form-item">
        <label class="form-label">Image (optional)</label>
        <ui-file-drop
          v-model="form.files"
          accept="image/*"
          :multiple="false"
          hint="Leave empty to keep current image"
        />
      </div>
    </form>

    <template #footer>
      <ui-button variant="secondary" @click="open = false">Cancel</ui-button>
      <ui-button type="submit" form="editTemplateForm" :disabled="isUpdating">
        {{ isUpdating ? 'Saving...' : 'Save Changes' }}
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiFileDrop from '@/components/ui/UiFileDrop.vue'
import UiSwitch from '@/components/ui/UiSwitch.vue'
import { useNotification } from '@/composables/useNotification'
import { useUpdateCertificateTemplate } from '@/api/certificates/certificates'
import type { CertificateTemplate } from '@/api/.ts.schemas'

const props = defineProps<{
  template?: CertificateTemplate
}>()

const { showNotification } = useNotification()
const { mutateAsync: updateTemplate, isPending: isUpdating } = useUpdateCertificateTemplate()

const open = defineModel({ default: false })

const form = reactive({
  name: '',
  files: [] as File[],
  is_default: false,
})

watch(
  () => props.template,
  (tpl) => {
    if (!tpl) return
    form.name = tpl.name
    form.files = []
    form.is_default = tpl.is_default ?? false
  },
  { immediate: true },
)

async function submit() {
  if (!props.template) return

  try {
    await updateTemplate({
      id: props.template.id,
      data: {
        name: form.name,
        image: form.files[0] || undefined,
        is_default: form.is_default,
      },
    })

    showNotification('Template updated successfully.', 'success')
    open.value = false
  } catch {
    showNotification('Failed to update template.', 'error')
  }
}
</script>

<style scoped>
.modal-head {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.panel-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 800;
  color: var(--foreground);
}

.panel-note {
  margin: 0;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

.template-form {
  display: grid;
  gap: 0.85rem;
  padding: 10px 0;
}

.form-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.form-item {
  display: grid;
  gap: 0.4rem;
  flex: 1 1 220px;
}

.form-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--foreground);
}

.check {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 0.9rem;
  white-space: nowrap;
}

@media (max-width: 480px) {
  .form-row {
    flex-direction: column;
    align-items: stretch;
  }

  .check {
    white-space: normal;
  }
}
</style>
