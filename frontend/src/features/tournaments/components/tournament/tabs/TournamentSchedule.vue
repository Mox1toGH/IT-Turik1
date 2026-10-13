<template>
  <div class="top-actions" v-if="user?.role === 'admin' && props.tournamentStatus !== 'finished'">
    <ui-button @click="isAddOpen = true">Add event</ui-button>
    <AddEventModal v-model="isAddOpen" :tournament-id="props.tournamentId" />
  </div>

  <section class="page-shell">
    <div v-if="status === 'loading'" class="events-list">
      <ui-card v-for="i in 5" :key="`event-skeleton-${i}`" class="event-card" status="loading">
        <template #skeleton>
          <div class="event-content">
            <div class="event-left-side">
              <ui-skeleton variant="rounded" width="50px" height="50px" />
              <div class="event-info">
                <ui-skeleton variant="rect" width="140px" />
                <ui-skeleton variant="rect" width="220px" />
              </div>
            </div>
            <div class="event-right-side">
              <ui-skeleton variant="rect" width="150px" />
            </div>
          </div>
        </template>
      </ui-card>
    </div>

    <ui-card
      v-else-if="status !== 'data'"
      :query="eventsQuery"
      class="events-state"
      empty-text="No events scheduled yet"
    >
      <template #empty-action>
        <p class="text-sm text-muted">Events added to this tournament appear here.</p>
      </template>
    </ui-card>

    <div v-else class="events-list">
      <ui-card v-for="event in events" :key="event.id" class="event-card">
        <div class="event-content">
          <div class="event-left-side">
            <div class="event-icon">
              <FinishIcon width="25px" height="25px" />
            </div>

            <div class="event-info">
              <p class="event-title break-anywhere" :title="event.title">
                {{ truncateText(event.title, 30) }}
              </p>
              <ui-expandable-text :text="event.description ?? '-'" :lines="2" />
            </div>
          </div>

          <div class="event-right-side">
            <p class="text-muted">
              {{ formatDate(event.start_datetime, { showHours: true }) }}
            </p>
          </div>
        </div>

        <div class="event-actions" v-if="user?.role === 'admin'">
          <ui-button size="sm" @click="openEdit(event.id)">Edit</ui-button>
          <EditEventModal
            v-if="editTargetId === event.id"
            v-model="isEditOpen"
            :event-id="event.id"
            :tournament-id="props.tournamentId"
            :title="event.title"
            :description="event.description ?? '-'"
            :start-date="event.start_datetime"
            :event-type="event.type"
            :link="event.link ?? ''"
          />

          <ui-button size="sm" variant="danger" @click="openDelete(event.id)">Delete</ui-button>
          <DeleteEventModal
            v-if="deleteTargetId === event.id"
            v-model="isDeleteOpen"
            :event-id="event.id"
            :tournament-id="props.tournamentId"
            :title="event.title"
          />
        </div>
      </ui-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard'
import UiExpandableText from '@/components/ui/UiExpandableText'
import UiSkeleton from '@/components/ui/UiSkeleton'
import FinishIcon from '@/icons/FinishIcon.vue'
import { formatDate } from '@/lib/date'
import EditEventModal from '../modals/EditEventModal.vue'
import DeleteEventModal from '../modals/DeleteEventModal.vue'
import AddEventModal from '../modals/AddEventModal.vue'
import { computed, ref, watch } from 'vue'
import UiButton from '@/components/ui/UiButton'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useCardState } from '@/composables/useCardState'
import { useListEvents } from '@/api/tournaments/tournaments'
import type { TournamentStatus } from '@/api/backendAPINinja.schemas.ts'
import { truncateText } from '@/lib/utils.ts'

interface Props {
  tournamentId: number
  tournamentStatus: TournamentStatus
}

const props = defineProps<Props>()
const { data: user } = useGetUserProfile()

const isAddOpen = ref(false)
const isEditOpen = ref(false)
const isDeleteOpen = ref(false)
const editTargetId = ref<number | null>(null)
const deleteTargetId = ref<number | null>(null)

const openEdit = (id: number) => {
  editTargetId.value = id
  isEditOpen.value = true
}
const openDelete = (id: number) => {
  deleteTargetId.value = id
  isDeleteOpen.value = true
}

watch(isEditOpen, (val) => {
  if (!val) editTargetId.value = null
})
watch(isDeleteOpen, (val) => {
  if (!val) deleteTargetId.value = null
})

const eventsQuery = useListEvents({ tournament: props.tournamentId })
const { status } = useCardState(eventsQuery)
const events = computed(() => eventsQuery.data.value ?? [])
</script>

<style scoped>
.event-card {
  position: relative;
}

.event-card::before {
  content: '';
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  left: -30px;
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background: var(--primary);
}

.event-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  padding-left: 20px;
  margin-left: 10px;
  border-left: 1px solid var(--border);
}

/* The state card only carries the placeholder panel: it draws no frame of its own. */
.events-state {
  padding: 0;
  border: none;
  background: transparent;
}

.events-state :deep(.card-empty),
.events-state :deep(.card-state-error) {
  flex: 1 1 auto;
  min-height: 220px;
  justify-content: center;
  padding: 2rem 1rem;
}

.event-icon {
  width: 50px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 0 0 auto;
  background: var(--primary);
  color: var(--primary-foreground);
  border-radius: 50%;
}

.event-info {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 0;
}

.event-title {
  margin: 0;
  font-weight: 700;
}

.event-left-side,
.event-right-side {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.event-right-side p {
  margin: 0;
}

.top-actions,
.event-actions {
  display: flex;
  gap: 0.6rem;
  justify-content: end;
  margin-bottom: 1rem;
}

.event-actions {
  margin-bottom: 0;
  margin-top: 14px;
  padding-top: 7px;
  border-top: 1px solid var(--border);
}
</style>
