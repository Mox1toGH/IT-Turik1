<template>
  <div class="actions" v-if="user?.role === 'admin'">
    <ui-button @click="openCreate">Create round</ui-button>
    <CreateRoundModal v-model="isCreateOpen" :tournament-id="props.tournamentId" />
  </div>

  <section>
    <ui-query-block :query="roundsQuery" title="rounds">
      <ui-query-field>
        <template #skeleton>
          <rounds-list-skeleton />
        </template>

        <template #default>
          <ui-empty-card
            v-if="rounds.length === 0"
            title="No rounds added yet"
            message="Rounds created for this tournament show up here."
          />
          <div v-else class="rounds-list">
            <ui-card v-for="round in rounds" :key="round.id" class="round-card">
              <template #header>
                <div class="round-header">
                  <h4>{{ truncateText(round.name ?? '-', 40) }}</h4>

                  <div class="header-right">
                    <ui-badge :variant="badgeVariant(getEffectiveRoundStatus(round))">{{
                      badgeStatus(getEffectiveRoundStatus(round))
                    }}</ui-badge>
                    <round-actions-popover
                      v-if="user?.role === 'admin'"
                      :roundId="round.id"
                      :tournamentId="props.tournamentId"
                      :status="round.status"
                    />
                  </div>
                </div>
              </template>

              <div class="round-dates">
                <p class="text-muted">
                  Start: {{ formatDate(round.start_date, { showHours: true }) }}
                </p>
                <p class="text-muted">End: {{ formatDate(round.end_date, { showHours: true }) }}</p>
              </div>

              <div class="round-actions">
                <ui-button size="sm" variant="secondary" @click="openDetails(round)">
                  View details
                </ui-button>

                <ui-button
                  v-if="user?.role === 'admin' && round.status === 'draft'"
                  size="sm"
                  variant="secondary"
                  @click="openEdit(round)"
                >
                  Edit
                </ui-button>

                <template
                  v-if="getEffectiveRoundStatus(round) === 'active' && user?.role === 'team'"
                >
                  <ui-query-block :query="submissionsQuery">
                    <ui-query-field>
                      <template #skeleton>
                        <ui-skeleton variant="rect" width="110px" height="36px" />
                      </template>
                      <ui-button
                        v-if="submittedRoundIds.has(round.id)"
                        size="sm"
                        variant="secondary"
                        @click="openSubmissionsSection"
                      >
                        View submission
                      </ui-button>
                      <ui-button v-else size="sm" @click="openSubmissionForm(round.id)">
                        Submit
                      </ui-button>
                    </ui-query-field>
                  </ui-query-block>
                </template>
              </div>
            </ui-card>
          </div>
        </template>
      </ui-query-field>
    </ui-query-block>

    <submit-modal
      v-if="selectedSubmitRoundId !== null"
      :roundId="selectedSubmitRoundId"
      :tournamentId="props.tournamentId"
      v-model="isSubmitOpen"
    />

    <round-details-modal
      v-if="selectedRound"
      v-model="isDetailsOpen"
      :title="selectedRound?.name ?? ''"
      :description="selectedRound?.description ?? {}"
      :mustHave="selectedRound?.must_have_requirements ?? {}"
      :technicalRequirements="selectedRound?.tech_requirements ?? {}"
    />

    <edit-round-modal v-if="selectedRound" v-model="isEditOpen" :round="selectedRound" />
  </section>
</template>

<script setup lang="ts">
import UiBadge from '@/components/ui/UiBadge'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiEmptyCard from '@/components/ui/UiEmptyCard'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import RoundsListSkeleton from './tournament-rounds/RoundsListSkeleton.vue'
import { truncateText } from '@/lib/utils'
import { formatDate } from '@/lib/date'
import { computed, ref, watch } from 'vue'
import type { Variants } from '@/components/ui/UiBadge'
import RoundDetailsModal from '../modals/RoundDetailsModal.vue'
import SubmitModal from '../modals/SubmitModal.vue'
import RoundActionsPopover from './tournament-rounds/RoundActionsPopover.vue'
import CreateRoundModal from './tournament-rounds/modals/CreateRoundModal.vue'
import EditRoundModal from '../modals/EditRoundModal.vue'
import { useRoute, useRouter } from 'vue-router'
import { useGetUserProfile } from '@/api/accounts/accounts'
import { useListMyTeamSubmissions, useListRounds } from '@/api/tournaments/tournaments'
import type { RoundResponse } from '@/api/backendAPINinja.schemas.ts'

interface Props {
  tournamentId: number
}

const props = defineProps<Props>()
const profileQuery = useGetUserProfile()
const { data: user } = profileQuery
const router = useRouter()
const route = useRoute()

const roundsQuery = useListRounds(props.tournamentId)
const submissionsQuery = useListMyTeamSubmissions(props.tournamentId)
const { data: submissions } = submissionsQuery

const rounds = computed(() => roundsQuery.data.value?.items ?? [])
const submittedRoundIds = computed(
  () => new Set((submissions.value?.items ?? []).map((submission) => submission.round_details.id)),
)

const isDetailsOpen = ref(false)
const isCreateOpen = ref(false)
const isEditOpen = ref(false)
const isSubmitOpen = ref(false)
const selectedRound = ref<RoundResponse | null>(null)
const selectedSubmitRoundId = ref<number | null>(null)

function getEffectiveRoundStatus(round: RoundResponse): RoundResponse['status'] {
  if (round.status !== 'active') return round.status
  const endTimestamp = new Date(round.end_date).getTime()
  if (!Number.isFinite(endTimestamp)) return round.status
  return Date.now() >= endTimestamp ? 'submission_closed' : 'active'
}

function openDetails(round: RoundResponse) {
  selectedRound.value = round
  isDetailsOpen.value = true
}

function openCreate() {
  isCreateOpen.value = true
}

function openEdit(round: RoundResponse) {
  selectedRound.value = round
  isEditOpen.value = true
}

function openSubmissionForm(roundId: number) {
  selectedSubmitRoundId.value = roundId
  isSubmitOpen.value = true
}

function openSubmissionsSection() {
  void router.replace({
    query: {
      ...route.query,
      section: 'submissions',
    },
  })
}

watch(isSubmitOpen, (isOpen) => {
  if (!isOpen) {
    selectedSubmitRoundId.value = null
  }
})

function badgeVariant(status: RoundResponse['status']): Variants {
  if (status === 'active') return 'primary'
  if (status === 'evaluated') return 'green'
  if (status === 'submission_closed') return 'red'
  return 'gray'
}

function badgeStatus(status: RoundResponse['status']) {
  if (status === 'draft') return 'Draft'
  if (status === 'active') return 'Active'
  if (status === 'evaluated') return 'Evaluated'
  if (status === 'submission_closed') return 'Closed'
}
</script>

<style scoped>
.actions {
  display: flex;
  justify-content: end;
  align-items: center;
  margin-bottom: 1rem;
}

.rounds-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
}

.round-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.round-actions {
  display: flex;
  justify-content: end;
  align-items: center;
  gap: 8px;
  margin-top: 1rem;
}

.round-dates {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.round-card {
  min-width: 0;
}

@media (max-width: 1024px) {
  .rounds-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .rounds-list {
    grid-template-columns: 1fr;
  }
}

</style>
