<script lang="ts">
import { defineComponent, h, Fragment, ref, onErrorCaptured } from 'vue'
import { TriangleAlert } from 'lucide-vue-next'
import UiButton from '@/components/ui/UiButton.vue'

// Fragment in the happy path: zero extra DOM, so card flex layouts
// (e.g. variant="stat" rows) are unaffected. Retry remounts via key.
export default defineComponent({
  name: 'UiErrorBoundary',
  setup(_, { slots }) {
    const hasError = ref(false)
    const renderKey = ref(0)

    onErrorCaptured((err, instance, info) => {
      hasError.value = true
      console.error('[UiErrorBoundary] render error:', err, info, instance)
      return false
    })

    const retry = () => {
      hasError.value = false
      renderKey.value += 1
    }

    return () => {
      if (!hasError.value) {
        return h(Fragment, { key: renderKey.value }, slots.default?.())
      }
      return h('div', { class: 'card-error', role: 'alert' }, [
        h(TriangleAlert, { class: 'card-error__icon', 'aria-hidden': 'true' }),
        h('p', { class: 'card-error__title' }, 'Something went wrong'),
        h('p', { class: 'card-error__hint text-muted' }, 'This block failed to display.'),
        h(UiButton, { size: 'sm', variant: 'secondary', onClick: retry }, () => 'Try again'),
      ])
    }
  },
})
</script>

<style scoped>
.card-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 0.35rem;
  padding: 1.5rem 1rem;
}

.card-error__icon {
  width: 22px;
  height: 22px;
  color: var(--muted-foreground);
}

.card-error__title {
  font-weight: 700;
  margin: 0;
}

.card-error__hint {
  margin: 0 0 0.5rem;
  font-size: 0.85rem;
}
</style>
