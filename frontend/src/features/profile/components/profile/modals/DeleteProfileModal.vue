<template>
  <ui-button
    variant="danger"
    :disabled="isLoading || isDeleting"
    @click="isDeleteModalOpen = true"
    type="button"
  >
    Delete account
  </ui-button>

  <ui-modal v-model="isDeleteModalOpen">
    <template #title>
      <h3>Delete account</h3>
    </template>

    <p class="modal-text">
      This action cannot be undone. Enter
      <ui-badge variant="red">{{ expectedDeleteText }}</ui-badge>
      to confirm.
    </p>

    <ui-input
      v-model="deleteConfirmInput"
      :placeholder="expectedDeleteText"
      :disabled="isDeleting"
      style="width: 100%"
    />

    <p v-if="deleteError">{{ deleteError }}</p>

    <template #footer>
      <ui-button
        size="sm"
        variant="secondary"
        :disabled="isDeleting"
        @click="isDeleteModalOpen = false"
      >
        Cancel
      </ui-button>
      <ui-button size="sm" variant="danger" :disabled="!canDelete" @click="handleDeleteAccount">
        <loading-icon v-if="isDeleting" />
        Delete permanently
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiModal from '@/components/ui/UiModal.vue'
import { useNotification } from '@/composables/useNotification'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { computed, ref } from 'vue'
import { useDeleteAccount, useProfile } from '@/api/queries/accounts'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const store = useUserStore()
const { data: user, isLoading } = useProfile()
const { mutate: deleteAccount, isPending: isDeleting } = useDeleteAccount()

const router = useRouter()
const { showNotification, hideNotification } = useNotification()

const isDeleteModalOpen = ref(false)
const deleteError = ref<string | null>(null)
const deleteConfirmInput = ref('')
const expectedDeleteText = computed(() => user.value?.username || '')

const canDelete = computed(
  () =>
    Boolean(expectedDeleteText.value) &&
    deleteConfirmInput.value === expectedDeleteText.value &&
    !isDeleting.value,
)

const handleDeleteAccount = async () => {
  if (deleteConfirmInput.value !== expectedDeleteText.value) {
    deleteError.value = `Please enter "${expectedDeleteText.value}" exactly.`
    return
  }

  isDeleting.value = true
  deleteError.value = ''
  hideNotification()

  deleteAccount(void 0, {
    onSuccess: () => {
      store.logout()
      router.push('/login')
    },
    onError: (err) => {
      showNotification(
        err.response ? 'Unable to delete account.' : 'Server connection error.',
        'error',
      )
    },
  })
}
</script>

<style>
.modal-text {
  margin-bottom: 0.4rem;
}
</style>
