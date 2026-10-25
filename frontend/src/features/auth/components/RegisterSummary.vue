<template>
  <aside class="summary-panel" aria-label="Registration summary">
    <ui-card class="summary-stat">
      <strong>{{ isRestrictedRole ? 'Code' : 'Open' }}</strong>
      <span>{{ isRestrictedRole ? 'Invite required' : 'No invite needed' }}</span>
    </ui-card>

    <ui-card class="summary-card">
      <p class="section-eyebrow">Draft summary</p>
      <h2>{{ username || 'New account' }}</h2>
      <p class="summary-description text-muted">
        {{ email || 'Email will appear here when added.' }}
      </p>

      <div class="summary-list">
        <div>
          <span>Role</span>
          <strong>{{ roleLabel }}</strong>
        </div>
        <div>
          <span>Name</span>
          <strong>{{ fullName || 'Not set' }}</strong>
        </div>
        <div>
          <span>City</span>
          <strong>{{ city || 'Not set' }}</strong>
        </div>
      </div>
    </ui-card>
  </aside>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'

interface Props {
  username: string
  email: string
  fullName: string
  city: string
  roleLabel: string
  isRestrictedRole: boolean
}

defineProps<Props>()
</script>

<style scoped>
.summary-panel {
  position: sticky;
  top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

.summary-stat strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  line-height: var(--text-2xl--line-height);
  font-weight: 800;
}

.summary-stat span {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
  white-space: nowrap;
}

.summary-stat {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  gap: 0.7rem;
  padding: 0.5rem 1.1rem;
  min-height: 30px;
  border-color: var(--border);
}

.summary-card.card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-radius: 18px;
  border-color: var(--border);
}

.summary-card h2 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
  font-weight: 800;
}

.summary-description {
  display: -webkit-box;
  min-height: 3.2rem;
  margin: 0;
  overflow: hidden;
  line-clamp: 3;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.summary-list {
  display: grid;
  padding-top: 0.15rem;
  border-top: 1px solid var(--border);
}

.summary-list div {
  display: grid;
  grid-template-columns: minmax(0, 0.8fr) minmax(0, 1fr);
  gap: 0.75rem;
  padding: 0.8rem 0;
}

.summary-list div + div {
  border-top: 1px solid var(--border);
}

.summary-list span {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
}

.summary-list strong {
  overflow: hidden;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

@media (max-width: 980px) {
  .summary-panel {
    position: static;
  }
}
</style>
