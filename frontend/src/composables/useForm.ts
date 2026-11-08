import * as v from 'valibot'
import { computed, ref, shallowRef, toRaw, type ComputedRef, type Ref } from 'vue'

export type FormErrors<T extends object = Record<string, unknown>> = Partial<
  Record<keyof T & string, string>
>

export interface UseFormReturn<T extends object> {
  fields: Ref<T>
  errors: Ref<FormErrors<T>>
  isDirty: ComputedRef<boolean>
  validate: () => boolean
  validateField: (field: string) => void
  setError: (key: string, message: string) => void
  hydrate: (values: T) => void
  reset: () => void
}

export function useForm<T extends object>(
  schema: v.GenericSchema<unknown, unknown>,
  initialValues: T,
): UseFormReturn<T> {
  let initial = structuredClone(toRaw(initialValues))
  const fields = ref(structuredClone(initial)) as Ref<T>
  const errors = shallowRef<FormErrors<T>>({})

  const isDirty = computed(() => JSON.stringify(fields.value) !== JSON.stringify(initial))

  function isField(key: string): key is keyof T & string {
    return Object.hasOwn(fields.value, key)
  }

  function collectErrors(): FormErrors<T> {
    const result = v.safeParse(schema, fields.value)
    if (result.success) return {}

    const out: FormErrors<T> = {}
    for (const issue of result.issues) {
      const key = v.getDotPath(issue)
      if (!key || !isField(key)) continue
      if (!(key in out)) out[key] = issue.message
    }
    return out
  }

  function validate(): boolean {
    errors.value = collectErrors()
    return Object.keys(errors.value).length === 0
  }

  function validateField(field: string) {
    if (!isField(field)) return

    const next = collectErrors()

    if (field in next) errors.value = { ...errors.value, [field]: next[field] }
    else {
      const updatedErrors = { ...errors.value }
      delete updatedErrors[field]
      errors.value = updatedErrors
    }
  }

  const setError = (key: string, message: string) => {
    if (isField(key)) errors.value = { ...errors.value, [key]: message }
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
    hydrate,
    reset,
  }
}
