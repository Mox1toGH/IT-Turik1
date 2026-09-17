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

    <div class="auth-layout">
      <ui-card variant="panel" class="register-card">
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
        </form>

        <template #footer>
          <p class="auth-link">
            Already have an account?
            <router-link to="/login">Sign in</router-link>
          </p>
        </template>
      </ui-card>

      <aside class="summary-panel" aria-label="Registration summary">
        <ui-card variant="stat" class="summary-stat">
          <strong>{{ isRestrictedRole ? 'Code' : 'Open' }}</strong>
          <span>{{ isRestrictedRole ? 'Invite required' : 'No invite needed' }}</span>
        </ui-card>

        <ui-card class="summary-card">
          <p class="section-eyebrow">Draft summary</p>
          <h2>{{ form.fields.value.username || 'New account' }}</h2>
          <p class="summary-description text-muted">
            {{ form.fields.value.email || 'Email will appear here when added.' }}
          </p>

          <div class="summary-list">
            <div>
              <span>Role</span>
              <strong>{{ roleLabel }}</strong>
            </div>
            <div>
              <span>Name</span>
              <strong>{{ form.fields.value.full_name || 'Not set' }}</strong>
            </div>
            <div>
              <span>City</span>
              <strong>{{ form.fields.value.city || 'Not set' }}</strong>
            </div>
          </div>
        </ui-card>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import GoogleAuthButton from '@/components/shared/GoogleAuthButton.vue'
import UiPasswordField from '@/components/ui/UiPasswordField.vue'
import PhoneField from '@/components/shared/PhoneField.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import { useNotification } from '@/composables/useNotification'
import { useUserStore } from '@/stores/user'
import { useForm } from '@/composables/useForm'
import { RegisterSchema } from '@/schemas/auth.schema'
import type { RoleB96Enum } from '@/api/.ts.schemas'
import { useRegisterUser, type GoogleAuthMutationResult } from '@/api/accounts/accounts'
import { useRouter } from 'vue-router'

interface Form {
  username: string
  full_name: string
  email: string
  password: string
  role: RoleB96Enum
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
const router = useRouter()

const { mutate: register, isPending: isLoading, isSuccess } = useRegisterUser()

const restrictedRoles = ['jury', 'organizer', 'admin']
const roleOptions = [
  { value: 'team', label: 'Team Member' },
  { value: 'organizer', label: 'Organizer' },
  { value: 'jury', label: 'Jury' },
  { value: 'admin', label: 'Admin' },
]
const isRestrictedRole = computed(() => restrictedRoles.includes(form.fields.value.role))
const roleLabel = computed(
  () => roleOptions.find((option) => option.value === form.fields.value.role)?.label ?? 'Team',
)

const saveTokensAndRedirect = (data: GoogleAuthMutationResult) => {
  storage.setTokens(data)
  router.push('/')
}

const handleRegister = () => {
  if (!form.validate()) return

  register(
    { data: form.fields.value },
    {
      onError: (error) => {
        for (const [field, errors] of Object.entries(error.details || {})) {
          form.setError(field as keyof Form, errors?.[0] ?? 'Invalid value')
        }

        showNotification(error.message, 'error')
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
.auth-page {
  gap: 1.4rem;
  padding: 1.6rem 0 2rem;
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

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--accent-strong);
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

.summary-stat strong {
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  line-height: var(--text-2xl--line-height);
  font-weight: 800;
}

.summary-stat span {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
  white-space: nowrap;
}

.auth-rule {
  height: 1px;
  margin: 0.7rem 0 0.9rem;
  background: var(--line-soft);
}

.auth-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.38fr);
  gap: 1rem;
  align-items: start;
}

.register-card {
  min-width: 0;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.profile-fields {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  margin-top: 0.2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line-soft);
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

.summary-panel {
  position: sticky;
  top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

.summary-stat {
  justify-content: flex-start;
}

.summary-card.card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-radius: 18px;
  border-color: var(--line-soft);
}

.summary-card h2 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-xl);
  line-height: var(--text-xl--line-height);
  font-weight: 800;
}

.summary-description {
  display: -webkit-box;
  min-height: 3.2rem;
  margin: 0;
  overflow: hidden;
  line-clamp: 3;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.summary-list {
  display: grid;
  gap: 0.65rem;
  padding-top: 0.15rem;
}

.summary-list div {
  display: grid;
  grid-template-columns: minmax(0, 0.8fr) minmax(0, 1fr);
  gap: 0.75rem;
  padding: 0.8rem;
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  background: color-mix(in srgb, var(--card) 92%, var(--foreground) 8%);
}

.summary-list span {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
}

.summary-list strong {
  overflow: hidden;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

@media (max-width: 980px) {
  .auth-layout {
    grid-template-columns: 1fr;
  }

  .summary-panel {
    position: static;
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

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
