<template>
  <section class="page-shell">
    <StatsSection :user="user" />
  </section>
</template>

<script setup lang="ts">
import { useGetUserProfile } from '@/api/accounts/accounts'
import StatsSection from '@/components/stats/StatsSection.vue'

const { data: user } = useGetUserProfile()
</script>
