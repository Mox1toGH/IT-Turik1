<template>
  <header
    class="tournament-hero"
    :class="{ 'tournament-hero--with-banner': Boolean(tournament?.banner) }"
  >
    <button
      v-if="user?.role === 'admin'"
      class="banner-edit-btn"
      type="button"
      aria-label="Edit tournament banner"
      @click="isBannerModalOpen = true"
    >
      <avatar-edit-icon />
    </button>
    <div v-if="tournament?.banner" class="hero-banner" :style="heroBannerStyle" />
    <div v-if="tournament?.banner" class="hero-overlay" />
    <UpdateBannerModal v-model="isBannerModalOpen" :tournament-id="tournamentId" />

    <div class="hero-content tournament-hero-copy">
      <div class="breadcrumb-label">
        <span>Workspace</span>
        <span aria-hidden="true">/</span>
        <span>Tournament</span>
      </div>

      <h1 class="text-6xl">{{ tournament?.name ?? `Tournament ${tournamentId}` }}</h1>
      <p class="section-subtitle text-xl">
        Review tournament information, rounds, teams, and results.
      </p>
    </div>

    <div class="hero-actions hero-content">
      <ui-card variant="stat" class="tournament-stat-card">
        <span class="text-sm">Status:</span>
        <strong class="text-base">{{ tournament?.status ?? 'Loading' }}</strong>
      </ui-card>

      <ui-button asLink to="/tournaments" variant="secondary" size="lg" class="tournament-link">
        Back to tournaments
      </ui-button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import AvatarEditIcon from '@/icons/AvatarEditIcon.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useGetTournament } from '@/api/tournaments/tournaments'
import UpdateBannerModal from './modals/UpdateBannerModal.vue'
import { useBannerPosition } from '../../composables/useBannerPosition.ts'

const props = defineProps<{
  tournamentId: number
}>()

const isBannerModalOpen = ref(false)

const { data: user } = useGetUserProfile()
const { data: tournament } = useGetTournament(props.tournamentId)
const { objectPosition: bannerObjectPosition } = useBannerPosition(props.tournamentId)

const heroBannerStyle = computed(() =>
  tournament.value?.banner
    ? {
        backgroundImage: `url(${tournament.value.banner})`,
        backgroundPosition: bannerObjectPosition.value,
      }
    : {},
)
</script>

<style scoped>
.tournament-hero {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
  overflow: hidden;
  min-height: 220px;
  padding: 1.5rem;
  border: 1px solid var(--line-soft);
  border-radius: 20px;
  background: var(--card);
}

.hero-content {
  position: relative;
  z-index: 2;
}

.tournament-hero-copy {
  min-width: 0;
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
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.tournament-hero--with-banner h1,
.tournament-hero--with-banner .section-subtitle {
  color: #fff;
}

.tournament-hero--with-banner .breadcrumb-label {
  color: rgba(255, 255, 255, 0.78);
}

.hero-banner {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  z-index: 0;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  z-index: 1;
  background: linear-gradient(135deg, rgba(5, 11, 23, 0.78), rgba(5, 11, 23, 0.42));
}

.banner-edit-btn {
  position: absolute;
  top: 0.9rem;
  right: 0.9rem;
  z-index: 3;
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 999px;
  border: 1px solid var(--line-soft);
  background: var(--secondary);
  color: var(--secondary-foreground);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.banner-edit-btn:hover {
  border-color: var(--brand-500);
  color: var(--brand-700);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
  gap: 1rem;
}

.tournament-link {
  width: max-content;
}

.tournament-stat-card {
  display: flex;
}

.tournament-stat-card strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 800;
  text-transform: capitalize;
}

.tournament-stat-card span {
  color: var(--muted-foreground);
  font-weight: 700;
  white-space: nowrap;
}

.tournament-hero--with-banner .tournament-stat-card {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.tournament-hero--with-banner .tournament-stat-card strong,
.tournament-hero--with-banner .tournament-stat-card span {
  color: #fff;
}

@media (max-width: 810px) {
  .tournament-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
    min-height: 0;
    padding: 1.2rem;
  }

  .tournament-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .tournament-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
  }
}
</style>
