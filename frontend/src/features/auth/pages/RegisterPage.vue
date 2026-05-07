<template>
  <section class="page-shell centered">
    <ui-card class="register-card">
      <template #header>
        <div>
          <p class="section-eyebrow">Join the Platform</p>
          <h1 class="section-title">Create your account</h1>
          <p class="section-subtitle">
            Get access to tournaments, team tools, and profile management.
          </p>
        </div>
      </template>

      <div v-if="isSuccess" class="notice success">
        Registration completed. Check <strong>{{ form.fields.value.email }}</strong> to activate
        your account.
      </div>

      <form v-else @submit.prevent="handleRegister" class="register-form">
        <div class="form-grid">
          <label class="form-item">
            <p class="form-label">Username</p>
            <ui-input
              v-model="form.fields.value.username"
              @blur="form.validateField('username')"
              placeholder="johndoe"
              required
              :is-invalid="!!form.errors.value.username"
            />
            <small v-if="form.errors.value.username" class="text-error">{{
              form.errors.value.username
            }}</small>
          </label>

          <label class="form-item">
            <p class="form-label">Email</p>
            <ui-input
              v-model="form.fields.value.email"
              @blur="form.validateField('email')"
              :is-invalid="!!form.errors.value.email"
              placeholder="name@mail.com"
              required
            />
            <small v-if="form.errors.value.email" class="text-error">{{
              form.errors.value.email
            }}</small>
          </label>

          <label class="form-item">
            <p class="form-label">Password</p>
            <ui-password-field
              v-model="form.fields.value.password"
              autocomplete="new-password"
              :is-invalid="!!form.errors.value.password"
              placeholder="********"
              required
              @blur="form.validateField('password')"
            />
            <small v-if="form.errors.value.password" class="text-error">{{
              form.errors.value.password
            }}</small>
          </label>

          <label class="form-item">
            <p class="form-label">Role</p>
            <ui-select
              v-model="form.fields.value.role"
              @blur="form.validateField('role')"
              :options="[
                { value: 'team', label: 'Team Member' },
                { value: 'organizer', label: 'Organizer' },
                { value: 'jury', label: 'Jury' },
                { value: 'admin', label: 'Admin' },
              ]"
              class="select-control"
            />
          </label>
        </div>

        <label class="form-item" v-if="isRestrictedRole">
          <p class="form-label full-width">Redeem code</p>
          <ui-input
            v-model="form.fields.value.redeem_code"
            @blur="form.validateField('redeem_code')"
            :is-invalid="!!form.errors.value.redeem_code"
            placeholder="Enter one-time activation code"
            required
          />
          <small v-if="form.errors.value.redeem_code" class="text-error">{{
            form.errors.value.redeem_code
          }}</small>
        </label>

        <div style="display: flex; flex-direction: column; gap: 0.9rem; margin-top: 1rem">
          <label class="form-item">
            <p class="form-label full-width">Full name</p>
            <ui-input
              v-model="form.fields.value.full_name"
              :is-invalid="!!form.errors.value.full_name"
              placeholder="John Doe"
              @blur="form.validateField('full_name')"
            />
            <small v-if="form.errors.value.full_name" class="text-error">{{
              form.errors.value.full_name
            }}</small>
          </label>

          <div class="form-grid">
            <label class="form-item">
              <p class="form-label">Phone</p>
              <PhoneField
                v-model="form.fields.value.phone"
                placeholder="Enter phone number"
                :is-invalid="!!form.errors.value.phone"
                @blur="form.validateField('phone')"
              />
              <small v-if="form.errors.value.phone" class="text-error">{{
                form.errors.value.phone
              }}</small>
            </label>

            <label class="form-item">
              <p class="form-label">City</p>
              <ui-input
                v-model="form.fields.value.city"
                @blur="form.validateField('city')"
                :is-invalid="!!form.errors.value.city"
                placeholder="Kyiv"
              />
              <small v-if="form.errors.value.city" class="text-error">{{
                form.errors.value.city
              }}</small>
            </label>
          </div>
        </div>

        <ui-button type="submit" class="submit-btn" :disabled="isLoading">
          {{ isLoading ? 'Creating account...' : 'Create account' }}
        </ui-button>

        <GoogleAuthButton divider-label="or sign up with" @success="saveTokensAndRedirect" />

        <p class="auth-link">
          Already have an account?
          <router-link to="/login">Sign in</router-link>
        </p>
      </form>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import GoogleAuthButton from '@/components/shared/GoogleAuthButton.vue'
import UiPasswordField from '@/components/ui/UiPasswordField.vue'
import PhoneField from '@/components/shared/PhoneField.vue'
import type { RegisterResponse } from '@/api/services/accounts/types'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { useRegister } from '@/api/queries/accounts'
import type { UserRole } from '@/api/dbTypes'
import { useNotification } from '@/composables/useNotification'
import { useUserStore } from '@/stores/user'
import { parseApiError } from '@/api/errors'
import { useForm } from '@/composables/useForm'
import { RegisterSchema } from '@/schemas/auth.schema'

const router = useRouter()

interface Form {
  username: string
  full_name: string
  email: string
  password: string
  role: UserRole
  redeem_code: string
  phone: string
  city: string
}

const form = useForm<Form>(RegisterSchema, {
  username: '',
  email: '',
  password: '',
  role: 'team',
  redeem_code: '',
  full_name: '',
  phone: '',
  city: '',
})
const { showNotification } = useNotification()
const storage = useUserStore()

const { mutate: register, isPending: isLoading, isSuccess } = useRegister()

const restrictedRoles = ['jury', 'organizer', 'admin']
const isRestrictedRole = computed(() => restrictedRoles.includes(form.fields.value.role))

const saveTokensAndRedirect = (data: RegisterResponse) => {
  storage.setTokens(data)
  router.push('/')
}

const handleRegister = () => {
  if (!form.validate()) return

  register(
    { body: form.fields.value },
    {
      onError: (err) => {
        const parsedError = parseApiError(err)
        for (const [field, errors] of Object.entries(parsedError?.details || {})) {
          form.setError(field as keyof Form, errors?.[0] ?? 'Invalid value')
        }

        showNotification(parsedError?.message, 'error')
      },
    },
  )
}

watch(
  () => form.fields.value.role,
  (newRole) => {
    if (!restrictedRoles.includes(newRole)) {
      form.fields.value.redeem_code = ''
    }
  },
)
</script>

<style scoped>
.register-card {
  width: min(100%, 720px);
  padding: 2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
  margin-bottom: 0.9rem;
}

.full-width {
  grid-column: 1 / -1;
}

.submit-btn {
  width: 100%;
  margin-top: 1rem;
}

@media (max-width: 760px) {
  .register-card {
    border-radius: 18px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
