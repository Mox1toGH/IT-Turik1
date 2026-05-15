<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div>
          <p class="section-eyebrow">Admin</p>
          <h1 class="section-title">Admin Panel</h1>
          <p class="section-subtitle">Choose an admin section to continue.</p>
        </div>
      </template>

      <div class="admin-links">
        <ui-card class="admin-link-card">
          <template #header>
            <h2 class="card-title">Activation Codes</h2>
          </template>

          <p class="text-muted">Generate and monitor one-time registration codes for restricted roles.</p>
          <ui-button as-link to="/admin/role-codes" class="card-btn">Open Activation Codes</ui-button>
        </ui-card>

        <ui-card class="admin-link-card">
          <template #header>
            <h2 class="card-title">Certificates Admin</h2>
          </template>

          <p class="text-muted">Create certificates, manage templates, and verify certificate codes.</p>
          <ui-button as-link to="/admin/certificates" class="card-btn">Open Certificates Admin</ui-button>
        </ui-card>
      </div>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'
</script>

<style scoped>
.admin-links {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.admin-link-card {
  background: var(--muted);
}

.card-title {
  font-size: 1.1rem;
  font-weight: 700;
}

.card-btn {
  margin-top: 0.8rem;
}

@media (max-width: 900px) {
  .admin-links {
    grid-template-columns: 1fr;
  }
}
</style>
