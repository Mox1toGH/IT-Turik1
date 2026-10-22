<template>
  <section class="page-shell centered">
    <ui-card class="complete-card">
      <template #header>
        <div>
          <p class="section-eyebrow">Final Step</p>
          <h1 class="section-title">Complete your profile</h1>
          <p class="section-subtitle">
            Choose your role and review your account details before continuing.
          </p>
        </div>
      </template>

      <ui-query-block :query="userQuery">
        <form class="form-grid" @submit.prevent="handleSubmit">
          <div class="form-item">
            <label class="form-label"> Username </label>
            <ui-query-field>
              <template #skeleton
                ><ui-skeleton variant="rect" width="100%" height="40px"
              /></template>
              <ui-input
                v-model="form.fields.value.username"
                required
                :is-invalid="!!form.errors.value.username"
                @blur="form.validateField('username')"
              />
            </ui-query-field>
            <small v-if="form.errors.value.username" class="text-error">{{
              form.errors.value.username
            }}</small>
          </div>

          <div class="form-item">
            <label class="form-label"> Role </label>
            <ui-query-field>
              <template #skeleton
                ><ui-skeleton variant="rect" width="100%" height="40px"
              /></template>
              <ui-select
                :options="[
                  { value: 'team', label: 'Team Member' },
                  { value: 'organizer', label: 'Organizer' },
                  { value: 'jury', label: 'Jury' },
                  { value: 'admin', label: 'Admin' },
                ]"
                v-model="form.fields.value.role"
                required
              />
            </ui-query-field>
            <small v-if="form.errors.value.role" class="text-error">{{
              form.errors.value.role
            }}</small>
          </div>

          <div style="display: flex; flex-direction: column; gap: 1rem">
            <div class="form-item" v-if="isRestrictedRole">
              <label class="form-label full-width"> Redeem code </label>
              <ui-input
                v-model="form.fields.value.redeem_code"
                placeholder="Enter one-time activation code"
                required
                :is-invalid="!!form.errors.value.redeem_code"
                @blur="form.validateField('redeem_code')"
              />
              <small v-if="form.errors.value.redeem_code" class="text-error">{{
                form.errors.value.redeem_code
              }}</small>
            </div>

            <div class="form-item">
              <label class="form-label full-width"> Password </label>
              <ui-password-field
                v-model="form.fields.value.password"
                autocomplete="new-password"
                placeholder="Create a strong password"
                :is-invalid="!!form.errors.value.password"
                required
                @blur="form.validateField('password')"
              />
              <small v-if="form.errors.value.password" class="text-error">{{
                form.errors.value.password
              }}</small>
            </div>
          </div>

          <div class="form-item">
            <label class="form-label full-width"> Full name </label>
            <ui-query-field>
              <template #skeleton
                ><ui-skeleton variant="rect" width="100%" height="40px"
              /></template>
              <ui-input
                v-model="form.fields.value.full_name"
                :is-invalid="!!form.errors.value.full_name"
                @blur="form.validateField('full_name')"
              />
            </ui-query-field>
            <small v-if="form.errors.value.full_name" class="text-error">{{
              form.errors.value.full_name
            }}</small>
          </div>

          <div class="form-item">
            <label class="form-label"> Phone </label>
            <ui-query-field>
              <template #skeleton
                ><ui-skeleton variant="rect" width="100%" height="40px"
              /></template>
              <PhoneField
                v-model="form.fields.value.phone"
                placeholder="Enter phone number"
                :is-invalid="!!form.errors.value.phone"
              />
            </ui-query-field>
            <small v-if="form.errors.value.phone" class="text-error">{{
              form.errors.value.phone
            }}</small>
          </div>

          <div class="form-item">
            <label class="form-label"> City </label>
            <ui-query-field>
              <template #skeleton
                ><ui-skeleton variant="rect" width="100%" height="40px"
              /></template>
              <ui-input
                v-model="form.fields.value.city"
                :is-invalid="!!form.errors.value.city"
                @blur="form.validateField('city')"
              />
            </ui-query-field>
            <small v-if="form.errors.value.city" class="text-error">{{
              form.errors.value.city
            }}</small>
          </div>

          <ui-button class="submit-btn" :disabled="isUpdatingProfile" type="submit">
            Complete registration
            <LoaderCircle class="animate-spin" v-if="isUpdatingProfile" />
          </ui-button>
        </form>
      </ui-query-block>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRouter } from 'vue-router'

import PhoneField from '@/components/shared/PhoneField.vue'
import UiPasswordField from '@/components/ui/UiPasswordField'
import UiButton from '@/components/ui/UiButton'
import UiInput from '@/components/ui/UiInput'
import UiSelect from '@/components/ui/UiSelect'
import UiCard from '@/components/ui/UiCard'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import { LoaderCircle } from 'lucide-vue-next'
import { useForm } from '@/composables/useForm'
import { CompleteProfileSchema } from '@/schemas/profile.schema'
import { useGetUserProfile, useUpdateUserProfile } from '@/api/accounts/accounts'
import { useNotification } from '@/composables/useNotification'
import type { UserRole } from '@/shared/types/user'

interface Form {
  username: string
  role: UserRole
  redeem_code: string
  password: string
  full_name: string
  phone: string
  city: string
}

const router = useRouter()
const userQuery = useGetUserProfile()
const { data: user } = userQuery

const form = useForm<Form>(CompleteProfileSchema, {
  username: user.value?.username ?? '',
  role: (user.value?.role as UserRole) ?? 'team',
  redeem_code: '',
  password: '',
  full_name: user.value?.full_name ?? '',
  phone: user.value?.phone ?? '',
  city: user.value?.city ?? '',
})

watch(
  user,
  (profile) => {
    if (!profile) return
    form.hydrate({
      username: profile.username ?? '',
      role: (profile.role as UserRole) ?? 'team',
      redeem_code: '',
      password: '',
      full_name: profile.full_name ?? '',
      phone: profile.phone ?? '',
      city: profile.city ?? '',
    })
  },
  { immediate: true },
)

const { showNotification } = useNotification()

const restrictedRoles = ['jury', 'organizer', 'admin']
const isRestrictedRole = computed(() => restrictedRoles.includes(form.fields.value.role))

watch(
  () => form.fields.value.role,
  (newRole) => {
    if (!restrictedRoles.includes(newRole)) {
      form.fields.value.redeem_code = ''
    }
  },
)

const { mutate: updateProfile, isPending: isUpdatingProfile } = useUpdateUserProfile()

const handleSubmit = async () => {
  if (!form.validate()) return

  updateProfile(
    { data: form.fields.value },
    {
      onSuccess: () => {
        localStorage.removeItem('needs_onboarding')
        router.push('/')
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
</script>

<style scoped>
.complete-card {
  width: min(100%, 720px);
  padding: 2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.full-width {
  grid-column: 1 / -1;
}

.submit-btn {
  margin-top: 0.5rem;
  grid-column: 1 / -1;
}

.field-help {
  color: var(--text-muted);
}

@media (max-width: 760px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .submit-btn {
    grid-column: auto;
  }
}
</style>
