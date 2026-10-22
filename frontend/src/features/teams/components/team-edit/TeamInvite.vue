<template>
  <ui-card class="invite-card">
    <template #header>
      <div class="panel-header">
        <div>
          <h2>Invite someone</h2>
          <p class="text-muted">Add a teammate by invitation.</p>
        </div>
      </div>
    </template>

    <div class="invite-row">
      <div class="invite-select-wrap">
        <ui-query-block :query="usersQuery" title="users">
          <template #error><p class="text-muted">Could not load users.</p></template>
          <ui-query-field>
            <template #skeleton>
              <ui-skeleton variant="rect" height="40px" width="100%" />
            </template>
            <p v-if="userOptions.length === 0" class="text-muted">No users available to invite.</p>
            <ui-select-search
              v-else
              placeholder="Select user"
              v-model="addMemberSelection"
              :options="userOptions"
            />
          </ui-query-field>
        </ui-query-block>
      </div>

      <ui-button
        class="invite-btn"
        :disabled="addMemberLoading || isLoadingUsers || !addMemberSelection"
        @click="addMember"
      >
        <LoaderCircle class="animate-spin" v-if="addMemberLoading" />
        {{ addMemberLoading ? 'Sending...' : 'Send invitation' }}
      </ui-button>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { useNotification } from '@/composables/useNotification'
import { LoaderCircle } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useInviteMemberToTeam } from '@/api/teams/teams'
import { useListUsers } from '@/api/accounts/accounts'
import type { Team } from '@/features/teams/types'
import UiSelectSearch from '@/components/ui/UiSelectSearch/UiSelectSearch.vue'

interface Props {
  team: Team
}

const props = defineProps<Props>()
const { showNotification } = useNotification()

const usersQuery = useListUsers()
const { data: users, isLoading: isLoadingUsers } = usersQuery

const addMemberSelection = ref<number | null>(null)

const availableUsers = computed(() => {
  const currentIds = new Set(props.team?.members.map((member) => member.id))
  return users.value?.items.filter((user) => !currentIds.has(user.id))
})

const userOptions = computed(() => [
  ...(availableUsers.value?.map((user) => ({
    value: String(user.id),
    label: `${user.username} (${user.email})`,
  })) || []),
])

const { mutate: addMemberMutate, isPending: addMemberLoading } = useInviteMemberToTeam()

const addMember = () => {
  if (!props.team) return

  if (!addMemberSelection.value) {
    showNotification('Select a user to add.', 'error')
    return
  }

  addMemberMutate(
    { pk: props.team.id, data: { user_id: Number(addMemberSelection.value) } },
    {
      onSuccess: () => {
        addMemberSelection.value = null
        showNotification('Invitation sent.', 'success')
      },
      onError: (error) => {
        showNotification(error.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
.invite-card {
  gap: 1rem;
}

.invite-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.invite-select-wrap {
  flex: 1 1 240px;
  min-width: 0;
}

.invite-btn {
  width: max-content;
}
</style>
