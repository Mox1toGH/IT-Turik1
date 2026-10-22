<template>
  <ui-card v-if="isCaptain" class="manage-zone">
    <div class="manage-stack">
      <div class="manage-row">
        <div>
          <h3>Edit team</h3>
          <p class="text-muted">Update team profile and manage members in edit workspace.</p>
        </div>
        <ui-button asLink variant="secondary" :to="`/teams/${team?.id}/edit`">Edit team</ui-button>
      </div>

      <div>
        <div class="danger-zone-header">
          <TriangleAlert :size="20" />
          <span>Danger Zone</span>
        </div>

        <div class="danger-zone-box">
          <div class="manage-row danger-zone-row" v-if="!team?.is_in_active_tournament">
            <div>
              <h3>Change visibility</h3>
              <p class="text-muted">
                <ui-badge :variant="team?.is_public ? 'green' : 'red'">{{
                  team?.is_public ? 'Public' : 'Private'
                }}</ui-badge>
                -

                {{
                  team?.is_public
                    ? 'Anyone can find and request to join this team.'
                    : 'Only invited members can see this team.'
                }}
              </p>
            </div>

            <TeamVisibilityModal
              :team="props.team"
              @changed-team-visibility="(newTeamValue) => emit('updateTeam', newTeamValue)"
            />
          </div>

          <div class="manage-row danger-zone-row">
            <div>
              <h3>Delete team</h3>
              <p class="text-muted">
                This action permanently deletes the team and cannot be undone.
              </p>
            </div>

            <DeleteTeamModal
              :disabled="props.loading"
              :team="props.team"
              @deleted="router.push('/teams')"
            />
          </div>
        </div>
      </div>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import DeleteTeamModal from './modals/DeleteTeamModal.vue'
import TeamVisibilityModal from './modals/TeamVisibilityModal.vue'
import UiCard from '@/components/ui/UiCard'
import { TriangleAlert } from 'lucide-vue-next'
import UiButton from '@/components/ui/UiButton'
import UiBadge from '@/components/ui/UiBadge'
import { useRouter } from 'vue-router'
import type { Team } from '@/features/teams/types'

interface Props {
  team?: Team
  loading: boolean
  isCaptain: boolean
}

const props = defineProps<Props>()
const router = useRouter()

const emit = defineEmits<{
  (e: 'updateTeam', newTeamValue: Team): void
}>()
</script>

<style scoped>
.manage-stack {
  display: grid;
  gap: 1.5rem;
}

.danger-zone-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.8rem;
  margin: 0.2rem 0 0;
  background: var(--destructive-soft);
  border: 1px solid var(--destructive-ring);
  border-radius: var(--radius-sm);
  color: var(--destructive);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.danger-zone-box {
  margin-top: 0.6rem;
  padding: 0 1rem;
  border: 1px solid var(--destructive-ring);
  border-radius: var(--radius-sm);
  background: var(--destructive-soft);
}

.manage-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.9rem;
  padding: 1rem 0;
}

.danger-zone-row + .danger-zone-row {
  border-top: 1px solid var(--destructive-ring);
}

.manage-row h3 {
  margin: 0;
  font-size: 1rem;
}

.manage-row p {
  margin: 0.3rem 0 0;
}

.danger-zone-row h3 {
  color: var(--destructive);
}

@media (max-width: 640px) {
  .manage-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
