<template>
  <button
    v-if="showTrigger"
    class="avatar-edit-btn"
    type="button"
    @click="avatar.isOpen.value = true"
    :disabled="disabled"
  >
    <SquarePen :size="18" />
  </button>

  <ui-modal v-model="avatar.isOpen.value" @close="avatar.resetState">
    <template #title>
      <h3>Avatar</h3>
    </template>

    <div class="modal-body">
      <div
        v-if="avatar.previewUrl.value"
        class="avatar-preview-frame"
        @pointerdown="avatar.onPreviewPointerDown"
      >
        <img
          :src="avatar.previewUrl.value"
          alt="Avatar preview"
          class="avatar-preview"
          :style="{ objectPosition: avatar.previewObjectPosition.value }"
        />
      </div>
      <div v-else class="avatar-empty">No avatar</div>

      <p v-if="avatar.previewUrl.value" class="position-hint">
        Drag image to choose avatar position
      </p>
      <ui-file-drop
        v-model="avatar.selectedAvatar.value"
        accept=".jpg,.jpeg,.png,.webp"
        :multiple="false"
        :max-files="1"
        :max-size-mb="5"
      />
    </div>

    <template #footer>
      <ui-button size="sm" variant="secondary" @click="avatar.resetState">Cancel</ui-button>
      <ui-button
        size="sm"
        variant="secondary"
        :disabled="avatar.isUpdating.value || !avatar.previewUrl.value"
        @click="isRemoveConfirmOpen = true"
      >
        Remove
      </ui-button>
      <ui-button size="sm" :disabled="avatar.isUpdating.value" @click="avatar.saveAvatar">
        <LoaderCircle
          v-if="avatar.isUpdating.value"
          class="animate-spin"
          :size="16"
        />
        Save
      </ui-button>
    </template>
  </ui-modal>
  <ui-confirm-modal
    v-model="isRemoveConfirmOpen"
    title="Remove profile photo?"
    confirm-text="Remove photo"
    confirm-variant="danger"
    :loading="avatar.isUpdating.value"
    @confirm="confirmRemoveAvatar"
  >
    <template #message>
      <p>Your current <ui-badge variant="red">profile photo</ui-badge> will be removed.</p>
    </template>
  </ui-confirm-modal>
</template>

<script setup lang="ts">
import { ref, toRef } from 'vue'
import UiModal from '@/components/ui/UiModal'
import UiConfirmModal from '@/components/ui/UiConfirmModal'
import UiBadge from '@/components/ui/UiBadge'
import UiButton from '@/components/ui/UiButton'
import { LoaderCircle, SquarePen } from 'lucide-vue-next'
import UiFileDrop from '@/components/ui/UiFileDrop'
import { useAvatarUpload } from '../../../composables/useAvatarUpload'
import type { UserSummary } from '@/shared/types/user'

const props = withDefaults(
  defineProps<{
    user?: Pick<UserSummary, 'id' | 'avatar'>
    disabled?: boolean
    showTrigger?: boolean
  }>(),
  { showTrigger: true },
)

const avatar = useAvatarUpload(
  toRef(props, 'user'),
  toRef(props, 'disabled', false),
)
const isRemoveConfirmOpen = ref(false)

function confirmRemoveAvatar() {
  isRemoveConfirmOpen.value = false
  avatar.removeAvatar()
}

defineExpose({ open: avatar.open })
</script>

<style scoped>
.avatar-edit-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--subtle);
  color: var(--muted-foreground);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.avatar-edit-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.modal-body {
  display: grid;
  gap: 0.75rem;
}

.avatar-preview-frame,
.avatar-empty {
  width: 120px;
  height: 120px;
  border-radius: 999px;
  border: 1px solid var(--border);
}

.avatar-preview-frame {
  overflow: hidden;
  cursor: move;
}

.position-hint {
  margin: 0;
  color: var(--muted-foreground);
  font-size: 0.8rem;
}

.avatar-preview,
.avatar-empty {
  width: 100%;
  height: 100%;
}

.avatar-preview {
  object-fit: cover;
  user-select: none;
  pointer-events: none;
}

.avatar-empty {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--muted-foreground);
  font-size: 0.85rem;
}
</style>
