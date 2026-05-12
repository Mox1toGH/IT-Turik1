<template>
  <section class="page-shell home-page">
    <ui-card class="hero">
      <div>
        <p class="eyebrow">Dashboard</p>
        <h1>
          Welcome back,
          <ui-skeleton-loader :loading="isLoading" style="display: inline-block">
            <template #skeleton>
              <ui-skeleton variant="rect" width="160px" />
            </template>

            <span>{{ displayName }}</span>
          </ui-skeleton-loader>
        </h1>

        <p class="sub">Manage your profile and stay ready for upcoming competitions.</p>
      </div>
    </ui-card>

    <div class="grid">
      <ui-card class="info-card" :is-error="isLoadingError">
        <template #error>
          <div
            style="
              width: 100%;
              height: 100%;
              display: flex;
              justify-content: center;
              align-items: center;
              height: 126px;
            "
          >
            <p>Failed to fetch account info (code: {{ error?.code }})</p>
          </div>
        </template>

        <template #header>
          <h2>Account details</h2>
        </template>

        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <div style="display: flex; flex-direction: column; gap: 10px">
              <ui-skeleton variant="rect" width="55%" />
              <ui-skeleton variant="rect" width="65%" />
              <ui-skeleton variant="rect" width="35%" />
              <ui-skeleton variant="rect" width="70%" />
            </div>
          </template>

          <div class="account-data">
            <p><strong>Username:</strong> {{ user?.username ?? '-' }}</p>
            <p><strong>Email:</strong> {{ user?.email ?? '-' }}</p>
            <p><strong>Role:</strong> {{ user?.role ?? '-' }}</p>
            <p v-if="teamNames"><strong>Teams:</strong> {{ teamNames }}</p>
          </div>
        </ui-skeleton-loader>
      </ui-card>

      <ui-card class="info-card" :is-error="isLoadingError">
        <template #error>
          <div
            style="
              width: 100%;
              height: 100%;
              display: flex;
              justify-content: center;
              align-items: center;
            "
          >
            <p>Failed to fetch profile status (code: {{ error?.code }})</p>
          </div>
        </template>

        <template #header>
          <h2>Quick status</h2>
        </template>

        <ui-skeleton-loader :loading="isLoading" min-height="90px">
          <template #skeleton>
            <div style="display: flex; flex-direction: column; gap: 10px">
              <ui-skeleton variant="rect" width="45%" />
              <ui-skeleton variant="rect" width="38%" />
              <ui-skeleton variant="rect" width="42%" />
            </div>
          </template>

          <ul class="account-data">
            <li>
              Profile ready: <span>{{ profileReady ? 'Yes' : 'No' }}</span>
            </li>
            <li>
              City set: <span>{{ user?.city ? 'Yes' : 'No' }}</span>
            </li>
            <li>
              Phone set: <span>{{ user?.phone ? 'Yes' : 'No' }}</span>
            </li>
          </ul>
        </ui-skeleton-loader>
      </ui-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import { useProfile } from '@/api/queries/accounts'
import { parseApiError } from '@/api/errors'

const { data: user, isLoading, isLoadingError, error: profileError } = useProfile()
const error = computed(() => parseApiError(profileError.value))

const displayName = computed(() => user.value?.full_name || user.value?.username || 'User')
const profileReady = computed(() => Boolean(user.value?.full_name && user.value?.city))
const teamNames = computed(() => (user.value?.teams || []).map((team) => team.name).join(', '))
</script>

<style scoped>
.home-page {
  display: grid;
  gap: 1rem;
}

.hero {
  padding: 1.4rem;
  background:
    linear-gradient(130deg, rgba(15, 118, 110, 0.95), rgba(20, 184, 166, 0.88)),
    linear-gradient(45deg, rgba(249, 115, 22, 0.2), transparent);
  color: white;
  border: none;
}

.eyebrow {
  margin: 0;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.75rem;
  opacity: 0.85;
}

h1 {
  margin: 0.45rem 0 0;
  font-family: var(--font-display);
  font-size: clamp(1.4rem, 1.3vw + 1rem, 2rem);
}

.sub {
  margin: 0.5rem 0 0;
  opacity: 0.92;
}

.hero-actions {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.account-data {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-card h2 {
  margin-top: 0;
  font-family: var(--font-display);
}

.info-card p,
li {
  color: var(--muted-foreground);
}

ul {
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.55rem;
}

li {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px dashed var(--line-soft);
  padding-bottom: 0.35rem;
}

li span {
  font-weight: 700;
}

@media (max-width: 760px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-actions {
    justify-content: flex-start;
  }

  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
