<template>
  <ui-card v-if="team?.banner || (isCaptain && !loading)" class="banner-card">
    <template #header>
      <div class="panel-header">
        <div class="banner-copy">
          <h2>Team banner</h2>
          <p class="text-muted">Cover image shown for this team.</p>
        </div>

        <ui-button
          v-if="isCaptain"
          size="sm"
          variant="secondary"
          class="banner-action"
          @click="emit('open')"
        >
          <Pencil class="banner-action-icon" />
          {{ team?.banner ? 'Edit' : 'Add banner' }}
        </ui-button>
      </div>
    </template>

    <div
      v-if="team?.banner"
      class="banner-frame"
      :style="heroBannerStyle"
      role="img"
      :aria-label="`Banner of ${team?.name ?? 'team'}`"
    ></div>

    <div v-else class="banner-frame banner-frame--empty">
      <span>No banner yet</span>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import { Pencil } from 'lucide-vue-next'
import type { Team } from '@/features/teams/types'

interface Props {
  team?: Team
  loading: boolean
  isCaptain: boolean
  heroBannerStyle: Record<string, string>
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'open'): void
}>()
</script>

<style scoped>
.banner-card {
  gap: 0.9rem;
}

.banner-card .panel-header {
  align-items: center;
}

.banner-copy {
  flex: 1 1 auto;
  min-width: 0;
}

.banner-action {
  flex: 0 0 auto;
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.banner-action-icon {
  width: 1rem;
  height: 1rem;
}

.banner-frame {
  width: 100%;
  aspect-ratio: 16 / 6;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background-color: var(--subtle);
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center;
}

.banner-frame--empty {
  display: flex;
  align-items: center;
  justify-content: center;
  border-style: dashed;
  color: var(--muted-foreground);
  font-size: 0.85rem;
}
</style>
