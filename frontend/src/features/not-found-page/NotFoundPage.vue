<template>
  <ui-card class="not-found-card">
    <div>
      <h1 class="title">Page not found</h1>
      <p class="text">The page you’re looking for doesn’t exist or was moved.</p>
      <div class="actions">
        <ui-button asLink to="/">Go home</ui-button>
        <ui-button variant="secondary" asLink to="/tournaments">Browse tournaments</ui-button>
      </div>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
</script>

<style scoped>
.not-found-card {
  max-width: 720px;
  margin: 0 auto;
}

.title {
  margin: 0;
}

.text {
  margin: 0.5rem 0 0;
  color: color-mix(in srgb, var(--foreground) 70%, transparent);
}

.actions {
  display: flex;
  gap: 0.6rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}
</style>
