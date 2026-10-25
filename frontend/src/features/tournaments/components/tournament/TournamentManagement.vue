<template>
  <section class="management-page" aria-label="Tournament management">
    <ManagementActionCard
      title="Tournament banner"
      description="Upload or remove the image displayed at the top of this tournament."
    >
      <template #action>
        <ui-button variant="secondary" size="sm" @click="isBannerModalOpen = true">
          Edit banner
        </ui-button>
      </template>
    </ManagementActionCard>
    <ManagementActionCard
      title="Edit tournament"
      description="Update the tournament name, schedule, and participation settings."
    >
      <template #action>
        <ui-button as-link variant="secondary" size="sm" :to="`/tournaments/${tournamentId}/edit`">
          Edit tournament
        </ui-button>
      </template>
    </ManagementActionCard>
    <ManageZoneCard :tournament-id="tournamentId" />
    <UpdateBannerModal v-model="isBannerModalOpen" :tournament-id="tournamentId" />
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UiButton from '@/components/ui/UiButton'
import ManagementActionCard from '@/components/shared/ManagementActionCard.vue'
import ManageZoneCard from './ManageZoneCard.vue'
import UpdateBannerModal from './modals/UpdateBannerModal.vue'

defineProps<{ tournamentId: number }>()
const isBannerModalOpen = ref(false)
</script>

<style scoped>
.management-page {
  display: grid;
  gap: 1rem;
}

</style>
