<template>
  <section class="page-shell">
    <StatsSection :user="user" />
  </section>
</template>

<script setup lang="ts">
import StatsSection from '@/components/stats/StatsSection.vue'
import { useProfile } from '@/api/queries/accounts'

const { data: user } = useProfile()
</script>
