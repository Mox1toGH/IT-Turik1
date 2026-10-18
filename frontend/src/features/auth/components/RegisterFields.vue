<template>
  <div class="register-fields">
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

    <label v-if="isRestrictedRole" class="form-item">
      <p class="form-label full-width">Activation code</p>
      <ui-input
        v-model="form.fields.value.activation_code"
        @blur="form.validateField('activation_code')"
        :is-invalid="!!form.errors.value.activation_code"
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
          <phone-field
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
  </div>
</template>

<script setup lang="ts">
import type { Ref } from 'vue'
import PhoneField from '@/components/shared/PhoneField.vue'
import UiPasswordField from '@/components/ui/UiPasswordField'
import UiInput from '@/components/ui/UiInput'
import UiSelect from '@/components/ui/UiSelect'
import type { FormErrors } from '@/composables/useForm'
import type { UserRole } from '@/api/backendAPINinja.schemas'

export interface RegisterFormValues {
  username: string
  full_name: string
  email: string
  password: string
  role: UserRole
  activation_code: string
  phone: string
  city: string
}

export interface RegisterForm {
  fields: Ref<RegisterFormValues>
  errors: Ref<FormErrors>
  validateField: (field: string) => void
}

export interface RoleOption {
  value: string
  label: string
}

interface Props {
  form: RegisterForm
  roleOptions: RoleOption[]
  isRestrictedRole: boolean
}

defineProps<Props>()
</script>

<style scoped>
.register-fields {
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
  border-top: 1px solid var(--border);
}

.profile-header {
  margin-bottom: 0.1rem;
}

.full-width {
  grid-column: 1 / -1;
}

@media (max-width: 760px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
