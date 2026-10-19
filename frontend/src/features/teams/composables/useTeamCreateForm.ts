import { computed, type ComputedRef, type Ref } from 'vue'
import { useRouter } from 'vue-router'
import { useNotification } from '@/composables/useNotification'
import { useForm } from '@/composables/useForm'
import { CreateTeamSchema } from '@/schemas/teams.schema'
import { useCreateTeam, type CreateTeamMutationBody } from '@/api/teams/teams'
import { useGetUserProfile, useListUsers } from '@/api/accounts/accounts'

import type { TeamUserListResponse } from '@/api/backendAPINinja.schemas'

export type TeamCreateFormFields = CreateTeamMutationBody

export interface UseTeamCreateFormReturn {
  form: ReturnType<typeof useForm<TeamCreateFormFields>>
  isCreatingTeam: Ref<boolean>
  isLoadingUsers: Ref<boolean>
  isLoadingError: unknown
  createCandidateUsers: ComputedRef<TeamUserListResponse[] | undefined>
  selectedMembersCount: ComputedRef<number>
  contactSummary: ComputedRef<string>
  handleFormSubmit: () => void
}

export function useTeamCreateForm(): UseTeamCreateFormReturn {
  const router = useRouter()
  const { showNotification } = useNotification()

  const form = useForm<TeamCreateFormFields>(CreateTeamSchema, {
    name: '',
    email: '',
    organization: '',
    contact_telegram: '',
    contact_discord: '',
    is_public: false,
    member_ids: [],
  })

  const resetForm = (): void => {
    form.reset()
  }

  const { data: user } = useGetUserProfile()

  const { data: users, isLoading: isLoadingUsers, isLoadingError } = useListUsers()

  const createCandidateUsers = computed(() => {
    return users.value?.items.filter((u) => {
      if (u.id === user.value?.id) return false
      return [u.username, u.email, u.full_name || ''].join(' ').toLowerCase()
    })
  })

  const selectedMembersCount = computed(() => form.fields.value.member_ids?.length ?? 0)
  const contactSummary = computed(() => {
    if (form.fields.value.contact_telegram && form.fields.value.contact_discord)
      return '2 channels'
    if (form.fields.value.contact_telegram || form.fields.value.contact_discord)
      return '1 channel'
    return 'Not set'
  })

  const { mutate: createTeam, isPending: isCreatingTeam } = useCreateTeam()

  const handleFormSubmit = (): void => {
    if (!form.validate()) return

    createTeam(
      { data: form.fields.value },
      {
        onSuccess: (data) => {
          showNotification('Team created successfully.', 'success')
          resetForm()

          router.push(`/teams/${data.id}`)
        },
        onError: (error) => {
          for (const [field, message] of Object.entries(error?.details || {})) {
            form.setError(field, message)
          }

          showNotification(error.message, 'error')
        },
      },
    )
  }

  return {
    form,
    isCreatingTeam,
    isLoadingUsers,
    isLoadingError,
    createCandidateUsers,
    selectedMembersCount,
    contactSummary,
    handleFormSubmit,
  }
}
