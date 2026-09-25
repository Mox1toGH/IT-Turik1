<template>
  <ui-modal v-model="isOpen" maxWidth="760px" :close-on-backdrop="!isUpdating">
    <template #title>Edit news</template>

    <form class="create-form" @submit.prevent="handleSubmit">
      <label class="form-item">
        <span class="form-label">Title</span>
        <ui-input
          v-model="editForm.fields.value.title"
          placeholder="Enter news title"
          :isInvalid="!!editForm.errors.value.title"
          @blur="editForm.validateField('title')"
        />
        <small v-if="editForm.errors.value.title" class="text-error">{{
          editForm.errors.value.title
        }}</small>
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

      <ui-button type="submit" :disabled="isUpdating">
        <loading-icon v-if="isUpdating" />
        <span>Save</span>
      </ui-button>
    </form>
  </ui-modal>
</template>

<script setup lang="ts">
import { watch } from 'vue'
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
import { useUpdateNews } from '@/api/news/news'
import type { NewsArticleResponse } from '@/api/backendAPINinja.schemas'

interface EditNewsFields {
  title: string
  content: JSONContent | null
  send_notification: boolean
}

const isOpen = defineModel<boolean>({ required: true })

const props = defineProps<{
  item: NewsArticleResponse | null
}>()

const emit = defineEmits<{
  success: []
}>()

const { showNotification } = useNotification()
const { mutate: updateNews, isPending: isUpdating } = useUpdateNews()

const editForm = useForm<EditNewsFields>(CreateNewsSchema, {
  title: '',
  content: null,
  send_notification: false,
})

watch(
  () => props.item,
  (item) => {
    if (!item) return
    editForm.hydrate({
      title: item.title,
      content: item.content as JSONContent,
      send_notification: false,
    })
  },
  { immediate: true },
)

function handleSubmit() {
  if (!props.item) return
  if (!editForm.validate()) return

  updateNews(
    {
      articleId: props.item.id,
      data: {
        title: editForm.fields.value.title,
        content: editForm.fields.value.content as JSONContent,
        send_notification: editForm.fields.value.send_notification,
      },
    },
    {
      onSuccess() {
        isOpen.value = false
        showNotification('News updated successfully.', 'success')
        emit('success')
      },
      onError(error) {
        for (const [field, errors] of Object.entries(error?.details || {})) {
          const message = Array.isArray(errors) ? errors[0] : errors
          editForm.setError(
            field as keyof EditNewsFields,
            typeof message === 'string' ? message : 'Invalid value',
          )
        }
        showNotification(error?.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
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
