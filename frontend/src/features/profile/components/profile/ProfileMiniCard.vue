<template>
  <ui-card variant="panel">
    <div class="profile-mini-content">
      <div class="profile-mini-identity">
        <div class="avatar-box">
          <user-avatar
            :avatar="user?.avatar"
            :avatar-frame-url="user?.avatar_frame_url"
            :username="user?.username || 'user'"
            :full-name="user?.full_name || ''"
            :size="100"
            :position-key="user?.id ? `image-position:avatar:user:${user.id}` : ''"
            :class="{ 'avatar-is-disabled': props.isLoading }"
            @click="openAvatarModal"
          />
          <span class="avatar-edit-indicator" aria-hidden="true">
            <AvatarEditIcon />
          </span>
          <avatar-modal
            ref="avatarModal"
            :user="user"
            :disabled="props.isLoading"
            :show-trigger="false"
          />
        </div>

        <div class="profile-mini-copy">
          <strong class="profile-mini-name">{{
            user?.full_name || user?.username || 'User'
          }}</strong>
          <p class="profile-mini-meta">
            {{ user?.username || 'user' }}<span aria-hidden="true"> · </span
            >{{ user?.role || 'Member' }}
          </p>
        </div>
      </div>

      <ui-button size="lg" :disabled="isLoading" @click="emit('edit-profile')">
        <!-- TODO: split to individual component or even better import from lib-->
        <svg aria-hidden="true" viewBox="0 0 24 24" class="edit-icon">
          <path d="m4 20 4.4-1 10.2-10.2a2.1 2.1 0 0 0-3-3L5.4 16 4 20Z" />
          <path d="m14.5 7.5 2 2" />
        </svg>
        Edit profile
      </ui-button>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import AvatarEditIcon from '@/icons/AvatarEditIcon.vue'
import AvatarModal from './modals/AvatarModal.vue'
import type { UserResponse } from '@/api/backendAPINinja.schemas.ts'

const props = defineProps<{
  user?: UserResponse
  isLoading?: boolean
}>()

const emit = defineEmits<{
  'edit-profile': []
}>()

const avatarModal = ref<InstanceType<typeof AvatarModal> | null>(null)

const openAvatarModal = () => {
  avatarModal.value?.open()
}
</script>

<style scoped>
.profile-mini-content,
.profile-mini-identity {
  display: flex;
  align-items: center;
}

.profile-mini-content {
  justify-content: space-between;
  gap: 1.5rem;
}

.profile-mini-identity {
  min-width: 0;
  gap: 1.25rem;
}

.avatar-box {
  position: relative;
  flex: 0 0 auto;
}

.avatar-box :deep(.user-avatar-wrap) {
  cursor: pointer;
}

.avatar-box :deep(.avatar-is-disabled) {
  cursor: not-allowed;
  opacity: 0.6;
}

.avatar-edit-indicator {
  position: absolute;
  top: -0.2rem;
  right: -0.2rem;
  z-index: 3;
  display: grid;
  width: 2rem;
  height: 2rem;
  place-items: center;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--primary);
  color: var(--primary-foreground);
  pointer-events: none;
}

.avatar-edit-indicator :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.profile-mini-copy {
  min-width: 0;
}

.profile-mini-name,
.profile-mini-meta {
  display: block;
  overflow-wrap: anywhere;
}

.profile-mini-name {
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  line-height: var(--text-2xl--line-height);
  font-weight: 800;
}

.profile-mini-meta {
  margin: 0.35rem 0 0;
  color: var(--muted-foreground);
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.edit-profile-button:hover {
  background: color-mix(in srgb, var(--primary) 84%, black 16%);
  opacity: 1;
}

.edit-icon {
  width: 1.35rem;
  height: 1.35rem;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

@media (max-width: 560px) {
  .profile-mini-content {
    align-items: flex-start;
    flex-direction: column;
  }

  .profile-mini-identity {
    flex-direction: column;
    align-items: start;
  }

  .profile-mini-content :deep(.btn) {
    align-self: stretch;
  }
}
</style>
