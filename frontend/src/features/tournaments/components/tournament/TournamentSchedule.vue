<template>
  <div class="top-actions" v-if="user?.role === 'admin'">
    <ui-button @click="isAddOpen = true">Add event</ui-button>
    <AddEventModal v-model="isAddOpen" :tournament-id="props.tournamentId" />
  </div>

  <section class="page-shell">
    <ui-skeleton-loader :loading="isEventsLoading">
      <template #skeleton>
        <div class="events-list">
          <ui-card v-for="i in 5" :key="i">
            <div class="event-content">
              <div class="event-left-side">
                <ui-skeleton variant="rounded" width="50px" height="50px" />
                <ui-skeleton variant="rect" width="100px" />
              </div>
              <div class="event-dates">
                <ui-skeleton variant="rect" width="150px" />
              </div>
            </div>
          </ui-card>
        </div>
      </template>

      <ui-card v-if="isEventsError">
        <div style="display: flex; height: 300px; justify-content: center; align-items: center">
          <p>Error while fetching tournament schedule</p>
        </div>
      </ui-card>

      <ui-card
        v-else-if="events?.length === 0"
        class="empty-card"
        style="display: flex; align-items: center; justify-content: center; height: 300px"
      >
        <p class="empty-error">No events founded for this tournament</p>
      </ui-card>

      <div v-else class="events-list">
        <ui-card v-for="event in events" :key="event.title" class="event-card">
          <div class="event-content">
            <div class="event-left-side">
              <div class="event-icon">
                <FinishIcon width="25px" height="25px" />
              </div>

              <div class="event-info">
                <p>{{ event.title }}</p>
                <LargeTextModal
                  title="Event description"
                  :text="event.description"
                  max-length="100"
                >
                  <template #trigger>
                    <p class="event-description">
                      {{ truncateText(event.description, 100) }}
                    </p>
                  </template>
                </LargeTextModal>
              </div>
            </div>

            <div class="event-right-side">
              <p class="text-muted">
                {{ formatDate(event.start_datetime, { showHours: true }) }}
              </p>
            </div>
          </div>

          <div class="event-actions" v-if="user?.role === 'admin'">
            <ui-button size="sm" @click="openEditModal(event)">Edit</ui-button>
            <ui-button size="sm" variant="danger" @click="openDeleteModal(event)">Delete</ui-button>
          </div>
        </ui-card>
      </div>
    </ui-skeleton-loader>

    <!-- Modals -->
    <EditEventModal
      v-if="selectedEvent && isEditOpen"
      v-model="isEditOpen"
      :event-id="selectedEvent.id"
      :tournament-id="props.tournamentId"
      :title="selectedEvent.title"
      :description="selectedEvent.description"
      :start-date="selectedEvent.start_datetime"
    />

    <DeleteEventModal
      v-if="selectedEvent && isDeleteOpen"
      v-model="isDeleteOpen"
      :event-id="selectedEvent.id"
      :tournament-id="props.tournamentId"
      :title="selectedEvent.title"
    />
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import FinishIcon from '@/icons/FinishIcon.vue'
import { formatDate } from '@/lib/date'
import type { TournamentEvent } from '@/api/dbTypes'
import EditEventModal from './modals/EditEventModal.vue'
import { useProfile } from '@/api/queries/accounts'
import DeleteEventModal from './modals/DeleteEventModal.vue'
import AddEventModal from './modals/AddEventModal.vue'
import { useTournamentEvents } from '@/api/queries/tournaments'
import { ref } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'
import LargeTextModal from '@/components/shared/LargeTextModal.vue'
import { truncateText } from '@/lib/utils'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()
const { data: user } = useProfile()

const isAddOpen = ref(false)
const isEditOpen = ref(false)
const isDeleteOpen = ref(false)

const selectedEvent = ref<TournamentEvent | null>(null)

const openEditModal = (event: TournamentEvent) => {
  selectedEvent.value = event
  isEditOpen.value = true
}

const openDeleteModal = (event: TournamentEvent) => {
  selectedEvent.value = event
  isDeleteOpen.value = true
}

const {
  data: events,
  isLoading: isEventsLoading,
  isError: isEventsError,
} = useTournamentEvents({ tournamentId: props.tournamentId })
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
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  padding-left: 20px;
  margin-left: 10px;
  border-left: 1px solid var(--border);
}

.event-icon {
  width: 50px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--primary);
  color: #fff;
  border-radius: 50%;
}

.event-info {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.event-description {
  word-break: break-word;
  max-width: 600px;
}

.event-left-side,
.event-right-side {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.top-actions {
  margin-bottom: 1rem;
}

.top-actions,
.event-actions {
  display: flex;
  gap: 0.6rem;
  justify-content: end;
}

.event-actions {
  padding-top: 14px;
  border-top: 1px solid var(--border);
}
</style>
