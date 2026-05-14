<template>
  <div class="private-team-wrapper">
    <ui-card class="private-team-card">
      <div class="content">
        <div class="icon-section">
          <div class="icon-blob"></div>
          <div class="icon-wrapper">
            <lock-icon class="lock-icon" />
          </div>
        </div>
      <div class="text-section">
        <h1 class="title">Team is Private</h1>
        <p class="text">
          This team is set to private. Only team members and platform administrators have access to view it.
        </p>
      </div>
      <div class="actions">
        <ui-button asLink to="/teams" class="primary-action">
          <template #prefix>
            <arrow-left class="btn-icon" />
          </template>
          Back to teams
        </ui-button>
        <ui-button variant="secondary" asLink to="/" class="secondary-action">
          Go home
        </ui-button>
      </div>
      </div>
    </ui-card>
  </div>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import LockIcon from '@/icons/LockIcon.vue'
import ArrowLeft from '@/icons/ArrowLeft.vue'
</script>

<style scoped>
.private-team-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  padding: 2rem;
}

.private-team-card {
  max-width: 520px;
  width: 100%;
  border: 1px solid var(--line-soft);
  box-shadow: var(--shadow-lg);
  overflow: visible;
}

.content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  padding: 1rem;
}

.icon-section {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
}

.icon-blob {
  position: absolute;
  width: 100%;
  height: 100%;
  background: var(--brand-500);
  filter: blur(25px);
  opacity: 0.15;
  border-radius: 50%;
  animation: pulse 4s infinite ease-in-out;
}

.icon-wrapper {
  position: relative;
  z-index: 1;
  width: 80px;
  height: 80px;
  background: var(--card);
  border: 1px solid var(--line-soft);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  transform: rotate(-5deg);
}

.lock-icon {
  width: 36px;
  height: 36px;
  color: var(--brand-500);
}

.text-section {
  text-align: center;
}

.title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--foreground);
  margin-bottom: 0.75rem;
}

.text {
  margin: 0;
  color: var(--muted-foreground);
  line-height: 1.6;
  font-size: 1.05rem;
}

.actions {
  display: flex;
  gap: 0.75rem;
  width: 100%;
}

.primary-action {
  flex: 2;
}

.secondary-action {
  flex: 1;
}

.btn-icon {
  width: 1.2rem;
  height: 1.2rem;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.15; }
  50% { transform: scale(1.2); opacity: 0.25; }
}

@media (max-width: 480px) {
  .actions {
    flex-direction: column;
  }
  
  .primary-action, .secondary-action {
    width: 100%;
  }
  
  .title {
    font-size: 1.5rem;
  }
}
</style>
