<template>
  <section class="auth-page">
    <ui-card class="auth-card">
      <template #header>
        <header class="auth-header">
          <h1>Sign in</h1>
          <p class="section-subtitle">Welcome back to TournamentOS.</p>
        </header>
      </template>

      <form @submit.prevent="handleLogin" class="auth-form">
        <label class="form-item">
          <p class="form-label">Username</p>
          <ui-input
            v-model="form.fields.value.username"
            autocomplete="username"
            :is-invalid="!!form.errors.value.username"
            placeholder="Username"
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
            placeholder="Password"
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

      <template #footer>
        <p class="auth-link">
          New here?
          <router-link to="/register">Create one</router-link>
        </p>
      </template>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import GoogleAuthButton from '@/components/shared/GoogleAuthButton.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiPasswordField from '@/components/ui/UiPasswordField.vue'
import { useUserStore } from '@/stores/user'
import { useLogin } from '@/api/accounts/accounts'
import { useForm } from '@/composables/useForm'
import { LoginSchema } from '@/schemas/auth.schema'
import type { LoginResponse } from '@/api/backendAPINinja.schemas'

const store = useUserStore()

const form = useForm(LoginSchema, { username: '', password: '' })
const router = useRouter()

const { mutate: login, isPending, error } = useLogin()

function saveAndRedirect(data: LoginResponse) {
  store.setTokens(data)
  router.push('/')
}

async function handleLogin() {
  if (!form.validate()) return

  login(
    { data: form.fields.value },
    {
      onSuccess: (data) => {
        saveAndRedirect(data)
      },
    },
  )
}
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - 160px);
  display: grid;
  place-items: center;
  padding: 2rem 1rem;
}

.auth-card {
  width: min(100%, 420px);
  gap: 1.1rem;
  padding: 1.5rem;
  border-color: var(--line-soft);
  border-radius: 16px;
}

.auth-header {
  display: grid;
  gap: 0.35rem;
  text-align: center;
}

.auth-header h1 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  line-height: var(--text-2xl--line-height);
  font-weight: 800;
}

.auth-header p {
  margin: 0;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

.auth-form {
  display: grid;
  gap: 0.9rem;
}

.feedback {
  margin: 0;
  text-align: center;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
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

.auth-link {
  margin: 0;
  text-align: center;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
}

@media (max-width: 520px) {
  .auth-page {
    align-items: start;
    padding-top: 1rem;
  }
}
</style>
