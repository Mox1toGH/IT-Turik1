<template>
  <section class="page-shell centered">
    <section class="reset-card">
      <div class="modal-title">
        <p class="section-eyebrow">Password Recovery</p>
        <h1>Reset password</h1>
      </div>

      <ui-card variant="form" class="form-panel">
        <div class="panel-header">
          <span class="step-marker">01</span>
          <div>
            <h3>Set a new password</h3>
            <p class="text-muted">Choose a strong password to secure your account.</p>
          </div>
        </div>

        <p v-if="isLoading" class="text-muted">Checking your reset link...</p>
        <p v-else-if="error" class="notice error">{{ error.message }}</p>

        <div v-else-if="isSuccess" class="notice success reset-success">
          Password has been reset successfully.
          <div class="footer-actions">
            <ui-button as-link to="/login">Back to Login</ui-button>
          </div>
        </div>

        <form v-else class="reset-form" @submit.prevent="handleReset">
          <label class="field">
            <span class="label">New password</span>
            <ui-password-field
              v-model="form.new_password"
              :isInvalid="!!resetError?.details.new_password"
              autocomplete="new-password"
              placeholder="Create a strong password"
              required
            />
            <small v-if="resetError?.details.new_password" class="error">{{
              resetError.details.new_password[0]
            }}</small>
            <small v-else class="text-muted">
              Use at least 8 characters, including upper/lowercase letters, a number, and a special
              character.
            </small>
          </label>

          <label class="field">
            <span class="label">Confirm new password</span>
            <ui-password-field
              v-model="form.confirm_password"
              autocomplete="new-password"
              :isInvalid="!!resetError?.details.confirm_password"
              placeholder="Repeat your new password"
              required
            />
            <small v-if="resetError?.details.confirm_password" class="error">{{
              resetError.details.confirm_password[0]
            }}</small>
          </label>

          <div class="footer-actions">
            <ui-button :disabled="isResetingPassword" type="submit">
              <loading-icon v-if="isResetingPassword" />
              Set new password
            </ui-button>
          </div>
        </form>
      </ui-card>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import UiCard from '@/components/ui/UiCard.vue'
import UiPasswordField from '@/components/ui/UiPasswordField.vue'
import UiButton from '@/components/ui/UiButton.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useConfirmPasswordReset, useValidatePasswordResetLink } from '@/api/accounts/accounts'

const route = useRoute()
const form = ref({
  new_password: '',
  confirm_password: '',
})

const uid = computed(() => String(route.params.uid))
const token = computed(() => String(route.params.token))

const { isLoading, error } = useValidatePasswordResetLink(uid.value, token.value)
const {
  mutate: resetPassword,
  isPending: isResetingPassword,
  isSuccess,
  error: resetError,
} = useConfirmPasswordReset()

const handleReset = () => {
  resetPassword({
    uidb64: uid.value,
    token: token.value,
    data: form.value,
  })
}
</script>

<style scoped>
.reset-card {
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

.reset-form {
  display: grid;
  gap: 0.9rem;
}

.reset-success {
  display: grid;
  gap: 0.8rem;
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
  .reset-card {
    border-radius: 18px;
  }
}
</style>
