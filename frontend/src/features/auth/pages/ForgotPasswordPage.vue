<template>
  <section class="page-shell centered">
    <ui-card class="forgot-card">
      <template #header>
        <div>
          <p class="section-eyebrow">Password Recovery</p>
          <h1 class="section-title">Forgot your password?</h1>
          <p class="section-subtitle">
            Enter your account email and we will send you a password reset link.
          </p>
        </div>
      </template>

      <form class="forgot-form" @submit.prevent="handleSubmit">
        <div class="form-item">
          <label class="form-label"> Email </label>
          <ui-input
            v-model="email"
            type="email"
            :is-invalid="!!error?.details.email"
            autocomplete="email"
            placeholder="name@mail.com"
            required
          />
          <small v-if="error?.details.email" class="text-error">{{ error.details.email[0] }}</small>
        </div>

        <ui-button :disabled="isLoading" type="submit">
          Send reset link
          <loading-icon v-if="isLoading" />
        </ui-button>
      </form>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { useForgotPassword } from '@/api/queries/accounts'
import { parseApiError } from '@/api/errors'
import { useNotification } from '@/composables/useNotification'
import LoadingIcon from '@/icons/LoadingIcon.vue'

const { showNotification } = useNotification()
const email = ref('')

const {
  mutate: forgotPassword,
  isPending: isLoading,
  error: forgotPasswordError,
} = useForgotPassword()
const error = computed(() => parseApiError(forgotPasswordError.value))

const handleSubmit = () => {
  forgotPassword(
    { body: { email: email.value } },
    {
      onSuccess: () => {
        showNotification('Password reset email sent successfully.', 'success')
      },
    },
  )
}
</script>

<style scoped>
.forgot-card {
  width: min(100%, 520px);
  padding: 2rem;
}

.forgot-form {
  display: grid;
  gap: 0.9rem;
}

@media (max-width: 640px) {
  .forgot-card {
    border-radius: 18px;
  }
}
</style>
