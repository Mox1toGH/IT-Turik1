<template>
  <ui-modal v-model="isOpen" :close-on-backdrop="canCloseOnBackdrop" max-width="620px" scrollable>
    <template #title>
      <div class="modal-title">
        <p class="section-eyebrow">Account</p>
        <h2>{{ modalMode === 'profile' ? 'Edit profile' : 'Change password' }}</h2>
      </div>
    </template>

    <profile-details-form
      v-if="modalMode === 'profile'"
      ref="profileFormRef"
      @saved="close"
      @cancel="close"
      @change-password="modalMode = 'password'"
    />

    <password-change-form
      v-else
      ref="passwordFormRef"
      :user-email="userEmail"
      @saved="modalMode = 'profile'"
      @back="modalMode = 'profile'"
    />
  </ui-modal>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import UiModal from '@/components/ui/UiModal.vue'
import ProfileDetailsForm from './ProfileDetailsForm.vue'
import PasswordChangeForm from './PasswordChangeForm.vue'
import { useGetUserProfile } from '@/api/accounts/accounts'

const props = withDefaults(
  defineProps<{
    defaultOpen?: boolean
  }>(),
  { defaultOpen: false },
)

const { data: user } = useGetUserProfile()
const userEmail = computed(() => user.value?.email)

const isOpen = ref(props.defaultOpen)
const modalMode = ref<'profile' | 'password'>('profile')
const profileFormRef = ref<InstanceType<typeof ProfileDetailsForm> | null>(null)
const passwordFormRef = ref<InstanceType<typeof PasswordChangeForm> | null>(null)

const canCloseOnBackdrop = computed(
  () => !profileFormRef.value?.isSubmitting && !passwordFormRef.value?.isSubmitting,
)

const open = () => {
  isOpen.value = true
}

const close = () => {
  if (!canCloseOnBackdrop.value) return
  isOpen.value = false
  modalMode.value = 'profile'
  passwordFormRef.value?.reset()
}

defineExpose({ open, close })
</script>

<style scoped>
.modal-title h2 {
  margin: 0.2rem 0 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
}
</style>
