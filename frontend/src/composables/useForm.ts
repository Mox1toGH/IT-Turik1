import * as v from 'valibot'
import { computed, ref, toRaw, type Ref } from 'vue'

export type FormErrors = Record<string, string>

export function useForm<T extends object>(schema: v.GenericSchema<T, unknown>, initialValues: T) {
  let initial = structuredClone(toRaw(initialValues))
  const fields = ref(structuredClone(initial)) as Ref<T>
  const errors = ref<FormErrors>({})

  const isDirty = computed(() => JSON.stringify(fields.value) !== JSON.stringify(initial))

  function collectErrors(): FormErrors {
    const result = v.safeParse(schema, fields.value)
    if (result.success) return {}

    const out: FormErrors = {}
    for (const issue of result.issues) {
      const key = v.getDotPath(issue) ?? '_form'
      if (!(key in out)) out[key] = issue.message
    }
    return out
  }

  function validate(): boolean {
    errors.value = collectErrors()
    return Object.keys(errors.value).length === 0
  }

  function validateField(field: string) {
    const next = collectErrors()

    if (field in next) errors.value[field] = next[field]!
    else delete errors.value[field]
  }

  const setError = (key: string, message: string) => {
    errors.value[key] = message
  }
  const setApiErrors = (details: FormErrors) => {
    errors.value = { ...errors.value, ...details }
  }

  function hydrate(values: T) {
    initial = structuredClone(toRaw(values))
    fields.value = structuredClone(initial)
    errors.value = {}
  }

  function reset() {
    fields.value = structuredClone(initial)
    errors.value = {}
  }

  return {
    fields,
    errors,
    isDirty,
    validate,
    validateField,
    setError,
    setApiErrors,
    hydrate,
    reset,
  }
}
