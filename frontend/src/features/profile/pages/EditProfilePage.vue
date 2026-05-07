<template>
  <section class="page-shell">
    <ui-card>
      <template #header>
        <div>
          <div class="head">
            <div>
              <p class="section-eyebrow">User Center</p>
              <h1 class="section-title profile-title">Edit Profile</h1>
            </div>
          </div>

          <p class="section-subtitle">Update your account details below and save your changes.</p>
        </div>
      </template>

      <form @submit.prevent="handleSubmit" class="profile-form">
        <div class="form-grid">
          <label class="form-item">
            <p class="form-label">Full name</p>

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
            <small v-if="form.errors.value.full_name" class="text-error">{{
              form.errors.value.full_name
            }}</small>
          </label>

          <label class="form-item">
            <p class="form-label">Username</p>
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

            <small v-if="form.errors.value.username" class="text-error">{{
              form.errors.value.username
            }}</small>
          </label>

          <label class="form-item">
            <p class="form-label">Phone number</p>

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
            <small v-if="form.errors.value.phone" class="text-error">{{
              form.errors.value.phone
            }}</small>
          </label>

          <label class="form-item">
            <p class="form-label">City</p>
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

            <small v-if="form.errors.value.city" class="text-error">{{
              form.errors.value.city
            }}</small>
          </label>
        </div>

        <div class="actions">
          <ui-button type="submit" :disabled="isUpdatingProfile || isLoadingError || isLoading">
            <LoadingIcon v-if="isUpdatingProfile" />
            Save changes
          </ui-button>

          <ChangePasswordModal :disabled="isLoadingError || isLoading" />

          <ui-button
            variant="secondary"
            :disabled="isUpdatingProfile || isLoadingError || isLoading"
            @click="goBackToProfile"
            >Cancel</ui-button
          >
        </div>
      </form>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useRouter } from 'vue-router'
import PhoneField from '@/components/shared/PhoneField.vue'
import { useNotification } from '@/composables/useNotification'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiCard from '@/components/ui/UiCard.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { useProfile, useUpdateProfile } from '@/api/queries/accounts'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import ChangePasswordModal from '../components/profile/modals/ChangePasswordModal.vue'
import { parseApiError } from '@/api/errors'
import { useForm } from '@/composables/useForm'
import { EditProfileSchema } from '@/schemas/profile.schema'

interface ProfileForm {
  username: string
  full_name: string
  phone: string
  city: string
}

const { data: user, isLoading, isLoadingError } = useProfile()

const form = useForm(EditProfileSchema, {
  username: '',
  full_name: '',
  phone: '',
  city: '',
})

const router = useRouter()
const { showNotification } = useNotification()

const { mutate: updateProfile, isPending: isUpdatingProfile } = useUpdateProfile()

const handleSubmit = () => {
  if (!form.validate()) return

  updateProfile(
    { body: form.fields.value },
    {
      onSuccess: () => {
        showNotification('Profile updated successfully.', 'success')
        router.push('/profile')
      },
      onError: (err) => {
        const parsedError = parseApiError(err)
        for (const [field, errors] of Object.entries(parsedError?.details || {})) {
          form.setError(field as keyof ProfileForm, errors?.[0] ?? 'Invalid value')
        }

        showNotification(parsedError?.message, 'error')
      },
    },
  )
}

const goBackToProfile = () => {
  router.push('/profile')
}

watch(
  user,
  (user) => {
    if (!user) return

    form.hydrate({
      username: user.username ?? '',
      full_name: user.full_name ?? '',
      phone: user.phone ?? '',
      city: user.city ?? '',
    })
  },
  { immediate: true },
)
</script>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

.profile-title {
  margin-top: 0.2rem;
}

.section-subtitle {
  margin-bottom: 0;
}

.state-box {
  margin-top: 1rem;
  border-radius: 14px;
  border: 1px solid var(--line-soft);
  padding: 0.9rem 1rem;
  background: rgba(255, 255, 255, 0.85);
}

.state-box.error {
  color: #991b1b;
  border-color: rgba(220, 38, 38, 0.25);
  background: rgba(254, 242, 242, 0.9);
}

.form-grid {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.accent-hover:hover {
  border-color: var(--brand-500);
  color: var(--brand-700);
  background: rgba(20, 184, 166, 0.08);
}

.password-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.panel-title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.2rem;
}

.icon-close {
  border: 1px solid var(--line-strong);
  background: #fff;
  color: var(--color-gray-700);
  width: 2.1rem;
  height: 2.1rem;
  border-radius: 10px;
  font-size: 1.2rem;
  cursor: pointer;
}

.icon-close:hover {
  background: rgba(15, 23, 42, 0.06);
}

.mode-switch {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.8rem;
}

.switch-btn {
  padding: 0.55rem 0.8rem;
}

.switch-btn.active {
  border-color: var(--brand-500);
  color: var(--brand-700);
  background: rgba(20, 184, 166, 0.12);
}

.password-form {
  display: grid;
  gap: 0.75rem;
}

@media (max-width: 760px) {
  .profile-card {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .actions {
    flex-direction: column;
  }

  .mode-switch {
    width: 100%;
  }
}
</style>
