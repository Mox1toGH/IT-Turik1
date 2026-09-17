<template>
  <ui-modal
    v-model="isOpen"
    maxWidth="760px"
    :close-on-backdrop="!isCreating"
    @close="form.reset()"
  >
    <template #title>Create news</template>

    <div class="section-head">
      <span class="text-muted">Admins and organizers only</span>
    </div>

    <form class="create-form" @submit.prevent="handleSubmit">
      <label class="form-item">
        <span class="form-label">Title</span>
        <ui-input
          v-model="form.fields.value.title"
          placeholder="Enter news title"
          :isInvalid="!!form.errors.value.title"
          @blur="form.validateField('title')"
        />
        <small v-if="form.errors.value.title" class="text-error">{{
          form.errors.value.title
        }}</small>
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
</template>

<script setup lang="ts">
import type { JSONContent } from '@tiptap/core'
import UiModal from '@/components/ui/UiModal.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSwitch from '@/components/ui/UiSwitch.vue'
import UiButton from '@/components/ui/UiButton.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import EditorModal from '@/features/tournaments/components/create-round/modals/EditorModal.vue'
import { useForm } from '@/composables/useForm'
import { CreateNewsSchema } from '@/schemas/news.schema'
import { useNotification } from '@/composables/useNotification'
import { useCreateNews } from '@/api/news/news'

interface CreateNewsFields {
  title: string
  content: JSONContent | null
  send_notification: boolean
}

const isOpen = defineModel<boolean>({ required: true })

const emit = defineEmits<{
  success: []
}>()

const { showNotification } = useNotification()
const { mutate: createNews, isPending: isCreating } = useCreateNews()

const form = useForm<CreateNewsFields>(CreateNewsSchema, {
  title: '',
  content: null,
  send_notification: false,
})

function handleSubmit() {
  if (!form.validate()) return

  createNews(
    {
      data: {
        title: form.fields.value.title,
        content: form.fields.value.content as JSONContent,
        send_notification: form.fields.value.send_notification,
      },
    },
    {
      onSuccess() {
        isOpen.value = false
        form.reset()
        showNotification('News created successfully.', 'success')
        emit('success')
      },
      onError(error) {
        for (const [field, errors] of Object.entries(error?.details || {})) {
          form.setError(field as keyof CreateNewsFields, errors?.[0] ?? 'Invalid value')
        }
        showNotification(error?.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
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
.text-error {
  color: var(--destructive);
}
</style>
