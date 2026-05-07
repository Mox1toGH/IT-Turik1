<template>
  <ui-button v-bind="$attrs" variant="secondary" @click="isOpen = true">Change Password</ui-button>

  <ui-modal v-model="isOpen" @close="resetPasswordState">
    <template #title>
      <h2>Change password</h2>
    </template>

    <form class="password-form" @submit.prevent="handlePasswordChange">
      <label class="form-item">
        <p class="form-label">Current password</p>
        <ui-password-field
          v-model="form.fields.value.current_password"
          :is-invalid="!!form.errors.value.current_password"
          autocomplete="current-password"
          required
          @blur="form.validateField('current_password')"
        />
        <small v-if="form.errors.value.current_password" class="text-error">{{
          form.errors.value.current_password
        }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">New password</p>
        <ui-password-field
          v-model="form.fields.value.new_password"
          :is-invalid="!!form.errors.value.new_password"
          autocomplete="new-password"
          required
          @blur="form.validateField('new_password')"
        />
        <small v-if="form.errors.value.new_password" class="text-error">{{
          form.errors.value.new_password
        }}</small>
      </label>

      <label class="form-item">
        <p class="form-label">Confirm new password</p>
        <ui-password-field
          v-model="form.fields.value.confirm_password"
          :is-invalid="!!form.errors.value.confirm_password"
          autocomplete="new-password"
          required
          @blur="form.validateField('confirm_password')"
        />
        <small v-if="form.errors.value.confirm_password" class="text-error">{{
          form.errors.value.confirm_password
        }}</small>
      </label>

      <p class="auth-link" style="text-align: end">
        <router-link to="/forgot-password">Forgot password?</router-link>
      </p>

      <ui-button type="submit" :disabled="isChangingPassword">
        <LoadingIcon v-if="isChangingPassword" />
        Update password
      </ui-button>
    </form>
  </ui-modal>
</template>

<script setup lang="ts">
import { parseApiError } from '@/api/errors'
import UiButton from '@/components/ui/UiButton.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiPasswordField from '@/components/ui/UiPasswordField.vue'
import { useForm } from '@/composables/useForm'
import { useNotification } from '@/composables/useNotification'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useChangePassword } from '@/api/queries/accounts'
import { ChangePasswordSchema } from '@/schemas/profile.schema'
import { ref } from 'vue'

interface PasswordForm {
  current_password: string
  new_password: string
  confirm_password: string
}

const isOpen = ref(false)
const form = useForm<PasswordForm>(ChangePasswordSchema, {
  current_password: '',
  new_password: '',
  confirm_password: '',
})

const resetPasswordState = () => {
  form.reset()
}

const { showNotification } = useNotification()
const { mutate: changePassword, isPending: isChangingPassword } = useChangePassword()

const handlePasswordChange = () => {
  if (!form.validate()) return

  changePassword(
    { body: form.fields.value },
    {
      onSuccess: () => {
        showNotification('Password updated successfully.', 'success')
      },
      onError(error) {
        const parsedError = parseApiError(error)
        for (const [field, errors] of Object.entries(parsedError?.details || {})) {
          form.setError(field as keyof PasswordForm, errors?.[0] ?? 'Invalid value')
        }
      },
    },
  )
}
</script>

<style scoped>
.password-form {
  display: grid;
  gap: 0.75rem;
}
</style>
