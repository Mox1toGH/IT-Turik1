<template>
  <ui-card class="info-card" variant="form" :is-error="isLoadingUserError">
    <template #error>
      <div class="empty-state">
        <p>Failed to fetch profile info</p>
      </div>
    </template>

    <template #header>
      <div>
        <h2>Quick status</h2>
        <p class="text-muted">Readiness checks for your account.</p>
      </div>
    </template>

    <ui-skeleton-loader class="panel-body" :loading="isLoadingUser" min-height="90px">
      <template #skeleton>
        <div class="skeleton-stack">
          <ui-skeleton variant="rect" width="45%" />
          <ui-skeleton variant="rect" width="38%" />
          <ui-skeleton variant="rect" width="42%" />
        </div>
      </template>

      <ul class="status-list">
        <li v-for="item in statusItems" :key="item.label">
          <span class="status-dot" :class="{ ready: item.ready }" aria-hidden="true"></span>
          <span>{{ item.label }}</span>
          <strong>{{ item.ready ? 'Ready' : 'Missing' }}</strong>
        </li>
      </ul>
    </ui-skeleton-loader>
  </ui-card>
</template>

<script setup lang="ts">
import type { User } from '@/api/.ts.schemas'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { computed } from 'vue'

const props = defineProps<{
  user?: User
  isLoadingUserError: boolean
  isLoadingUser: boolean
}>()

const statusItems = computed(() => [
  { label: 'Profile ready', ready: !props.user?.needs_onboarding },
  { label: 'City set', ready: Boolean(props.user?.city) },
  { label: 'Phone set', ready: Boolean(props.user?.phone) },
])
</script>
