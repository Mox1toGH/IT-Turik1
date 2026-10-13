<template>
  <AdminStats v-if="user?.is_staff" />
  <PlayerStats v-else-if="user" :user="user" />
</template>

<script setup lang="ts">
import AdminStats from './AdminStats.vue'
import PlayerStats from './PlayerStats.vue'
import type { UserRole } from '@/api/backendAPINinja.schemas'

type TeamRef = { id: number; name: string }
type ProfileLike = {
  role?: UserRole
  is_staff?: boolean
  readonly teams?: readonly TeamRef[]
}

interface Props {
  user?: ProfileLike | null
}

defineProps<Props>()
</script>
