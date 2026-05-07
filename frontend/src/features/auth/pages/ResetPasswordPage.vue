<template>
  <section class="page-shell centered">
    <ui-card class="reset-card">
      <template #header>
        <p class="section-eyebrow">Password Recovery</p>
        <h1 class="section-title">Reset password</h1>
      </template>

      <div>
        <p v-if="isLoading" class="text-muted">Checking your reset link...</p>
        <p v-else-if="validationError" class="notice error">{{ validationError.message }}</p>

        <div v-else-if="isSuccess" class="notice success reset-success">
          Password has been reset successfully.
          <ui-button asLink to="/login">Back to Login</ui-button>
        </div>

        <form v-else class="reset-form" @submit.prevent="handleReset">
          <div class="form-item">
            <label class="form-label"> New password </label>
            <ui-password-field
              v-model="form.new_password"
              :isInvalid="!!resetingError?.details.new_password"
              autocomplete="new-password"
              placeholder="Create a strong password"
              required
            />
            <small v-if="resetingError?.details.new_password" class="text-error">{{
              resetingError.details.new_password[0]
            }}</small>
            <small v-else class="text-muted">
              Use at least 8 characters, including upper/lowercase letters, a number, and a special
              character.
            </small>
          </div>

          <div class="form-item">
            <label class="form-label"> Confirm new password </label>
            <ui-password-field
              v-model="form.confirm_password"
              autocomplete="new-password"
              :isInvalid="!!resetingError?.details.confirm_password"
              placeholder="Repeat your new password"
              required
            />
            <small v-if="resetingError?.details.confirm_password" class="text-error">{{
              resetingError.details.confirm_password[0]
            }}</small>
          </div>

          <ui-button :disabled="isResetingPassword" type="submit">
            <loading-icon v-if="isResetingPassword" />
            Set new password
          </ui-button>
        </form>
      </div>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import UiPasswordField from '@/components/ui/UiPasswordField.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import { useResetPassword, useValidateResetLink } from '@/api/queries/accounts'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { parseApiError } from '@/api/errors'

const route = useRoute()
const form = ref({
  new_password: '',
  confirm_password: '',
})

const uid = computed(() => String(route.params.uid))
const token = computed(() => String(route.params.token))

const { isLoading, error } = useValidateResetLink({ uid: uid.value, token: token.value })
const validationError = computed(() => parseApiError(error.value))

const {
  mutate: resetPassword,
  isPending: isResetingPassword,
  isSuccess,
  error: resetError,
} = useResetPassword()
const resetingError = computed(() => parseApiError(resetError.value))

const handleReset = () => {
  resetPassword({
    uid: uid.value,
    token: token.value,
    body: form.value,
  })
}
</script>

<style scoped>
.reset-card {
  width: min(100%, 520px);
  padding: 2rem;
}

.reset-form {
  display: grid;
  gap: 0.9rem;
}

.reset-success {
  display: grid;
  gap: 0.8rem;
}

.back-btn {
  text-align: center;
}

@media (max-width: 640px) {
  .reset-card {
    border-radius: 18px;
  }
}
</style>
