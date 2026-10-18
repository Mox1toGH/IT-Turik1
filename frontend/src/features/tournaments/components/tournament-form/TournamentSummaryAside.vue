<template>
  <aside class="summary-panel" aria-label="Tournament summary">
    <ui-card class="summary-stat">
      <strong>{{ maxTeams }}</strong>
      <span>Teams</span>
    </ui-card>

    <ui-card class="summary-card">
      <p class="section-eyebrow">Draft summary</p>
      <h2>{{ name || 'Untitled tournament' }}</h2>
      <p
        v-if="truncateDescription"
        class="summary-description text-muted"
        :title="description"
      >
        {{ truncateText(description, 200) || 'Description will appear here as you write.' }}
      </p>
      <p v-else class="summary-description text-muted">
        {{ description || 'Description will appear here as you write.' }}
      </p>

      <div class="summary-list">
        <div class="summary-list-item">
          <span>Team size</span>
          <strong>{{ minTeamMembers }}+ members</strong>
        </div>
        <div class="summary-list-item">
          <span>Starts</span>
          <strong>{{ startsLabel }}</strong>
        </div>
        <div class="summary-list-item">
          <span>Ends</span>
          <strong>{{ endsLabel }}</strong>
        </div>
      </div>
    </ui-card>
  </aside>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'
import { truncateText } from '@/lib/utils'

withDefaults(
  defineProps<{
    name: string
    description: string
    maxTeams: number
    minTeamMembers: number
    startsLabel: string
    endsLabel: string
    truncateDescription?: boolean
  }>(),
  { truncateDescription: false },
)
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

.summary-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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
  -webkit-box-orient: vertical;
}

.summary-list {
  display: grid;
  padding-top: 0.15rem;
  border-top: 1px solid var(--border);
}

.summary-list-item {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.65rem 0;
  border-top: 1px solid var(--border);
}

.summary-list-item:first-child {
  border-top: 0;
}

.summary-list span {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
}

.summary-list strong {
  text-align: right;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

@media (max-width: 980px) {
  .summary-panel {
    position: static;
  }
}
</style>
