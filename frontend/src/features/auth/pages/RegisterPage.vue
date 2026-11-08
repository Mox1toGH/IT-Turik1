<template>
  <section class="auth-page page-shell">
    <header class="auth-hero">
      <div class="auth-hero-copy">
        <div class="breadcrumb-label">
          <span>Account</span>
          <span aria-hidden="true">/</span>
          <span>Register</span>
        </div>

        <h1>Create your account</h1>
        <p class="section-subtitle">
          Get access to tournaments, team tools, and profile management.
        </p>
      </div>
    </header>

    <div class="auth-rule" aria-hidden="true"></div>

    <div>
      <ui-card class="register-card">
        <template #header>
          <div class="panel-header">
            <span class="step-marker">01</span>
            <div>
              <p class="section-eyebrow">Join the platform</p>
              <h2>Account details</h2>
            </div>
          </div>
        </template>

        <div v-if="isSuccess" class="notice success">
          Registration completed. Check <strong>{{ form.fields.value.email }}</strong> to activate
          your account.
        </div>

        <form v-else @submit.prevent="handleRegister" class="register-form">
          <div class="register-fields">
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
                  :options="roleOptions"
                  class="select-control"
                />
              </label>
            </div>

            <label v-if="isRestrictedRole" class="form-item">
              <p class="form-label full-width">Activation code</p>
              <ui-input
                v-model="form.fields.value.activation_code"
                @blur="form.validateField('activation_code')"
                :is-invalid="!!form.errors.value.activation_code"
                placeholder="Enter one-time activation code"
                required
              />
              <small v-if="form.errors.value.activation_code" class="text-error">{{
                form.errors.value.activation_code
              }}</small>
            </label>

            <div class="profile-fields">
              <div class="panel-header profile-header">
                <span class="step-marker">02</span>
                <div>
                  <p class="section-eyebrow">Profile</p>
                  <h2>Optional info</h2>
                </div>
              </div>

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
                  <phone-field
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
          </div>

          <ui-button type="submit" class="submit-btn" :disabled="isLoading">
            {{ isLoading ? 'Creating account...' : 'Create account' }}
          </ui-button>

          <GoogleAuthButton divider-label="or sign up with" @success="saveTokensAndRedirect" />
        </form>

        <template #footer>
          <p class="auth-link">
            Already have an account?
            <router-link to="/login">Sign in</router-link>
          </p>
        </template>
      </ui-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import GoogleAuthButton from '@/components/shared/GoogleAuthButton.vue'
import PhoneField from '@/components/shared/PhoneField.vue'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import UiInput from '@/components/ui/UiInput'
import UiPasswordField from '@/components/ui/UiPasswordField'
import UiSelect from '@/components/ui/UiSelect'
import { useNotification } from '@/composables/useNotification'
import { useUserStore } from '@/stores/user'
import { useForm } from '@/composables/useForm'
import { RegisterSchema } from '@/schemas/auth.schema'
import { useRegisterUser, type GoogleAuthMutationResult } from '@/api/accounts/accounts'
import { useRouter } from 'vue-router'
import type { UserRole } from '@/api/backendAPINinja.schemas'

interface RegisterFormValues {
  username: string
  full_name: string
  email: string
  password: string
  role: UserRole
  activation_code?: string
  phone: string
  city: string
}

const form = useForm<RegisterFormValues>(RegisterSchema, {
  username: '',
  email: '',
  password: '',
  role: 'team',
  activation_code: undefined,
  full_name: '',
  phone: '',
  city: '',
})

const storage = useUserStore()
const router = useRouter()
const { showNotification } = useNotification()

const { mutate: register, isPending: isLoading, isSuccess } = useRegisterUser()

const restrictedRoles = ['jury', 'organizer', 'admin']
const roleOptions = [
  { value: 'team', label: 'Team Member' },
  { value: 'organizer', label: 'Organizer' },
  { value: 'jury', label: 'Jury' },
  { value: 'admin', label: 'Admin' },
]

const isRestrictedRole = computed(() => restrictedRoles.includes(form.fields.value.role))

watch(
  () => form.fields.value.role,
  (newRole) => {
    if (!restrictedRoles.includes(newRole)) {
      form.fields.value.activation_code = ''
    }
  },
)

function saveTokensAndRedirect(data: GoogleAuthMutationResult) {
  storage.setSession({ authenticated: true, onboarding_required: data.onboarding_required })
  router.push('/')
}

function handleRegister() {
  if (!form.validate()) return

  register(
    { data: form.fields.value },
    {
      onError: (error) => {
        for (const [field, message] of Object.entries(error.details || {})) {
          form.setError(field, message)
        }

        showNotification(error.message, 'error')
      },
    },
  )
}
</script>

<style scoped>
.auth-page {
  gap: 1.4rem;
}

.auth-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.auth-hero-copy {
  min-width: 0;
}

.auth-link {
  margin: 1rem 0 0;
  color: var(--muted-foreground);
  text-align: center;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

.auth-link a {
  color: var(--primary);
  font-weight: 700;
}

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.auth-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.auth-hero .section-subtitle {
  margin: 0.45rem 0 0;
  max-width: 780px;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.auth-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--border);
}

.register-card {
  min-width: 0;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.register-fields,
.profile-fields {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.profile-fields {
  margin-top: 0.2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

.profile-header {
  margin-bottom: 0.1rem;
}

.full-width {
  grid-column: 1 / -1;
}

.submit-btn {
  width: 100%;
}

@media (max-width: 760px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .auth-page {
    padding: 1rem 1rem 2rem;
  }

  .auth-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .auth-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .auth-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }
}
</style>
