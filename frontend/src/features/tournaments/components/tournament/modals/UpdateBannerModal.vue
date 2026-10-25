<template>
  <ui-modal v-model="isOpen" @close="resetBannerState" scrollable>
    <template #title>
      <h3>Tournament banner</h3>
    </template>

    <div class="banner-modal-body">
      <banner-preview v-model:draft="draft" :preview-url="bannerPreviewUrl" />
      <ui-file-drop v-model="selectedBanner" accept="image/*" />
    </div>

    <template #footer>
      <ui-button size="sm" variant="secondary" :disabled="isBannerUpdating" @click="cancel">
        Cancel
      </ui-button>
      <ui-button
        size="sm"
        variant="secondary"
        :disabled="isBannerUpdating || !tournament?.banner"
        @click="isRemoveConfirmOpen = true"
      >
        Remove
      </ui-button>
      <ui-button size="sm" :disabled="isBannerUpdating || !canSave" @click="saveBanner">
        <LoaderCircle class="animate-spin" v-if="isBannerUpdating" />
        Save
      </ui-button>
    </template>
  </ui-modal>
  <ui-confirm-modal
    v-model="isRemoveConfirmOpen"
    title="Remove tournament banner?"
    message="The current tournament banner will be removed."
    confirm-text="Remove banner"
    confirm-variant="danger"
    :loading="isBannerUpdating"
    @confirm="confirmRemoveBanner"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { LoaderCircle } from 'lucide-vue-next'
import UiModal from '@/components/ui/UiModal'
import UiConfirmModal from '@/components/ui/UiConfirmModal'
import UiButton from '@/components/ui/UiButton'
import UiFileDrop from '@/components/ui/UiFileDrop'
import BannerPreview from './BannerPreview.vue'
import { useBannerUpload } from '../../../composables/useBannerUpload'

const props = defineProps<{ tournamentId: number }>()

const isOpen = defineModel({ default: false })
const isRemoveConfirmOpen = ref(false)

const {
  tournament,
  selectedBanner,
  draft,
  canSave,
  isBannerUpdating,
  bannerPreviewUrl,
  resetBannerState,
  cancel,
  saveBanner,
  removeBanner,
} = useBannerUpload(
  () => props.tournamentId,
  isOpen,
)

function confirmRemoveBanner() {
  isRemoveConfirmOpen.value = false
  removeBanner()
}
</script>

<style scoped>
.banner-modal-body {
  display: grid;
  gap: 0.75rem;
}
</style>
