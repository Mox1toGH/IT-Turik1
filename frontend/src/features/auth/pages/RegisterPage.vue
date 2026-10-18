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
          <register-fields
            :form="form"
            :role-options="roleOptions"
            :is-restricted-role="isRestrictedRole"
          />

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

      <register-summary
        :username="form.fields.value.username"
        :email="form.fields.value.email"
        :full-name="form.fields.value.full_name"
        :city="form.fields.value.city"
        :role-label="roleLabel"
        :is-restricted-role="isRestrictedRole"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import GoogleAuthButton from '@/components/shared/GoogleAuthButton.vue'
import UiButton from '@/components/ui/UiButton'
import UiCard from '@/components/ui/UiCard'
import { useNotification } from '@/composables/useNotification'
import { useUserStore } from '@/stores/user'
import { useForm } from '@/composables/useForm'
import { RegisterSchema } from '@/schemas/auth.schema'
import { useRegisterUser, type GoogleAuthMutationResult } from '@/api/accounts/accounts'
import { useRouter } from 'vue-router'
import RegisterFields, { type RegisterFormValues } from '../components/RegisterFields.vue'
import RegisterSummary from '../components/RegisterSummary.vue'

const form = useForm<RegisterFormValues>(RegisterSchema, {
  username: '',
  email: '',
  password: '',
  role: 'team',
  activation_code: '',
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
const roleLabel = computed(
  () => roleOptions.find((option) => option.value === form.fields.value.role)?.label ?? 'Team',
)

watch(
  () => form.fields.value.role,
  (newRole) => {
    if (!restrictedRoles.includes(newRole)) {
      form.fields.value.activation_code = ''
    }
  },
)

function saveTokensAndRedirect(data: GoogleAuthMutationResult) {
  storage.setTokens(data)
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

.submit-btn {
  width: 100%;
}

@media (max-width: 980px) {
  .auth-layout {
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
