<template>
  <div class="tournament-hero-wrap">
    <div class="hero-topbar">
      <page-back-link to="/tournaments" label="Back to tournaments" />
    </div>

    <header
      class="tournament-hero"
      :class="{ 'tournament-hero--with-banner': Boolean(tournament?.banner) }"
    >
      <ui-query-field class="hero-data-state" :loading="isTournamentLoading">
        <template #skeleton>
          <div class="hero-fallback" aria-hidden="true" />
        </template>
        <template #default>
          <img
            v-if="tournament?.banner"
            class="hero-img"
            :src="tournament.banner"
            :alt="`${tournament?.name ?? 'Tournament'} banner`"
            :style="{ objectPosition: bannerObjectPosition }"
          />
          <div v-else class="hero-fallback" aria-hidden="true" />
          <div v-if="tournament?.banner" class="hero-overlay" aria-hidden="true" />
        </template>
      </ui-query-field>

      <div class="hero-content">
        <ui-query-field :loading="isTournamentLoading">
          <template #skeleton>
            <ui-skeleton variant="rect" width="min(480px, 75vw)" height="48px" />
          </template>
          <template #default>
            <h1 class="text-6xl">
              <ui-truncate :text="tournament?.name ?? `Tournament ${tournamentId}`" />
            </h1>
          </template>
        </ui-query-field>
        <p class="section-subtitle text-xl">
          Review tournament information, rounds, teams, and results.
        </p>
      </div>
    </header>

  </div>
</template>

<script setup lang="ts">
import PageBackLink from '@/components/shared/PageBackLink.vue'
import UiTruncate from '@/components/ui/UiTruncate'
import { UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { useGetTournament } from '@/api/tournaments/tournaments'
import { useBannerPosition } from '../../composables/useBannerPosition.ts'

const props = defineProps<{
  tournamentId: number
}>()

const tournamentQuery = useGetTournament(props.tournamentId)
const { isLoading: isTournamentLoading } = tournamentQuery
const { data: tournament } = tournamentQuery
const { objectPosition: bannerObjectPosition } = useBannerPosition(props.tournamentId)
</script>

<style scoped>
.tournament-hero-wrap {
  display: grid;
  gap: 0.75rem;
  min-width: 0;
}

.hero-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  min-width: 0;
}

.hero-data-state {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.hero-data-state :deep(.hero-fallback),
.hero-data-state :deep(.hero-img),
.hero-data-state :deep(.hero-overlay) {
  position: absolute;
  inset: 0;
}

.tournament-hero {
  position: relative;
  display: flex;
  align-items: flex-end;
  height: 200px;
  overflow: hidden;
  padding: 1.25rem 1.5rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
}

.hero-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-fallback {
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, var(--primary-soft), var(--subtle));
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    100deg,
    color-mix(in srgb, var(--scrim) 92%, transparent) 0%,
    color-mix(in srgb, var(--scrim) 45%, transparent) 55%,
    transparent 85%
  );
}

.hero-content {
  position: relative;
  z-index: 1;
  min-width: 0;
  max-width: 760px;
}

.tournament-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.tournament-hero .section-subtitle {
  margin: 0.45rem 0 0;
  max-width: 780px;
  color: var(--muted-foreground);
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.tournament-hero--with-banner h1 {
  color: var(--on-image);
}

.tournament-hero--with-banner .section-subtitle {
  color: var(--on-image);
  opacity: 0.85;
}

@media (max-width: 700px) {
  .tournament-hero {
    height: 160px;
    padding: 1rem;
  }

  .tournament-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .tournament-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }
}
</style>
