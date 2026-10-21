<template>
  <form class="password-form" @submit.prevent="handleSubmit">
    <div class="form-panel">
      <div class="panel-header">
        <span class="step-marker">01</span>
        <div>
          <h3>Change password</h3>
          <p class="text-muted">Confirm your current password, then set a new one.</p>
        </div>
      </div>

      <label class="field">
        <span class="label">Current password</span>
        <ui-password-field
          v-model="form.fields.value.current_password"
          :is-invalid="!!form.errors.value.current_password"
          autocomplete="current-password"
          required
          @blur="form.validateField('current_password')"
        />
        <small v-if="form.errors.value.current_password" class="error">
          {{ form.errors.value.current_password }}
        </small>
      </label>

      <label class="field">
        <span class="label">New password</span>
        <ui-password-field
          v-model="form.fields.value.new_password"
          :is-invalid="!!form.errors.value.new_password"
          autocomplete="new-password"
          required
          @blur="form.validateField('new_password')"
        />
        <small v-if="form.errors.value.new_password" class="error">
          {{ form.errors.value.new_password }}
        </small>
      </label>

      <label class="field">
        <span class="label">Confirm new password</span>
        <ui-password-field
          v-model="form.fields.value.confirm_password"
          :is-invalid="!!form.errors.value.confirm_password"
          autocomplete="new-password"
          required
          @blur="form.validateField('confirm_password')"
        />
        <small v-if="form.errors.value.confirm_password" class="error">
          {{ form.errors.value.confirm_password }}
        </small>
      </label>

      <div class="reset-hint">
        <span>Forgot your current password?</span>
        <ui-button type="button" size="sm" :disabled="isSendingReset" @click="sendResetEmail">
          <LoaderCircle class="animate-spin" v-if="isSendingReset" />
          Send reset email
        </ui-button>
      </div>
    </div>

    <div class="footer-actions">
      <ui-button v-if="showBack" type="button" variant="secondary" @click="emit('back')">
        Back to profile
      </ui-button>
      <ui-button type="submit" :disabled="isChangingPassword">
        <LoaderCircle class="animate-spin" v-if="isChangingPassword" />
        Update password
      </ui-button>
    </div>
  </form>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton'
import UiPasswordField from '@/components/ui/UiPasswordField'
import { LoaderCircle } from 'lucide-vue-next'
import { useForm } from '@/composables/useForm'
import { useNotification } from '@/composables/useNotification'
import { ChangePasswordSchema } from '@/schemas/profile.schema'
import { useChangePassword, useRequestPasswordReset } from '@/api/accounts/accounts'

interface PasswordForm {
  current_password: string
  new_password: string
  confirm_password: string
}

const props = withDefaults(
  defineProps<{
    userEmail?: string
    showBack?: boolean
  }>(),
  { showBack: true },
)

const emit = defineEmits<{
  back: []
  saved: []
}>()

const { showNotification } = useNotification()

const form = useForm<PasswordForm>(ChangePasswordSchema, {
  current_password: '',
  new_password: '',
  confirm_password: '',
})

const { mutate: changePassword, isPending: isChangingPassword } = useChangePassword()
const { mutate: requestReset, isPending: isSendingReset } = useRequestPasswordReset()

const handleSubmit = () => {
  if (!form.validate()) return

  changePassword(
    { data: form.fields.value },
    {
      onSuccess: () => {
        showNotification('Password updated successfully.', 'success')
        form.reset()
        emit('saved')
      },
      onError: (error) => {
        for (const [field, message] of Object.entries(error?.details || {})) {
          form.setError(field, message)
        }
      },
    },
  )
}

const sendResetEmail = () => {
  if (!props.userEmail) {
    showNotification('Account email is missing.', 'error')
    return
  }

  requestReset(
    { data: { email: props.userEmail } },
    {
      onSuccess: () => {
        showNotification('Password reset email sent to your account email.', 'success')
      },
      onError: (error) => {
        showNotification(error?.message || 'Failed to send reset email.', 'error')
      },
    },
  )
}

defineExpose({ reset: form.reset, isSubmitting: isChangingPassword })
</script>

<style scoped>
.password-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-panel {
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

.reset-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.8rem;
  border-radius: var(--radius-sm);
  background: var(--subtle);
}

.reset-hint span {
  color: var(--muted-foreground);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 600;
}

.reset-hint :deep(button) {
  flex-shrink: 0;
  width: auto;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

@media (max-width: 480px) {
  .reset-hint {
    justify-content: center;
    text-align: center;
  }
}

@media (max-width: 760px) {
  .footer-actions {
    flex-direction: column;
  }

  .footer-actions .btn {
    width: 100%;
  }
}
</style>
