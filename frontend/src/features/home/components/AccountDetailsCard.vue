<template>
  <ui-card class="info-card" variant="form" :is-error="isLoadingUserError">
    <template #error>
      <div class="empty-state">
        <p>Failed to fetch account info</p>
      </div>
    </template>

    <template #header>
      <div>
        <h2>Account details</h2>
        <p class="text-muted">Profile identity and team membership.</p>
      </div>
    </template>

    <ui-skeleton-loader class="panel-body" :loading="isLoadingUser">
      <template #skeleton>
        <div class="skeleton-stack">
          <ui-skeleton variant="rect" width="55%" />
          <ui-skeleton variant="rect" width="65%" />
          <ui-skeleton variant="rect" width="35%" />
          <ui-skeleton variant="rect" width="70%" />
        </div>
      </template>

      <dl class="detail-list">
        <div v-for="item in accountDetails" :key="item.label">
          <dt>{{ item.label }}</dt>
          <dd>{{ item.value }}</dd>
        </div>
      </dl>
    </ui-skeleton-loader>
  </ui-card>
</template>

<script setup lang="ts">
import type { UserResponse } from '@/api/backendAPINinja.schemas'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { computed } from 'vue'

const props = defineProps<{
  user?: UserResponse
  isLoadingUser: boolean
  isLoadingUserError: boolean
}>()

const teamNames = computed(() => (props.user?.teams ?? []).map((team) => team.name).join(', '))

const accountDetails = computed(() => [
  { label: 'Username', value: props.user?.username || '-' },
  { label: 'Email', value: props.user?.email || '-' },
  { label: 'Role', value: props.user?.role || '-' },
  { label: 'Teams', value: teamNames.value || '-' },
])
</script>
