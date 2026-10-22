<template>
  <section class="page-shell">
    <section class="page-section role-codes-section">
      <header class="page-header">
        <div class="head">
          <div>
            <p class="section-eyebrow">Admin</p>
            <h1 class="section-title">Activation Codes</h1>
            <p class="section-subtitle">
              Generate and monitor one-time registration codes for restricted roles.
            </p>
          </div>
          <ui-button as-link to="/admin" variant="secondary">Back to Admin hub</ui-button>
        </div>
      </header>

      <ui-query-block :query="roleCodesQuery">
        <div>
          <ui-query-field>
            <template #skeleton>
              <div class="counts">
                <ui-card v-for="role in restrictedRoles" :key="role" class="statistic-card">
                  <template #header>
                    <span class="card-label">{{ role }}</span>
                  </template>

                  <ui-skeleton variant="rect" width="100%" />
                </ui-card>
              </div>
            </template>

            <template #default>
              <div class="counts">
                <ui-card v-for="role in restrictedRoles" :key="role" class="statistic-card">
                  <template #header>
                    <span class="card-label">{{ role }}</span>
                  </template>

                  <strong class="text-muted">{{ activeCounts?.[role] || 0 }}/10 active</strong>
                </ui-card>
              </div>
            </template>
          </ui-query-field>

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
              <ui-number-input v-model="generateForm.quantity" min="1" max="10" required />
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

        <section class="codes-section">
          <ui-query-field>
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

            <template #default>
              <div v-if="isEmpty" class="codes-list">
                <ui-card class="empty-card">
                  <p class="text-muted empty-error">No codes found for current filter.</p>
                </ui-card>
              </div>

              <div v-else class="codes-list">
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
                      <p><strong>Used by:</strong> {{ code.used_by_username }}</p>
                      <p>
                        <strong>Used at:</strong>
                        {{ code.used_at ? formatDateTime(code.used_at) : '-' }}
                      </p>
                    </template>
                  </div>
                </ui-card>
              </div>
            </template>
          </ui-query-field>
        </section>
      </ui-query-block>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import UiButton from '@/components/ui/UiButton'
import UiNumberInput from '@/components/ui/UiNumberInput'
import UiSelect from '@/components/ui/UiSelect'
import UiCard from '@/components/ui/UiCard'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { useNotification } from '@/composables/useNotification'
import UiBadge from '@/components/ui/UiBadge'
import {
  useGenerateRoleActivationCodes,
  useListRoleActivationCodes,
  type GenerateRoleActivationCodesMutationBody,
} from '@/api/accounts/accounts'
import type { UserRole } from '@/shared/types/user'

interface Errors {
  role: UserRole[]
  quantity: string[]
}

const forbidden = ref(false)
const errors = ref<Errors | null>(null)
const restrictedRoles = ['jury', 'organizer', 'admin'] as const
const selectedRoleFilter = ref<string | 'all'>('all') // role
const generateForm = ref({
  role: 'jury',
  quantity: '1',
})

const { showNotification } = useNotification()

const roleCodesQuery = useListRoleActivationCodes(
  computed(() => (selectedRoleFilter.value !== 'all' ? { role: selectedRoleFilter.value } : {})),
)

const { data, error: getRoleCodesError } = roleCodesQuery

const codes = computed(() => data.value?.codes || [])
const activeCounts = computed(() => data.value?.active_counts)
const isEmpty = computed(() => codes.value.length === 0)

watch(getRoleCodesError, (err) => {
  if (err) {
    if (err._axiosError?.status === 403) {
      forbidden.value = true
      return
    }
  }
})

const { mutate: generateCodes, isPending: submitting } = useGenerateRoleActivationCodes()

const handleGenerate = () => {
  generateCodes(
    {
      data: {
        ...generateForm.value,
        quantity: parseInt(generateForm.value.quantity, 10),
      } as GenerateRoleActivationCodesMutationBody,
    },
    {
      onSuccess: (data) => {
        showNotification(`Generated ${data.created?.length || 0} code(s) successfully.`, 'success')
      },
      onError: (error) => {
        if (error._axiosError?.status === 403) {
          forbidden.value = true
          return
        }

        showNotification(error.message, 'error')
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
.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

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
  height: 100%;
  background: var(--card);
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
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
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
  .head {
    flex-direction: column;
    align-items: flex-start;
  }

  .counts {
    grid-template-columns: 1fr;
  }

  .generator {
    grid-template-columns: 1fr;
  }
}
</style>
