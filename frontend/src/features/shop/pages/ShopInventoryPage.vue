<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div class="head">
          <div>
            <p class="section-eyebrow">Profile</p>
            <h1 class="section-title">Digital Inventory</h1>
          </div>
          <ui-button as-link to="/profile" variant="secondary">Back to Profile</ui-button>
        </div>
      </template>

      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <ui-skeleton v-for="i in 4" :key="i" variant="rect" width="100%" />
        </template>

        <p v-if="isLoadingError" class="text-muted">Failed to load inventory.</p>
        <p v-else-if="!items.length" class="text-muted">You don't own digital items yet.</p>

        <div v-else class="grid">
          <ui-card v-for="item in items" :key="item.id" class="item-card">
            <template #header>
              <div class="item-head">
                <strong>{{ item.product.name }}</strong>
                <ui-badge :variant="item.is_equipped ? 'green' : 'gray'">
                  {{ item.is_equipped ? 'Equipped' : 'Owned' }}
                </ui-badge>
              </div>
            </template>

            <img
              v-if="item.product.avatar_frame?.svg_file || item.product.digital_asset_url"
              :src="item.product.avatar_frame?.svg_file || item.product.digital_asset_url"
              class="asset-preview"
              alt="Digital asset"
            />

            <p class="desc">{{ item.product.description || 'No description' }}</p>
            <p class="meta">Acquired: {{ formatDate(item.acquired_at) }}</p>

            <div class="button-group">
              <ui-button
                size="sm"
                :disabled="item.is_equipped || isEquipping || isUnequipping"
                @click="equip(item.id)"
              >
                Equip
              </ui-button>
              <ui-button
                size="sm"
                variant="secondary"
                :disabled="!item.is_equipped || isUnequipping || isEquipping"
                @click="unequip(item.id)"
              >
                Remove
              </ui-button>
            </div>
          </ui-card>
        </div>
      </ui-skeleton-loader>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { useEquipInventoryItem, useMyInventory, useUnequipInventoryItem } from '@/api/queries/inventory'
import { useNotification } from '@/composables/useNotification'
import { parseApiError } from '@/api/errors'

const { showNotification } = useNotification()
const { data, isLoading, isLoadingError } = useMyInventory()
const { mutate: equipItem, isPending: isEquipping } = useEquipInventoryItem()
const { mutate: unequipItem, isPending: isUnequipping } = useUnequipInventoryItem()

const items = computed(() => data.value?.results ?? [])

const equip = (inventoryId: number) => {
  equipItem(
    { data: { inventory_id: inventoryId } },
    {
      onSuccess: () => showNotification('Avatar frame equipped.', 'success'),
      onError: (e) => showNotification(parseApiError(e)?.message, 'error'),
    },
  )
}

const unequip = (inventoryId: number) => {
  unequipItem(
    { data: { inventory_id: inventoryId } },
    {
      onSuccess: () => showNotification('Avatar frame removed.', 'success'),
      onError: (e) => showNotification(parseApiError(e)?.message, 'error'),
    },
  )
}

const formatDate = (value: string) => new Date(value).toLocaleString('uk-UA')
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.grid { display: grid; gap: 10px; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
.item-card { background: var(--muted); }
.item-head { display: flex; justify-content: space-between; gap: 8px; align-items: center; }
.asset-preview { width: 100%; height: 180px; object-fit: contain; border-radius: 10px; background: var(--background); }
.desc { margin: 8px 0 4px; }
.meta { margin: 0 0 10px; color: var(--muted-foreground); font-size: 0.85rem; }
.button-group { display: flex; gap: 8px; }
@media (max-width: 760px) { .head { flex-direction: column; align-items: flex-start; } }
</style>
