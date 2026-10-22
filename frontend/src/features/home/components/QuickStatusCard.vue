<template>
  <ui-card class="info-card">
    <template #header>
      <div>
        <h2>Quick status</h2>
        <p class="text-muted">Readiness checks for your account.</p>
      </div>
    </template>

    <ui-query-block class="panel-body" :query="query">
      <template #error>
        <div class="empty-state">
          <p>Failed to fetch profile info</p>
        </div>
      </template>

      <ui-query-field>
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
      </ui-query-field>
    </ui-query-block>
  </ui-card>
</template>

<script setup lang="ts">
import type { UserSummary } from '@/shared/types/user'
import UiCard from '@/components/ui/UiCard'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import type { QueryLike } from '@/composables/useQueryState'
import { computed } from 'vue'

const props = defineProps<{
  user?: UserSummary
  query: QueryLike
}>()

const statusItems = computed(() => [
  { label: 'Profile ready', ready: !props.user?.needs_onboarding },
  { label: 'City set', ready: Boolean(props.user?.city) },
  { label: 'Phone set', ready: Boolean(props.user?.phone) },
])
</script>
