<template>
  <form class="profile-form" @submit.prevent="handleSubmit">
    <ui-card variant="form" class="form-panel">
      <div class="panel-header">
        <span class="step-marker">01</span>
        <div>
          <h3>Profile details</h3>
          <p class="text-muted">Update the information shown on your account.</p>
        </div>
      </div>

      <div class="row two">
        <label class="field">
          <span class="label">Full name</span>
          <ui-skeleton-loader :loading="isLoading" style="width: 100%">
            <template #skeleton>
              <ui-skeleton variant="rect" height="45px" width="100%" />
            </template>

            <ui-input
              v-model="form.fields.value.full_name"
              :disabled="isLoadingError"
              :isInvalid="!!form.errors.value.full_name"
              style="width: 100%"
              type="text"
              placeholder="John Doe"
              required
              @blur="form.validateField('full_name')"
            />
          </ui-skeleton-loader>
          <small v-if="form.errors.value.full_name" class="error">{{
            form.errors.value.full_name
          }}</small>
        </label>

        <label class="field">
          <span class="label">Username</span>
          <ui-skeleton-loader :loading="isLoading" style="width: 100%">
            <template #skeleton>
              <ui-skeleton variant="rect" height="45px" width="100%" />
            </template>

            <ui-input
              v-model="form.fields.value.username"
              :disabled="isLoadingError"
              :isInvalid="!!form.errors.value.username"
              style="width: 100%"
              placeholder="johndoe"
              required
              @blur="form.validateField('username')"
            />
          </ui-skeleton-loader>
          <small v-if="form.errors.value.username" class="error">{{
            form.errors.value.username
          }}</small>
        </label>

        <label class="field">
          <span class="label">Phone number</span>
          <ui-skeleton-loader :loading="isLoading" style="width: 100%">
            <template #skeleton>
              <ui-skeleton variant="rect" height="45px" width="100%" />
            </template>

            <PhoneField
              v-model="form.fields.value.phone"
              :disabled="isLoadingError"
              :isInvalid="!!form.errors.value.phone"
              @blur="form.validateField('phone')"
            />
          </ui-skeleton-loader>
          <small v-if="form.errors.value.phone" class="error">{{ form.errors.value.phone }}</small>
        </label>

        <label class="field">
          <span class="label">City</span>
          <ui-skeleton-loader :loading="isLoading" style="width: 100%">
            <template #skeleton>
              <ui-skeleton variant="rect" height="45px" width="100%" />
            </template>

            <ui-input
              v-model="form.fields.value.city"
              :disabled="isLoadingError"
              :isInvalid="!!form.errors.value.city"
              style="width: 100%"
              type="text"
              placeholder="Kyiv"
              required
              @blur="form.validateField('city')"
            />
          </ui-skeleton-loader>
          <small v-if="form.errors.value.city" class="error">{{ form.errors.value.city }}</small>
        </label>
      </div>
    </ui-card>

    <div class="footer-actions">
      <ui-button
        type="button"
        variant="secondary"
        :disabled="isLoadingError || isLoading"
        @click="emit('change-password')"
      >
        Change password
      </ui-button>
      <ui-button
        type="button"
        variant="secondary"
        :disabled="isUpdatingProfile || isLoadingError || isLoading"
        @click="emit('cancel')"
      >
        Cancel
      </ui-button>
      <ui-button type="submit" :disabled="isUpdatingProfile || isLoadingError || isLoading">
        <LoadingIcon v-if="isUpdatingProfile" />
        Save changes
      </ui-button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import PhoneField from '@/components/shared/PhoneField.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useForm } from '@/composables/useForm'
import { useNotification } from '@/composables/useNotification'
import { EditProfileSchema } from '@/schemas/profile.schema'
import { useGetUserProfile, useUpdateUserProfile } from '@/api/accounts/accounts'

interface ProfileForm {
  username: string
  full_name: string
  phone: string
  city: string
}

const emit = defineEmits<{
  cancel: []
  'change-password': []
  saved: []
}>()

const { showNotification } = useNotification()
const { data: user, isLoading, isLoadingError } = useGetUserProfile()

const form = useForm<ProfileForm>(EditProfileSchema, {
  username: '',
  full_name: '',
  phone: '',
  city: '',
})

const { mutate: updateProfile, isPending: isUpdatingProfile } = useUpdateUserProfile()

const handleSubmit = () => {
  if (!form.validate()) return

  updateProfile(
    { data: form.fields.value },
    {
      onSuccess: () => {
        showNotification('Profile updated successfully.', 'success')
        emit('saved')
      },
      onError: (error) => {
        for (const [field, errors] of Object.entries(error?.details || {})) {
          form.setError(field as keyof ProfileForm, errors?.[0] ?? 'Invalid value')
        }
        showNotification(error?.message, 'error')
      },
    },
  )
}

watch(
  user,
  (u) => {
    if (!u) return
    form.hydrate({
      username: u.username ?? '',
      full_name: u.full_name ?? '',
      phone: u.phone ?? '',
      city: u.city ?? '',
    })
  },
  { immediate: true },
)

defineExpose({ isSubmitting: isUpdatingProfile })
</script>

<style scoped>
.profile-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
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

.row.two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
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
  flex-wrap: wrap;
}

@media (max-width: 760px) {
  .row.two {
    grid-template-columns: 1fr;
  }

  .footer-actions {
    flex-direction: column;
  }

  .footer-actions .btn {
    width: 100%;
  }
}
</style>
