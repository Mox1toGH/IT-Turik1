<template>
  <section class="page-shell centered">
    <section class="forgot-card">
      <div class="modal-title">
        <p class="section-eyebrow">Password Recovery</p>
        <h1>Forgot your password?</h1>
      </div>

      <ui-card variant="form" class="form-panel">
        <div class="panel-header">
          <span class="step-marker">01</span>
          <div>
            <h3>Reset your password</h3>
            <p class="text-muted">
              Enter your account email and we will send you a password reset link.
            </p>
          </div>
        </div>

        <form class="forgot-form" @submit.prevent="handleSubmit">
          <label class="field">
            <span class="label">Email</span>
            <ui-input
              v-model="email"
              type="email"
              :is-invalid="!!error?.details?.email"
              autocomplete="email"
              placeholder="name@mail.com"
              required
            />
            <small v-if="error?.details?.email" class="error">{{ error.details.email }}</small>
          </label>

          <div class="footer-actions">
            <ui-button :disabled="isLoading" type="submit">
              Send reset link
              <loading-icon v-if="isLoading" />
            </ui-button>
          </div>
        </form>
      </ui-card>
    </section>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import { useNotification } from '@/composables/useNotification'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useRequestPasswordReset } from '@/api/accounts/accounts'

const email = ref('')

const { showNotification } = useNotification()
const { mutate: forgotPassword, isPending: isLoading, error } = useRequestPasswordReset()

const handleSubmit = () => {
  forgotPassword(
    { data: { email: email.value } },
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
  display: grid;
  gap: 1rem;
}

.modal-title h1 {
  margin: 0.2rem 0 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  line-height: var(--text-2xl--line-height);
  font-weight: 800;
}

.form-panel.card {
  display: grid;
  gap: 14px;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
}

.panel-header h3 {
  margin: 0;
  color: var(--foreground);
  font-family: var(--font-display);
  font-size: var(--text-lg, 1.1rem);
  font-weight: 800;
}

.panel-header p {
  margin: 0.2rem 0 0;
}

.forgot-form {
  display: grid;
  gap: 0.9rem;
}

.field {
  display: grid;
  gap: 6px;
}

.label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--muted-foreground);
}

.error {
  color: var(--destructive);
  font-size: 0.8rem;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.footer-actions .btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

@media (max-width: 640px) {
  .forgot-card {
    border-radius: 18px;
  }
}
</style>
