<template>
  <a v-if="part.type === 'user'" :href="`/users/${part.id}`" class="user-link" @click.stop>
    {{ part.text }}
  </a>
  <router-link
    v-else-if="part.type === 'team'"
    :to="`/teams/${part.id}`"
    class="user-link"
    @click.stop
  >
    {{ part.text }}
  </router-link>
  <router-link
    v-else-if="part.type === 'news'"
    :to="`/news#news-${part.id}`"
    class="user-link"
    @click.stop
  >
    {{ part.text }}
  </router-link>
  <span v-else>{{ part.text }}</span>
</template>

<script setup lang="ts">
import type { NotificationMessagePart } from '../../composables/useNotifications'

defineProps<{
  part: NotificationMessagePart
}>()
</script>

<style scoped>
.user-link {
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
}

.user-link:hover {
  text-decoration: underline;
  text-underline-offset: 2px;
}
</style>
