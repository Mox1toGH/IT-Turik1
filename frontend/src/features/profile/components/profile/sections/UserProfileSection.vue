<template>
  <section class="page-shell public-profile-page">
    <ui-query-block :query="userQuery" title="profile">
      <ui-query-field>
        <template #skeleton>
          <div class="profile-skeleton">
            <ui-skeleton variant="rounded" width="112px" height="112px" />
            <div class="skeleton-copy">
              <ui-skeleton variant="rect" width="260px" height="36px" />
              <ui-skeleton variant="rect" width="140px" height="20px" />
            </div>
            <ui-skeleton variant="rect" width="150px" height="40px" />
          </div>
          <ui-skeleton variant="rect" width="100%" height="280px" />
        </template>

        <div class="profile-content">
          <header class="profile-hero">
            <div class="identity">
              <user-avatar
                :avatar="user?.avatar"
                :username="user?.username || 'user'"
                :full-name="user?.full_name || ''"
                :size="112"
                :position-key="user?.id ? `image-position:avatar:user:${user.id}` : ''"
              />
              <div class="identity-copy">
                <h1>{{ user?.full_name || user?.username || 'User profile' }}</h1>
                <p class="username">@{{ user?.username || 'user' }}</p>
                <ui-badge variant="green">{{ user?.role || 'Member' }}</ui-badge>
              </div>
            </div>

            <div class="hero-actions">
              <div class="joined-meta">
                <span class="field-label">Joined</span>
                <strong>{{ user?.created_at ? formatDate(user.created_at) : 'N/A' }}</strong>
              </div>
              <ui-button
                as-link
                variant="secondary"
                size="sm"
                :to="`/users/${userId}/tournaments-history`"
              >
                Tournament history
              </ui-button>
            </div>
          </header>

          <div class="profile-grid">
            <ui-card class="details-card">
              <template #header>
                <div class="card-heading">
                  <div>
                    <p class="section-eyebrow">Profile</p>
                    <h2>About</h2>
                  </div>
                </div>
              </template>

              <dl class="details-grid">
                <div class="detail-item">
                  <dt>Email</dt>
                  <dd>{{ user?.email || '—' }}</dd>
                </div>
                <div class="detail-item">
                  <dt>Full name</dt>
                  <dd>{{ user?.full_name || '—' }}</dd>
                </div>
                <div class="detail-item">
                  <dt>City</dt>
                  <dd>{{ user?.city || '—' }}</dd>
                </div>
                <div class="detail-item">
                  <dt>Phone</dt>
                  <dd>{{ user?.phone || '—' }}</dd>
                </div>
              </dl>
            </ui-card>

            <div class="profile-side">
              <ui-card class="teams-card">
                <template #header>
                  <div class="card-heading card-heading-row">
                    <div>
                      <p class="section-eyebrow">Membership</p>
                      <h2>Teams</h2>
                    </div>
                    <span class="count-pill">{{ user?.teams?.length ?? 0 }}</span>
                  </div>
                </template>

                <div v-if="user?.teams?.length" class="team-list">
                  <router-link
                    v-for="team in user.teams"
                    :key="team.id"
                    :to="`/teams/${team.id}`"
                    class="team-link"
                  >
                    <span class="team-mark" aria-hidden="true">{{ team.name.slice(0, 1) }}</span>
                    <span>{{ team.name }}</span>
                    <span class="team-arrow" aria-hidden="true">↗</span>
                  </router-link>
                </div>
                <p v-else class="empty-copy">This user is not a member of any teams yet.</p>
              </ui-card>

              <ui-card v-if="user?.active_tournament" class="active-tournament-card">
                <template #header>
                  <div>
                    <p class="section-eyebrow">Currently competing</p>
                    <h2>Active tournament</h2>
                  </div>
                </template>
                <router-link
                  :to="`/tournaments/${user.active_tournament.id}`"
                  class="tournament-link"
                >
                  <span class="tournament-name">{{ user.active_tournament.name }}</span>
                  <span class="tournament-dates">
                    {{ formatDate(user.active_tournament.start_date) }} —
                    {{ formatDate(user.active_tournament.end_date) }}
                  </span>
                  <ui-badge variant="primary">{{ user.active_tournament.status }}</ui-badge>
                </router-link>
              </ui-card>
            </div>
          </div>
        </div>
      </ui-query-field>
    </ui-query-block>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import UiBadge from '@/components/ui/UiBadge'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import { useGetUser } from '@/api/accounts/accounts'
import { formatDate } from '@/lib/date'

const route = useRoute()
const userId = computed(() => Number(route.params.id))
const userQuery = useGetUser(userId)
const { data: user } = userQuery
</script>

<style scoped>
.public-profile-page {
  gap: 1.25rem;
}

.profile-content {
  display: grid;
  gap: 1.25rem;
  min-width: 0;
}

.profile-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
  padding: clamp(1.25rem, 3vw, 2rem);
  border: 1px solid var(--line-soft);
  border-radius: 20px;
  background:
    radial-gradient(
      ellipse at 8% 10%,
      color-mix(in srgb, var(--primary) 14%, transparent),
      transparent 44%
    ),
    var(--card);
  box-shadow: var(--shadow-card);
}

.identity {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  min-width: 0;
}

.identity-copy {
  display: grid;
  justify-items: start;
  gap: 0.4rem;
  min-width: 0;
}

.identity-copy h1 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: clamp(1.7rem, 4vw, 2.5rem);
  font-weight: 800;
  line-height: 1.1;
  overflow-wrap: anywhere;
}

.identity-copy,
.identity-copy .username {
  margin: 0;
}

.username {
  color: var(--muted-foreground);
}

.hero-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.9rem;
  flex: 0 0 auto;
}

.joined-meta {
  display: grid;
  gap: 0.15rem;
  text-align: right;
}

.joined-meta strong {
  color: var(--foreground);
  font-size: var(--text-sm);
}

.profile-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
  gap: 1rem;
  align-items: start;
}

.details-card,
.teams-card,
.active-tournament-card {
  min-width: 0;
  border-color: var(--line-soft);
}

.card-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.card-heading,
.card-heading h2 {
  margin: 0;
}

.card-heading h2 {
  margin-top: 0.2rem;
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 800;
}

.count-pill {
  display: inline-flex;
  min-width: 2rem;
  height: 2rem;
  align-items: center;
  justify-content: center;
  padding: 0 0.55rem;
  border-radius: 999px;
  background: var(--primary-soft);
  color: var(--primary);
  font-size: var(--text-xs);
  font-weight: 800;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin: 0;
  border-top: 1px solid var(--border);
}

.detail-item {
  display: grid;
  gap: 0.35rem;
  min-width: 0;
  padding: 0.95rem 0.75rem 0.95rem 0;
}

.detail-item:nth-child(n + 3) {
  border-top: 1px solid var(--border);
}

.detail-item dt,
.field-label {
  color: var(--muted-foreground);
  font-size: var(--text-xs);
  font-weight: 700;
}

.detail-item dd {
  margin: 0;
  color: var(--foreground);
  font-size: var(--text-sm);
  font-weight: 600;
  overflow-wrap: anywhere;
}

.profile-side {
  display: grid;
  gap: 1rem;
  min-width: 0;
}

.team-list {
  display: grid;
  gap: 0.5rem;
}

.team-link {
  display: grid;
  grid-template-columns: 2.25rem minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.65rem;
  min-width: 0;
  padding: 0.6rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--foreground);
  font-weight: 700;
  text-decoration: none;
  transition:
    border-color 0.15s ease,
    background-color 0.15s ease;
}

.team-link:hover {
  border-color: var(--primary);
  background: var(--subtle);
}

.team-mark {
  display: grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.65rem;
  background: var(--primary-soft);
  color: var(--primary);
  font-family: var(--font-display);
  font-weight: 900;
}

.team-link > span:nth-child(2) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.team-arrow {
  color: var(--muted-foreground);
}

.empty-copy {
  margin: 0;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
}

.tournament-link {
  display: grid;
  justify-items: start;
  gap: 0.5rem;
  padding: 0.9rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--subtle);
  color: inherit;
  text-decoration: none;
  transition: border-color 0.15s ease;
}

.tournament-link:hover {
  border-color: var(--primary);
}

.tournament-name {
  color: var(--foreground);
  font-weight: 800;
}

.tournament-dates {
  color: var(--muted-foreground);
  font-size: var(--text-xs);
}

.profile-skeleton {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
  border: 1px solid var(--border);
  border-radius: 20px;
  background: var(--card);
}

.skeleton-copy {
  display: grid;
  flex: 1;
  gap: 0.65rem;
}

@media (max-width: 820px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 620px) {
  .profile-hero {
    align-items: flex-start;
    flex-direction: column;
  }

  .hero-actions {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    width: 100%;
  }

  .joined-meta {
    text-align: left;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }

  .detail-item:nth-child(n + 2) {
    border-top: 1px solid var(--border);
  }

  .profile-skeleton {
    flex-wrap: wrap;
  }
}

@media (max-width: 430px) {
  .identity {
    align-items: flex-start;
    flex-direction: column;
  }

  .hero-actions {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (prefers-reduced-motion: reduce) {
  .team-link,
  .tournament-link {
    transition: none;
  }
}
</style>
