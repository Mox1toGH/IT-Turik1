<template>
  <section class="page-shell centered">
    <ui-card class="activate-card">
      <template #header>
        <div>
          <p class="section-eyebrow">Email Verification</p>
          <h1 class="section-title activate-title">Account activation</h1>
        </div>
      </template>

      <div>
        <p v-if="isPending" class="text-muted status">Checking your activation token...</p>

        <div v-if="isSuccess" class="notice success">
          Account was successfully activated
          <router-link to="/login">Go to sign in</router-link>
        </div>
      </div>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import UiCard from '@/components/ui/UiCard.vue'
import { useActivateAccount } from '@/api/queries/accounts'
import { useNotification } from '@/composables/useNotification'
import { parseApiError } from '@/api/errors'

const route = useRoute()
const { showNotification } = useNotification()

const { mutate: activate, isPending, isSuccess } = useActivateAccount()

onMounted(async () => {
  const { uid, token } = route.params
  if (!uid) return
  if (!token) return

  activate(
    { uid: uid as string, token: token as string },
    {
      onError: (error) => {
        const parsedError = parseApiError(error)
        showNotification(parsedError?.message, 'error')
      },
    },
  )
})
</script>

<style scoped>
.activate-card {
  width: min(100%, 520px);
  padding: 2rem;
  text-align: center;
}

.activate-title {
  margin-top: 0.2rem;
}

.status {
  margin-top: 1rem;
}

.notice {
  display: grid;
  gap: 0.45rem;
}

.notice a {
  color: var(--brand-700);
  font-weight: 700;
}
</style>
