<template>
  <aside class="summary-panel" aria-label="Team summary">
    <ui-card class="summary-stat">
      <strong>{{ selectedMembersCount }}</strong>
      <span>Initial members</span>
    </ui-card>

    <ui-card class="summary-card">
      <p class="section-eyebrow">Draft summary</p>
      <h2>
        <ui-truncate :text="teamName || 'Untitled team'" />
      </h2>
      <p class="summary-description text-muted">
        {{ organization || 'Organization will appear here when added.' }}
      </p>

      <div class="summary-list">
        <div class="summary-row">
          <span>Visibility</span>
          <strong>{{ isPublic ? 'Public' : 'Private' }}</strong>
        </div>
        <div class="summary-row">
          <span>Email</span>
          <strong>
            <ui-truncate :text="email || 'Not set'" />
          </strong>
        </div>
        <div class="summary-row">
          <span>Contact</span>
          <strong>{{ contactSummary }}</strong>
        </div>
      </div>
    </ui-card>
  </aside>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'
import UiTruncate from '@/components/ui/UiTruncate'

interface Props {
  selectedMembersCount: number
  contactSummary: string
  teamName?: string
  organization?: string
  email?: string
  isPublic?: boolean
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

.summary-stat strong {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  line-height: var(--text-2xl--line-height);
  font-weight: 800;
}

.summary-stat span {
  color: var(--muted-foreground);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.summary-card.card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-color: var(--border);
}

.summary-card h2 {
  margin: 0;
  min-width: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
  font-weight: 800;
}

.summary-description {
  min-height: 3.2rem;
  margin: 0;
  overflow-wrap: anywhere;
}

.summary-list {
  display: grid;
  gap: 0;
  padding-top: 0.15rem;
  border-top: 1px solid var(--border);
}

.summary-row {
  display: grid;
  grid-template-columns: minmax(0, 0.8fr) minmax(0, 1fr);
  gap: 0.75rem;
  padding: 0.8rem 0;
}

.summary-row + .summary-row {
  border-top: 1px solid var(--border);
}

.summary-list span {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
}

.summary-row strong {
  min-width: 0;
  text-align: right;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  overflow-wrap: anywhere;
}

@media (max-width: 980px) {
  .summary-panel {
    position: static;
  }
}
</style>
