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
        @click="removeBanner"
      >
        Remove
      </ui-button>
      <ui-button size="sm" :disabled="isBannerUpdating || !canSave" @click="saveBanner">
        <loading-icon v-if="isBannerUpdating" />
        Save
      </ui-button>
    </template>
  </ui-modal>
</template>

<script setup lang="ts">
import LoadingIcon from '@/icons/LoadingIcon.vue'
import UiModal from '@/components/ui/UiModal'
import UiButton from '@/components/ui/UiButton'
import UiFileDrop from '@/components/ui/UiFileDrop'
import BannerPreview from './BannerPreview.vue'
import { useBannerUpload } from '../../../composables/useBannerUpload'

const props = defineProps<{ tournamentId: number }>()

const isOpen = defineModel({ default: false })

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
</script>

<style scoped>
.banner-modal-body {
  display: grid;
  gap: 0.75rem;
}
</style>
