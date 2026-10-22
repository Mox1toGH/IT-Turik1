<template>
  <ui-card class="info-card">
    <template #header>
      <div>
        <h2>Account details</h2>
        <p class="text-muted">Profile identity and team membership.</p>
      </div>
    </template>

    <ui-query-block class="panel-body" :query="query">
      <template #error>
        <div class="empty-state">
          <p>Failed to fetch account info</p>
        </div>
      </template>

      <ui-query-field>
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

const teamNames = computed(() => (props.user?.teams ?? []).map((team) => team.name).join(', '))

const accountDetails = computed(() => [
  { label: 'Username', value: props.user?.username || '-' },
  { label: 'Email', value: props.user?.email || '-' },
  { label: 'Role', value: props.user?.role || '-' },
  { label: 'Teams', value: teamNames.value || '-' },
])
</script>
