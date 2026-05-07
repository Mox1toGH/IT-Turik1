<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div>
          <p class="section-eyebrow">Admin</p>
          <h1 class="section-title">Activation Codes</h1>
          <p class="section-subtitle">
            Generate and monitor one-time registration codes for restricted roles.
          </p>
        </div>
      </template>

      <div>
        <div class="counts">
          <ui-card v-for="role in restrictedRoles" :key="role" class="statistic-card">
            <template #header>
              <span class="card-label">{{ role }}</span>
            </template>

            <ui-skeleton-loader :loading="isLoading">
              <template #skeleton>
                <ui-skeleton variant="rect" width="100%" />
              </template>

              <strong class="text-muted">{{ activeCounts?.[role] || 0 }}/10 active</strong>
            </ui-skeleton-loader>
          </ui-card>
        </div>

        <form class="generator" @submit.prevent="handleGenerate">
          <div class="form-item">
            <label class="form-label"> Role </label>
            <ui-select
              v-model="generateForm.role"
              :miltiple="true"
              :options="[
                { value: 'jury', label: 'Jury' },
                { value: 'organizer', label: 'Organizer' },
                { value: 'admin', label: 'Admin' },
              ]"
              required
            >
              <option value="jury">Jury</option>
              <option value="organizer">Organizer</option>
              <option value="admin">Admin</option>
            </ui-select>
            <small v-if="errors?.role" class="text-error">{{ errors.role[0] }}</small>
          </div>

          <div class="form-item">
            <label class="form-label"> Quantity </label>
            <ui-input v-model="generateForm.quantity" type="number" min="1" max="10" required />
            <small v-if="errors?.quantity" class="text-error">{{ errors.quantity[0] }}</small>
          </div>

          <ui-button type="submit" class="generate-btn" :disabled="submitting">
            {{ submitting ? 'Generating...' : 'Generate Codes' }}
          </ui-button>
        </form>

        <div class="filters">
          <div class="form-item">
            <label class="form-label"> Filter by role </label>

            <ui-select
              v-model="selectedRoleFilter"
              :options="[
                { value: 'all', label: 'All restricted roles' },
                { value: 'jury', label: 'Jury' },
                { value: 'organizer', label: 'Organizer' },
                { value: 'admin', label: 'Admin' },
              ]"
            />
          </div>
        </div>
      </div>

      <template #footer>
        <ui-skeleton-loader :loading="isLoading">
          <template #skeleton>
            <div class="codes-list">
              <ui-card v-for="i in 3" :key="i" class="code-card">
                <template #header>
                  <div class="code-head">
                    <ui-skeleton variant="rect" width="100%" />
                    <ui-skeleton variant="rect" width="100px" />
                  </div>
                </template>

                <div style="display: flex; flex-direction: column; gap: 4px">
                  <ui-skeleton v-for="i in 6" :key="i" variant="rect" width="100%" />
                </div>
              </ui-card>
            </div>
          </template>

          <div class="codes-list">
            <div
              v-if="isLoadingError"
              style="display: flex; height: 120px; justify-content: center; align-items: center"
            >
              <p>Error while fetching role codes (code: {{ error?.code }})</p>
            </div>

            <template v-else>
              <ui-card v-for="code in codes" :key="code.id" class="code-card">
                <template #header>
                  <div class="code-head">
                    <strong class="mono">{{ code.code }}</strong>
                    <ui-badge :variant="code.is_used ? 'gray' : 'green'">
                      {{ code.is_used ? 'Used' : 'Active' }}
                    </ui-badge>
                  </div>
                </template>

                <div class="code-card-content">
                  <p><strong>Role:</strong> {{ code.role }}</p>
                  <p><strong>Created:</strong> {{ formatDateTime(code.created_at) }}</p>
                  <p><strong>Created by:</strong> {{ code.created_by_username || '-' }}</p>
                  <template v-if="code.is_used">
                    <p><strong>Used by:</strong> {{ code.used_by }}</p>
                    <p>
                      <strong>Used at:</strong>
                      {{ code.used_at ? formatDateTime(code.used_at) : '-' }}
                    </p>
                  </template>
                </div>
              </ui-card>

              <ui-card class="empty-card">
                <p v-if="!codes.length" class="text-muted empty-error">
                  No codes found for current filter.
                </p>
              </ui-card>
            </template>
          </div>
        </ui-skeleton-loader>
      </template>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { RoleCodesUserRole } from '@/api/services/accounts/types'
import { parseApiError } from '@/api/errors'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { useGenerateCodes, useRoleCodes } from '@/api/queries/accounts'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import { useNotification } from '@/composables/useNotification'
import UiBadge from '@/components/ui/UiBadge.vue'

interface Errors {
  role: string[]
  quantity: string[]
}

const forbidden = ref(false)
const statusMessage = ref('')
const statusType = ref('success')
const errors = ref<Errors | null>(null)
const restrictedRoles = ['jury', 'organizer', 'admin'] as const
const selectedRoleFilter = ref<RoleCodesUserRole | 'all'>('all')
const generateForm = ref({
  role: 'jury',
  quantity: '1',
})

const { showNotification } = useNotification()

const {
  data,
  isLoading,
  isLoadingError,
  error: getRoleCodesError,
} = useRoleCodes({
  filter: computed(() => ({ role: selectedRoleFilter.value })),
})
const error = computed(() => parseApiError(getRoleCodesError.value))

const codes = computed(() => data.value?.codes || [])
const activeCounts = computed(() => data.value?.active_counts)

watch(getRoleCodesError, (err) => {
  if (err) {
    if (err.response?.status === 403) {
      forbidden.value = true
      return
    }

    statusType.value = 'error'
    statusMessage.value = err.response
      ? 'Unable to load activation codes.'
      : 'Server connection error.'
  }
})

const { mutate: generateCodes, isPending: submitting } = useGenerateCodes()

const handleGenerate = () => {
  generateCodes(
    {
      body: {
        ...generateForm.value,
        quantity: parseInt(generateForm.value.quantity, 10),
      },
    },
    {
      onSuccess: (data) => {
        showNotification(`Generated ${data.created?.length || 0} code(s) successfully.`, 'success')
      },
      onError: (err) => {
        if (err.response?.status === 403) {
          forbidden.value = true
          return
        }

        if (err.response) {
          showNotification(err.response.data.message as string, 'error')
        } else {
          showNotification('Unable to generate codes.', 'error')
        }
      },
    },
  )
}

const formatDateTime = (value: string | number | Date) => {
  if (!value) return '-'
  return new Date(value).toLocaleString()
}
</script>

<style scoped>
.counts {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
  margin: 0.8rem 0 1rem;
}

.generator {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
  align-items: end;
  margin-bottom: 1rem;
}

.generate-btn {
  height: fit-content;
}

.statistic-card,
.code-card {
  background: var(--muted);
}

.code-card-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filters {
  width: min(320px, 100%);
  margin-bottom: 1rem;
}

.codes-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 0.75rem;
}

.code-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
  overflow-wrap: anywhere;
}

.empty-error {
  text-align: center;
}

@media (max-width: 900px) {
  .counts {
    grid-template-columns: 1fr;
  }

  .generator {
    grid-template-columns: 1fr;
  }
}
</style>
