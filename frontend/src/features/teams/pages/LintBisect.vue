<template>
  <div>
    <team-invitations :loading="x" />
  </div>
</template>

<script setup lang="ts">
import TeamInvitations from '../components/team-edit/TeamInvitations.vue'
const x = false
</script>
