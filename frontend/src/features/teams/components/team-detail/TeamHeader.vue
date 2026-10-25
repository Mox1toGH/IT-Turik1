<template>
  <div class="team-detail-head">
    <page-back-link to="/teams" label="Back to teams" />
    <header class="team-detail-hero">
    <div class="team-detail-copy">
      <div class="breadcrumb-label">
        <span>Workspace</span>
        <span aria-hidden="true">/</span>
        <span>Teams</span>
        <span aria-hidden="true">/</span>
        <span>Details</span>
      </div>

      <ui-query-field :loading="props.loading">
        <template #skeleton>
          <div class="hero-skeleton">
            <ui-skeleton variant="rect" height="48px" width="320px" />
            <div class="hero-contacts">
              <ui-skeleton variant="rect" width="120px" />
              <ui-skeleton variant="rect" width="120px" />
            </div>
          </div>
        </template>
        <h1 class="team-detail-title">
          <ui-truncate :text="team?.name ?? 'Team details'" />
        </h1>

        <div class="hero-contacts">
          <a
            v-if="team?.contact_telegram"
            :href="telegramLink(team.contact_telegram)"
            class="contact-pill"
          >
            <telegram-icon class="contact-icon" />
            <ui-badge>@{{ team?.contact_telegram }}</ui-badge> </a
          ><span v-else class="contact-pill muted">No Telegram</span>

          <a
            v-if="team?.contact_discord"
            class="contact-pill"
            :href="discordLink(team.contact_discord)"
          >
            <discord-icon class="contact-icon" />
            <ui-badge>{{ team.contact_discord }}</ui-badge> </a
          ><span v-else class="contact-pill muted">No Discord</span>
        </div>
      </ui-query-field>
    </div>

    </header>
  </div>
</template>

<script setup lang="ts">
import TelegramIcon from '@/icons/TelegramIcon.vue'
import DiscordIcon from '@/icons/DiscordIcon.vue'
import PageBackLink from '@/components/shared/PageBackLink.vue'
import UiBadge from '@/components/ui/UiBadge'
import { UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UiTruncate from '@/components/ui/UiTruncate'
import { discordLink, telegramLink } from '../../lib/team-links'
import type { Team } from '@/features/teams/types'

interface Props {
  team?: Team
  loading: boolean
}

const props = defineProps<Props>()
</script>

<style scoped>
.team-detail-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.team-detail-head {
  display: grid;
  gap: 0.8rem;
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

.hero-contacts {
  display: flex;
  gap: 0.7rem;
  flex-wrap: wrap;
  margin-top: 0.8rem;
}

.hero-skeleton {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
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

}
</style>
