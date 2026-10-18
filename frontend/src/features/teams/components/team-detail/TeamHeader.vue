<template>
  <header class="team-detail-hero">
    <div class="team-detail-copy">
      <div class="breadcrumb-label">
        <span>Workspace</span>
        <span aria-hidden="true">/</span>
        <span>Teams</span>
        <span aria-hidden="true">/</span>
        <span>Details</span>
      </div>

      <ui-skeleton-loader :loading="loading">
        <template #skeleton>
          <ui-skeleton variant="rect" height="48px" width="320px" />
        </template>

        <h1 class="team-detail-title">
          <ui-truncate :text="team?.name ?? 'Team details'" />
        </h1>
      </ui-skeleton-loader>

      <div class="hero-contacts">
        <ui-skeleton-loader :loading="loading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="120px" />
          </template>
          <a
            v-if="team?.contact_telegram"
            :href="telegramLink(team.contact_telegram)"
            class="contact-pill"
          >
            <telegram-icon class="contact-icon" />
            <ui-badge>@{{ team?.contact_telegram }}</ui-badge>
          </a>
          <span v-else class="contact-pill muted">No Telegram</span>
        </ui-skeleton-loader>

        <ui-skeleton-loader :loading="loading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="120px" />
          </template>
          <a
            v-if="team?.contact_discord"
            class="contact-pill"
            :href="discordLink(team.contact_discord)"
          >
            <discord-icon class="contact-icon" />
            <ui-badge>{{ team.contact_discord }}</ui-badge>
          </a>

          <span v-else class="contact-pill muted">No Discord</span>
        </ui-skeleton-loader>
      </div>
    </div>

    <div class="hero-actions">
      <ui-button asLink variant="secondary" size="lg" to="/teams">Back to teams</ui-button>
    </div>
  </header>
</template>

<script setup lang="ts">
import TelegramIcon from '@/icons/TelegramIcon.vue'
import DiscordIcon from '@/icons/DiscordIcon.vue'
import UiButton from '@/components/ui/UiButton'
import UiBadge from '@/components/ui/UiBadge'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiTruncate from '@/components/ui/UiTruncate'
import { discordLink, telegramLink } from '../../lib/team-links'
import type { TeamResponse } from '@/api/backendAPINinja.schemas'

interface Props {
  team?: TeamResponse
  loading: boolean
}

defineProps<Props>()
</script>

<style scoped>
.team-detail-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.team-detail-copy {
  min-width: 0;
}

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.team-detail-title {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
}

.hero-contacts {
  display: flex;
  gap: 0.7rem;
  flex-wrap: wrap;
  margin-top: 0.8rem;
}

.contact-icon {
  width: 1.3rem;
  height: 1.3rem;
  color: var(--primary);
}

.contact-pill {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--foreground);
  text-decoration: none;
}

.muted {
  color: var(--muted-foreground);
}

@media (max-width: 720px) {
  .team-detail-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .team-detail-title {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
  }
}
</style>
