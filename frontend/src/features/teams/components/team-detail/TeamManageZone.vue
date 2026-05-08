<template>
  <ui-card v-if="isCaptain" class="manage-zone">
    <div>
      <div class="manage-row">
        <div>
          <h3>Edit team</h3>
          <p class="text-muted">Update team profile and manage members in edit workspace.</p>
        </div>
        <ui-button asLink variant="secondary" size="sm" :to="`/teams/${team?.id}/edit`"
          >Edit team</ui-button
        >
      </div>

      <div>
        <div class="danger-zone-header">
          <danger-icon />
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
import type { GetTeamInfoResponse } from '@/api/services/teams/types'
import DeleteTeamModal from './modals/DeleteTeamModal.vue'
import TeamVisibilityModal from './modals/TeamVisibilityModal.vue'
import UiCard from '@/components/ui/UiCard.vue'
import DangerIcon from '@/icons/DangerIcon.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import { useRouter } from 'vue-router'

interface Props {
  team?: GetTeamInfoResponse
  loading: boolean
  isCaptain: boolean
}

const props = defineProps<Props>()
const router = useRouter()

const emit = defineEmits<{
  (e: 'updateTeam', newTeamValue: GetTeamInfoResponse): void
}>()
</script>

<style scoped>
.danger-zone-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.8rem;
  margin: 0.2rem 0 0;
  background: color-mix(in srgb, var(--destructive) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--destructive) 20%, transparent);
  border-radius: 8px;
  color: color-mix(in srgb, var(--destructive) 80%, transparent);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.danger-zone-icon {
  width: 0.95rem;
  height: 0.95rem;
  flex-shrink: 0;
}

.danger-zone-box {
  margin-top: 0.6rem;
  border: 1px solid color-mix(in srgb, var(--destructive) 20%, transparent);
  border-radius: 10px;
  overflow: hidden;
  background: color-mix(in srgb, var(--destructive) 10%, transparent);
}

.danger-zone-box {
  padding: 1rem;
  border: 1px solid color-mix(in srgb, var(--destructive) 20%, transparent);
}

.manage-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.9rem;
}

.danger-zone-row:not(:last-child) {
  border-bottom: 1px solid color-mix(in srgb, var(--destructive) 20%, transparent);
}

.manage-row:not(:last-child) {
  margin-bottom: 1rem;
  padding-bottom: 1rem;
}

.manage-row h3 {
  font-size: 1rem;
}

.manage-row p {
  margin-top: 0.3rem;
}

.danger-zone-row h3 {
  color: color-mix(in srgb, var(--destructive) 80%, transparent);
}
</style>
