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

      <ui-card v-else-if="events?.length === 0">
        <div style="display: flex; height: 300px; justify-content: center; align-items: center">
          <p>No events founded for this tournament</p>
        </div>
      </ui-card>

      <div v-else class="events-list">
        <ui-card v-for="event in events" :key="event.title" class="event-card">
          <div class="event-content">
            <div class="event-left-side">
              <div class="event-icon">
                <FinishIcon width="25px" height="25px" />
              </div>

              <p>{{ event.title }}</p>
            </div>

            <div class="event-right-side">
              <p class="text-muted">
                {{ formatDate(event.start_datetime, { showHours: true }) }}
              </p>
            </div>
          </div>

          <div class="event-actions" v-if="user?.role === 'admin'">
            <ui-button size="sm" @click="isEditOpen = true">Edit</ui-button>
            <EditEventModal
              v-model="isEditOpen"
              :event-id="event.id"
              :tournament-id="props.tournamentId"
              :title="event.title"
              :start-date="event.created_at!"
            />

            <ui-button size="sm" variant="danger" @click="isDeleteOpen = true">Delete</ui-button>
            <DeleteEventModal
              v-model="isDeleteOpen"
              :event-id="event.id"
              :tournament-id="props.tournamentId"
              :title="event.title"
            />
          </div>
        </ui-card>
      </div>
    </ui-skeleton-loader>
  </section>
</template>

<script setup lang="ts">
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import FinishIcon from '@/icons/FinishIcon.vue'
import { formatDate } from '@/lib/date'
import EditEventModal from './modals/EditEventModal.vue'
import { useProfile } from '@/api/queries/accounts'
import DeleteEventModal from './modals/DeleteEventModal.vue'
import AddEventModal from './modals/AddEventModal.vue'
import { useTournamentEvents } from '@/api/queries/tournaments'
import { ref } from 'vue'
import UiButton from '@/components/ui/UiButton.vue'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()
const { data: user } = useProfile()

const isAddOpen = ref(false)
const isEditOpen = ref(false)
const isDeleteOpen = ref(false)

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

.event-left-side,
.event-right-side {
  display: flex;
  align-items: center;
  gap: 1rem;
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
