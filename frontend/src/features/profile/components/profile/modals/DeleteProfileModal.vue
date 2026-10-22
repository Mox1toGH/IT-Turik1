<template>
  <ui-modal v-model="isOpen">
    <template #title>
      <h3>Delete account</h3>
    </template>

    <p class="modal-text">This action cannot be undone. Enter this username to confirm.</p>

    <ui-query-block :query="userQuery">
      <template #error><p class="text-error">Could not load account details.</p></template>
      <ui-query-field>
        <template #skeleton><ui-skeleton variant="rect" width="100%" height="40px" /></template>
        <div class="delete-confirmation">
          <ui-badge variant="red">{{ expectedDeleteText }}</ui-badge>
          <ui-input
            v-model="deleteConfirmInput"
            :placeholder="expectedDeleteText"
            :disabled="isDeleting"
            style="width: 100%"
          />
        </div>
      </ui-query-field>
    </ui-query-block>

    <p v-if="deleteError">{{ deleteError }}</p>

    <template #footer>
      <ui-button size="sm" variant="secondary" :disabled="isDeleting" @click="isOpen = false">
        Cancel
      </ui-button>
      <ui-button size="sm" variant="danger" :disabled="!canDelete" @click="handleDeleteAccount">
        <LoaderCircle class="animate-spin" v-if="isDeleting" />
        Delete permanently
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge'
import UiButton from '@/components/ui/UiButton'
import UiInput from '@/components/ui/UiInput'
import UiModal from '@/components/ui/UiModal'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { useNotification } from '@/composables/useNotification'
import { LoaderCircle } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { useDeleteUserProfile, useGetUserProfile } from '@/api/accounts/accounts'

/** Open state is owned by the parent, which renders the trigger button. */
const isOpen = defineModel<boolean>({ default: false })

const store = useUserStore()
const userQuery = useGetUserProfile()
const { data: user } = userQuery
const { mutate: deleteAccount, isPending: isDeleting } = useDeleteUserProfile()

const router = useRouter()
const { showNotification, hideNotification } = useNotification()

const deleteError = ref<string | null>(null)
const deleteConfirmInput = ref('')
const expectedDeleteText = computed(() => user.value?.username || '')

const canDelete = computed(
  () =>
    Boolean(expectedDeleteText.value) &&
    deleteConfirmInput.value === expectedDeleteText.value &&
    !isDeleting.value,
)

watch(isOpen, (open) => {
  if (!open) {
    deleteConfirmInput.value = ''
    deleteError.value = null
  }
})

const handleDeleteAccount = async () => {
  if (deleteConfirmInput.value !== expectedDeleteText.value) {
    deleteError.value = `Please enter "${expectedDeleteText.value}" exactly.`
    return
  }

  deleteError.value = ''
  hideNotification()

  deleteAccount(void 0, {
    onSuccess: () => {
      store.logout()
      router.push('/login')
    },
    onError: (error) => {
      showNotification(error.message, 'error')
    },
  })
}
</script>

<style>
.modal-text {
  margin-bottom: 0.4rem;
}
</style>
