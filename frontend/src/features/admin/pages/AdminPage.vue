<template>
  <section class="page-shell">
    <section class="page-section admin-section">
      <header class="admin-hero">
        <div>
          <div class="breadcrumb-label">
            <span>Workspace</span>
            <span aria-hidden="true">/</span>
            <span>Admin</span>
          </div>

          <h1 class="text-6xl">Admin Panel</h1>
          <p class="section-subtitle text-xl">Choose an admin section to continue.</p>
        </div>
      </header>

      <div class="admin-rule" aria-hidden="true"></div>

      <div class="admin-links">
        <ui-card
          v-for="(section, index) in sections"
          :key="section.to"
          variant="form"
          class="form-panel admin-link-card"
        >
          <div class="panel-header">
            <span class="step-marker">{{ String(index + 1).padStart(2, '0') }}</span>
            <div>
              <h3>{{ section.title }}</h3>
              <p class="text-muted">{{ section.description }}</p>
            </div>
          </div>

          <ui-button as-link :to="section.to" class="card-btn">{{ section.cta }}</ui-button>
        </ui-card>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiButton from '@/components/ui/UiButton.vue'

const sections = [
  {
    title: 'Activation Codes',
    description: 'Generate and monitor one-time registration codes for restricted roles.',
    to: '/admin/role-codes',
    cta: 'Open Activation Codes',
  },
  {
    title: 'Certificates Admin',
    description: 'Create certificates, manage templates, and verify certificate codes.',
    to: '/admin/certificates',
    cta: 'Open Certificates Admin',
  },
]
</script>

<style scoped>
.admin-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--accent-strong);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.admin-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.admin-hero .section-subtitle {
  margin: 0.45rem 0 0;
  max-width: 780px;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.admin-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.admin-links {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.form-panel.card {
  display: grid;
  gap: 12px;
}

.admin-link-card {
  background: var(--muted);
}

.panel-header {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
}

.panel-header h3 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-lg, 1.1rem);
  font-weight: 800;
}

.panel-header p {
  margin: 0.2rem 0 0;
}

.card-btn {
  margin-top: auto;
  align-self: flex-start;
}

@media (max-width: 900px) {
  .admin-links {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .admin-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .admin-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .admin-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }
}
</style>
