<template>
  <section class="page-shell settings-page">
    <header class="settings-hero">
      <div class="settings-hero-copy">
        <div class="breadcrumb-label">
          <span>User Center</span>
          <span aria-hidden="true">/</span>
          <span>Notifications</span>
          <span aria-hidden="true">/</span>
          <span>Settings</span>
        </div>

        <h1 class="text-4xl">Notification settings</h1>
        <p class="section-subtitle text-base">Choose which notifications you receive and how.</p>
      </div>

      <div class="settings-hero-actions">
        <span v-if="saveState === 'saved'" class="save-indicator">
          <Check class="save-icon" />
          Saved
        </span>
        <span v-else-if="saveState === 'saving'" class="save-indicator saving">
          <LoaderCircle class="save-icon animate-spin" :size="16" />
          Saving…
        </span>
        <span v-else-if="saveState === 'error'" class="save-indicator error">
          <CircleAlert class="save-icon" />
          Error
        </span>
        <ui-button variant="secondary" size="sm" @click="router.push('/profile/notifications')">
          <ArrowLeft class="btn-icon" />
          Back to notifications
        </ui-button>
      </div>
    </header>

    <div class="settings-rule" aria-hidden="true"></div>

    <div class="settings-layout">
      <aside class="settings-sidebar">
        <div class="sidebar-sticky">
          <div class="search-wrap">
            <Search class="search-icon" />
            <ui-input v-model="search" placeholder="Search events..." class="search-input" />
          </div>

          <ui-card class="sidebar-card">
            <template #header>
              <div class="sidebar-card-header">
                <p class="section-eyebrow">Sections</p>
              </div>
            </template>
            <nav class="anchor-nav" aria-label="Notification sections">
              <a
                v-for="group in visibleGroups"
                :key="group.key"
                :href="`#${group.key}`"
                class="anchor-chip"
                @click.prevent="scrollToGroup(group.key)"
              >
                {{ group.label }}
              </a>
            </nav>
          </ui-card>

          <ui-card class="sidebar-card">
            <template #header>
              <div class="sidebar-card-header">
                <p class="section-eyebrow">Quick actions</p>
              </div>
            </template>
            <div class="quick-actions">
              <ui-button variant="secondary" size="sm" @click="enableAll">Enable all</ui-button>
              <ui-button variant="secondary" size="sm" @click="disableAll">Disable all</ui-button>
              <ui-button variant="secondary" size="sm" @click="confirmReset">
                Reset to defaults
              </ui-button>
            </div>
          </ui-card>
        </div>
      </aside>

      <ui-query-block :query="settingsQuery" title="notification settings">
        <div class="settings-content">
          <ui-card class="global-card">
            <template #header>
              <div class="global-header">
                <div>
                  <p class="section-eyebrow">Email</p>
                  <h2 class="text-xl">Email notifications</h2>
                </div>
              </div>
            </template>
            <div class="global-body">
              <div class="global-toggle-row">
                <div class="global-toggle-info">
                  <span class="global-toggle-title">Disable all email notifications</span>
                  <span class="global-toggle-desc">
                    You will not receive any emails from the system. Individual email settings are
                    preserved but ignored.
                  </span>
                </div>
                <ui-query-field>
                  <template #skeleton>
                    <ui-skeleton
                      class="global-toggle-state"
                      variant="rect"
                      width="44px"
                      height="24px"
                    />
                  </template>
                  <ui-switch
                    class="global-toggle-state"
                    :modelValue="globalEmailsDisabled"
                    @update:modelValue="handleGlobalToggle"
                    aria-label="Disable all email notifications"
                  />
                </ui-query-field>
              </div>
            </div>
          </ui-card>

          <ui-query-field>
            <template #skeleton>
              <div class="settings-state">
                <ui-skeleton variant="rect" height="200px" width="100%" />
                <ui-skeleton variant="rect" height="200px" width="100%" style="margin-top: 1rem" />
              </div>
            </template>

            <template #default>
              <p v-if="visibleGroups.length === 0" class="text-muted settings-empty">
                {{ emptyGroupsText }}
              </p>
              <div
                v-else
                v-for="group in visibleGroups"
                :key="group.key"
                :id="group.key"
                class="settings-group"
              >
                <ui-card>
                  <template #header>
                    <div class="group-header">
                      <div class="group-header-text">
                        <h3 class="text-lg">{{ group.label }}</h3>
                        <p class="group-count">{{ group.events.length }} events</p>
                      </div>
                      <div class="group-bulk">
                        <div class="bulk-toggle">
                          <span class="bulk-label">All system</span>
                          <ui-switch
                            :modelValue="getGroupAllSystem(group.key)"
                            :indeterminate="getGroupIndeterminateSystem(group.key)"
                            @update:modelValue="(val) => setGroupAllSystem(group.key, val)"
                            :aria-label="`${group.label} – All system`"
                          />
                        </div>
                        <div class="bulk-toggle">
                          <span class="bulk-label">All email</span>
                          <ui-switch
                            :modelValue="getGroupAllEmail(group.key)"
                            :indeterminate="getGroupIndeterminateEmail(group.key)"
                            @update:modelValue="(val) => setGroupAllEmail(group.key, val)"
                            :disabled="globalEmailsDisabled"
                            :aria-label="`${group.label} – All email`"
                          />
                        </div>
                      </div>
                    </div>
                  </template>

                  <div class="group-table-header">
                    <span class="col-event">Event</span>
                    <span class="col-toggle">System</span>
                    <span class="col-toggle">Email</span>
                  </div>

                  <div class="group-events">
                    <div v-for="event in group.events" :key="event.key" class="event-row">
                      <div class="event-info">
                        <span class="event-title">{{ event.title }}</span>
                        <span v-if="event.description" class="event-desc">{{
                          event.description
                        }}</span>
                      </div>
                      <div class="event-toggles">
                        <div class="toggle-cell">
                          <ui-switch
                            :modelValue="getEventSystemEnabled(event.key)"
                            @update:modelValue="(val) => setEventSystemEnabled(event.key, val)"
                            :aria-label="`${event.title} – System`"
                          />
                        </div>
                        <div class="toggle-cell">
                          <ui-switch
                            :modelValue="getEventEmailEnabled(event.key)"
                            @update:modelValue="(val) => setEventEmailEnabled(event.key, val)"
                            :disabled="globalEmailsDisabled"
                            :aria-label="`${event.title} – Email`"
                            :title="
                              globalEmailsDisabled
                                ? 'Email notifications are disabled globally'
                                : undefined
                            "
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </ui-card>
              </div>
            </template>
          </ui-query-field>
        </div>
      </ui-query-block>
    </div>

    <ui-modal v-model="showResetConfirm" title="Reset to defaults" max-width="400px">
      <p>Are you sure you want to reset all notification settings to their default values?</p>
      <template #footer>
        <ui-button variant="secondary" size="sm" @click="showResetConfirm = false">
          Cancel
        </ui-button>
        <ui-button variant="danger" size="sm" @click="handleReset"> Reset </ui-button>
      </template>
    </ui-modal>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import UiCard from '@/components/ui/UiCard'
import UiInput from '@/components/ui/UiInput'
import UiSwitch from '@/components/ui/UiSwitch'
import UiButton from '@/components/ui/UiButton'
import UiModal from '@/components/ui/UiModal'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import { useNotification } from '@/composables/useNotification'
import {
  useGetNotificationSettings,
  useUpdateNotificationConfig,
  useUpdateGlobalNotificationConfig,
} from '@/api/notifications/notifications'
import { Search, Check, CircleAlert, ArrowLeft, LoaderCircle } from 'lucide-vue-next'

const router = useRouter()
const { showNotification } = useNotification()

const search = ref('')
const showResetConfirm = ref(false)
const saveState = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')

const settingsQuery = useGetNotificationSettings()
const { data: settings } = settingsQuery
const { mutate: updateEvent } = useUpdateNotificationConfig()
const { mutate: updateGlobal } = useUpdateGlobalNotificationConfig()

// ─── Event grouping ───────────────────────────────────────────────

interface EventGroup {
  key: string
  label: string
  events: { key: string; title: string; description?: string }[]
}

const GROUP_DEFINITIONS: { key: string; label: string; prefixes: string[] }[] = [
  { key: 'teams', label: 'Teams', prefixes: ['team_'] },
  { key: 'tournaments', label: 'Tournaments', prefixes: ['tournament_'] },
  { key: 'rounds', label: 'Rounds', prefixes: ['round_'] },
  { key: 'submissions', label: 'Submissions', prefixes: ['submission_'] },
  { key: 'evaluation', label: 'Evaluation / Jury', prefixes: ['jury_', 'evaluation_'] },
  { key: 'news', label: 'News', prefixes: ['news_'] },
]

const EVENT_DESCRIPTIONS: Record<string, string> = {
  team_invitation_received: 'When someone invites you to join a team',
  team_invitation_accepted: 'When your invitation is accepted',
  team_invitation_declined: 'When your invitation is declined',
  team_join_request_received: 'When someone requests to join your team',
  team_join_request_accepted: 'When your join request is approved',
  team_join_request_declined: 'When your join request is declined',
  team_member_removed: 'When you are removed from a team',
  team_member_left: 'When a member leaves your team',
  tournament_team_registered: 'When your team is registered for a tournament',
  tournament_team_unregistered: 'When your team is removed from a tournament',
  tournament_team_disqualified: 'When your team is disqualified',
  tournament_team_reactivated: 'When your team is reinstated',
  tournament_round_started: 'When a new round begins',
  tournament_round_submissions_closed: 'When submissions close for a round',
  tournament_round_evaluated: 'When a round is evaluated',
  tournament_finished: 'When a tournament finishes',
  jury_assignment_received: 'When you are assigned to evaluate submissions',
  news_published: 'When a new announcement is published',
}

const groups = computed<EventGroup[]>(() => {
  if (!settings.value) return []

  const allEvents = settings.value.event_types
  const grouped: EventGroup[] = []
  const used = new Set<string>()

  for (const def of GROUP_DEFINITIONS) {
    const events = allEvents
      .filter((e) => def.prefixes.some((p) => e.key.startsWith(p)))
      .map((e) => ({
        key: e.key,
        title: e.title,
        description: EVENT_DESCRIPTIONS[e.key],
      }))
    if (events.length > 0) {
      grouped.push({ key: def.key, label: def.label, events })
      events.forEach((e) => used.add(e.key))
    }
  }

  const otherEvents = allEvents
    .filter((e) => !used.has(e.key))
    .map((e) => ({
      key: e.key,
      title: e.title,
      description: EVENT_DESCRIPTIONS[e.key],
    }))
  if (otherEvents.length > 0) {
    grouped.push({ key: 'other', label: 'Other', events: otherEvents })
  }

  return grouped
})

const visibleGroups = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return groups.value
  return groups.value
    .map((g) => ({
      ...g,
      events: g.events.filter((e) => e.title.toLowerCase().includes(q)),
    }))
    .filter((g) => g.events.length > 0)
})

const emptyGroupsText = computed(() =>
  search.value.trim() ? 'No events match your search.' : 'No notification events are available.',
)

// ─── State helpers ────────────────────────────────────────────────

const globalEmailsDisabled = computed(
  () => settings.value?.global_config.emails_disabled_globally ?? false,
)

function getConfig(eventType: string) {
  return settings.value?.configs.find((c) => c.event_type === eventType)
}

function getEventSystemEnabled(eventType: string): boolean {
  return getConfig(eventType)?.is_system_enabled ?? true
}

function getEventEmailEnabled(eventType: string): boolean {
  return getConfig(eventType)?.is_email_enabled ?? true
}

function getGroupAllSystem(groupKey: string): boolean {
  const group = groups.value.find((g) => g.key === groupKey)
  if (!group) return false
  return group.events.every((e) => getEventSystemEnabled(e.key))
}

function getGroupIndeterminateSystem(groupKey: string): boolean {
  const group = groups.value.find((g) => g.key === groupKey)
  if (!group) return false
  const allOn = group.events.every((e) => getEventSystemEnabled(e.key))
  const allOff = group.events.every((e) => !getEventSystemEnabled(e.key))
  return !allOn && !allOff
}

function getGroupAllEmail(groupKey: string): boolean {
  const group = groups.value.find((g) => g.key === groupKey)
  if (!group) return false
  return group.events.every((e) => getEventEmailEnabled(e.key))
}

function getGroupIndeterminateEmail(groupKey: string): boolean {
  const group = groups.value.find((g) => g.key === groupKey)
  if (!group) return false
  const allOn = group.events.every((e) => getEventEmailEnabled(e.key))
  const allOff = group.events.every((e) => !getEventEmailEnabled(e.key))
  return !allOn && !allOff
}

// ─── Mutations ────────────────────────────────────────────────────

let saveTimeout: ReturnType<typeof setTimeout> | null = null

function scheduleSave() {
  saveState.value = 'saving'
  if (saveTimeout) clearTimeout(saveTimeout)
  saveTimeout = setTimeout(() => {
    saveState.value = 'saved'
    setTimeout(() => {
      saveState.value = 'idle'
    }, 2000)
  }, 800)
}

function setEventSystemEnabled(eventType: string, val: boolean) {
  updateEvent(
    { data: { event_type: eventType, is_system_enabled: val } },
    {
      onSuccess: () => scheduleSave(),
      onError: (err) => {
        saveState.value = 'error'
        showNotification(err.message, 'error')
      },
    },
  )
}

function setEventEmailEnabled(eventType: string, val: boolean) {
  updateEvent(
    { data: { event_type: eventType, is_email_enabled: val } },
    {
      onSuccess: () => scheduleSave(),
      onError: (err) => {
        saveState.value = 'error'
        showNotification(err.message, 'error')
      },
    },
  )
}

function setGroupAllSystem(groupKey: string, val: boolean) {
  const group = groups.value.find((g) => g.key === groupKey)
  if (!group) return
  group.events.forEach((e) => {
    if (getEventSystemEnabled(e.key) !== val) {
      setEventSystemEnabled(e.key, val)
    }
  })
}

function setGroupAllEmail(groupKey: string, val: boolean) {
  const group = groups.value.find((g) => g.key === groupKey)
  if (!group) return
  group.events.forEach((e) => {
    if (getEventEmailEnabled(e.key) !== val) {
      setEventEmailEnabled(e.key, val)
    }
  })
}

function handleGlobalToggle(val: boolean) {
  updateGlobal(
    { data: { emails_disabled_globally: val } },
    {
      onSuccess: () => {
        scheduleSave()
        showNotification(
          val ? 'All email notifications disabled' : 'Email notifications enabled',
          'success',
        )
      },
      onError: (err) => {
        saveState.value = 'error'
        showNotification(err.message, 'error')
      },
    },
  )
}

function enableAll() {
  groups.value.forEach((g) => {
    g.events.forEach((e) => {
      setEventSystemEnabled(e.key, true)
      setEventEmailEnabled(e.key, true)
    })
  })
  if (globalEmailsDisabled.value) {
    handleGlobalToggle(false)
  }
}

function disableAll() {
  groups.value.forEach((g) => {
    g.events.forEach((e) => {
      setEventSystemEnabled(e.key, false)
      setEventEmailEnabled(e.key, false)
    })
  })
}

function confirmReset() {
  showResetConfirm.value = true
}

function handleReset() {
  showResetConfirm.value = false
  groups.value.forEach((g) => {
    g.events.forEach((e) => {
      setEventSystemEnabled(e.key, true)
      setEventEmailEnabled(e.key, true)
    })
  })
  if (globalEmailsDisabled.value) {
    handleGlobalToggle(false)
  }
  showNotification('Settings reset to defaults', 'success')
}

function scrollToGroup(key: string) {
  document.getElementById(key)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<style scoped>
.settings-page {
  gap: 1.4rem;
}

.settings-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.settings-hero-copy {
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

.settings-hero h1 {
  margin: 0;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.settings-hero .section-subtitle {
  margin: 0.45rem 0 0;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.settings-hero-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

.save-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--success);
}

.save-indicator.saving {
  color: var(--muted-foreground);
}

.save-indicator.error {
  color: var(--destructive);
}

.save-icon {
  width: 16px;
  height: 16px;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.settings-rule {
  height: 1px;
  background: var(--border);
}

.settings-state {
  padding: 2rem 0;
}

.error-text {
  margin: 0 0 1rem;
  color: var(--destructive);
}

.settings-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 1.5rem;
  align-items: start;
}

.settings-sidebar {
  align-self: stretch;
}

.sidebar-sticky {
  position: sticky;
  top: calc(var(--nav-offset, 76px) + 1rem);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-height: calc(100vh - var(--nav-offset, 76px) - 2rem);
  overflow-y: auto;
  overscroll-behavior: contain;
}

.search-wrap {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--muted-foreground);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding-left: 2.25rem;
}

.sidebar-card {
  flex-shrink: 0;
}

.sidebar-card-header {
  display: flex;
  align-items: center;
}

.anchor-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.anchor-chip {
  display: block;
  padding: 0.4rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--muted-foreground);
  text-decoration: none;
  transition:
    background-color 0.15s ease,
    color 0.15s ease;
}

.anchor-chip:hover {
  background: var(--subtle);
  color: var(--foreground);
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  min-width: 0;
}

.global-card {
  flex-shrink: 0;
}

.global-toggle-state {
  flex: 0 0 auto;
}

.global-header h2 {
  margin: 0.25rem 0 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 700;
}

.section-eyebrow {
  margin: 0;
  font-size: var(--text-xs);
  line-height: var(--text-xs--line-height);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted-foreground);
}

.global-body {
  padding: 0.5rem 0;
}

.global-toggle-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
}

.global-toggle-info {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
}

.global-toggle-title {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--foreground);
}

.global-toggle-desc {
  font-size: var(--text-sm);
  color: var(--muted-foreground);
  line-height: 1.5;
}

.settings-group {
  scroll-margin-top: 1.5rem;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.group-header-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.group-header h3 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-weight: 700;
}

.group-count {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--muted-foreground);
}

.group-bulk {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-shrink: 0;
}

.bulk-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.bulk-label {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--muted-foreground);
  white-space: nowrap;
}

.group-table-header {
  display: grid;
  grid-template-columns: 1fr 100px 100px;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border);
  font-size: var(--text-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted-foreground);
}

.col-toggle {
  text-align: center;
}

.group-events {
  display: flex;
  flex-direction: column;
}

.event-row {
  display: grid;
  grid-template-columns: 1fr 100px 100px;
  gap: 1rem;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border);
  transition: background-color 0.15s ease;
}

.event-row:last-child {
  border-bottom: 0;
}

.event-row:hover {
  background: var(--subtle);
}

.event-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}

.event-title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--foreground);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-desc {
  font-size: var(--text-xs);
  color: var(--muted-foreground);
  line-height: 1.4;
}

.event-toggles {
  display: contents;
}

.toggle-cell {
  display: flex;
  justify-content: center;
  align-items: center;
}

.toggle-cell .visibility-switch:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

@media (max-width: 1024px) {
  .settings-layout {
    grid-template-columns: 1fr;
  }

  .sidebar-sticky {
    position: static;
  }

  .anchor-nav {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .anchor-chip {
    padding: 0.35rem 0.75rem;
    border: 1px solid var(--border);
    border-radius: 999px;
  }
}

@media (max-width: 760px) {
  .settings-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .settings-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .group-table-header {
    display: none;
  }

  .event-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
    padding: 1rem 0;
  }

  .event-toggles {
    display: flex;
    gap: 1.5rem;
    padding-top: 0.25rem;
  }

  .toggle-cell {
    justify-content: flex-start;
  }

  .toggle-cell::before {
    content: attr(data-label);
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--muted-foreground);
    margin-right: 0.35rem;
  }

  .group-bulk {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
