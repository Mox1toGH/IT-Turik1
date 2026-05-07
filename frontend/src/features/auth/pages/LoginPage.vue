<template>
  <section class="page-shell centered">
    <ui-card class="auth-card">
      <template #header>
        <div>
          <p class="section-eyebrow">Account Access</p>
          <h1 class="section-title">Sign in to TournamentOS</h1>
          <p class="section-subtitle">
            Track your team, profile, and upcoming tournaments in one place.
          </p>
        </div>
      </template>

      <div>
        <form @submit.prevent="handleLogin" class="auth-form">
          <label class="form-item">
            <p class="form-label">Username</p>
            <ui-input
              v-model="form.fields.value.username"
              autocomplete="username"
              :is-invalid="!!form.errors.value.username"
              required
              @blur="form.validateField('username')"
            />
            <small v-if="form.errors.value.username" class="text-error">{{
              form.errors.value.username
            }}</small>
          </label>

          <label class="form-item">
            <p class="form-label">Password</p>
            <ui-password-field
              v-model="form.fields.value.password"
              autocomplete="current-password"
              :is-invalid="!!form.errors.value.password"
              @blur="form.validateField('password')"
            />
            <small v-if="form.errors.value.password" class="text-error">{{
              form.errors.value.password
            }}</small>
          </label>

          <p class="forgot-link">
            <router-link to="/forgot-password">Forgot password?</router-link>
          </p>

          <ui-button type="submit" :disabled="isPending">
            {{ isPending ? 'Signing in...' : 'Sign in' }}
          </ui-button>
        </form>

        <p v-if="error" class="text-error feedback">
          {{ error.message }}
        </p>

        <GoogleAuthButton divider-label="or continue with" @success="saveAndRedirect" />
      </div>

      <template #footer>
        <p class="auth-link">
          No account yet?
          <router-link to="/register">Create one</router-link>
        </p>
      </template>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import GoogleAuthButton from '@/components/shared/GoogleAuthButton.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiPasswordField from '@/components/ui/UiPasswordField.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { useUserStore } from '@/stores/user'
import { useLogin } from '@/api/queries/accounts'
import { useQueryClient } from '@tanstack/vue-query'
import { accountKeys } from '@/api/queries/keys'
import type { LoginResponse } from '@/api/services/accounts/types'
import { parseApiError } from '@/api/errors'
import { useForm } from '@/composables/useForm'
import { LoginSchema } from '@/schemas/auth.schema'

const queryClient = useQueryClient()
const store = useUserStore()

const form = useForm(LoginSchema, { username: '', password: '' })
const router = useRouter()

const saveAndRedirect = (data: LoginResponse) => {
  store.setTokens(data)
  router.push('/')
}

const { mutate: login, isPending, error: loginError } = useLogin()
const error = computed(() => parseApiError(loginError.value))

const handleLogin = async () => {
  if (!form.validate()) return

  login(
    { body: form.fields.value },
    {
      onSuccess: (data) => {
        saveAndRedirect(data)
        queryClient.invalidateQueries({ queryKey: accountKeys.profile() })
      },
    },
  )
}
// We do this to reset AppNavbar state
// Like if we get 401 error and redirected to login
// We need to refetch profile to show Login and Register buttons
onMounted(() => queryClient.resetQueries({ queryKey: accountKeys.profile() }))
</script>

<style scoped>
.auth-card {
  width: min(100%, 520px);
  padding: 2rem;
}

.auth-form {
  display: grid;
  gap: 0.9rem;
}

.feedback {
  margin: 0.6rem 0 0;
}

.forgot-link {
  margin: -0.2rem 0 0;
  text-align: right;
  font-size: 0.9rem;
}

.forgot-link a {
  color: var(--brand-700);
  font-weight: 600;
}

@media (max-width: 640px) {
  .auth-card {
    border-radius: 18px;
  }
}
</style>
