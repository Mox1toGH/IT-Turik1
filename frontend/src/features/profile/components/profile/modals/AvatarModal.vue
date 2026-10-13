<template>
  <button
    v-if="showTrigger"
    class="avatar-edit-btn"
    type="button"
    @click="avatar.isOpen.value = true"
    :disabled="disabled"
  >
    <AvatarEditIcon />
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
      <ui-file-drop v-model="avatar.selectedAvatar.value" accept="image/*" />
    </div>

    <template #footer>
      <ui-button size="sm" variant="secondary" @click="avatar.resetState">Cancel</ui-button>
      <ui-button
        size="sm"
        variant="secondary"
        :disabled="avatar.isUpdating.value || !avatar.previewUrl.value"
        @click="avatar.removeAvatar"
      >
        Remove
      </ui-button>
      <ui-button size="sm" :disabled="avatar.isUpdating.value" @click="avatar.saveAvatar">
        <LoadingIcon v-if="avatar.isUpdating.value" />
        Save
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import { toRef } from 'vue'
import UiModal from '@/components/ui/UiModal'
import UiButton from '@/components/ui/UiButton'
import AvatarEditIcon from '@/icons/AvatarEditIcon.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import UiFileDrop from '@/components/ui/UiFileDrop'
import { useAvatarUpload } from '../../../composables/useAvatarUpload'
import type { UserResponse } from '@/api/backendAPINinja.schemas'

const props = withDefaults(
  defineProps<{
    user?: UserResponse
    disabled?: boolean
    showTrigger?: boolean
  }>(),
  { showTrigger: true },
)

const avatar = useAvatarUpload(
  toRef(props, 'user'),
  toRef(props, 'disabled', false),
)

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
