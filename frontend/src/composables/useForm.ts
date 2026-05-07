import * as v from 'valibot'
import { ref } from 'vue'

type Errors<T> = Partial<Record<keyof T, string>>

export function useForm<T extends object>(schema: v.GenericSchema, initialValues: T) {
  const fields = ref<T>({ ...initialValues })
  const errors = ref<Errors<T>>({})

  function validate(): boolean {
    const result = v.safeParse(schema, fields.value)
    Object.keys(errors.value).forEach((key) => delete errors.value[key])

    if (!result.success) {
      result.issues.forEach((issue) => {
        const field = issue.path?.[0]?.key as keyof T
        if (field) errors.value[field] = issue.message
      })
      return false
    }
    return true
  }

  function validateField(field: keyof T) {
    const result = v.safeParse(schema, fields.value)
    delete errors.value[field]
    const issue = result.issues?.find((issue) => issue.path?.[0]?.key === field)
    if (issue) errors.value[field] = issue.message
  }

  function setError(key: keyof T, value: string) {
    errors.value[key] = value
  }

  function hydrate(values: T) {
    fields.value = { ...values }
    errors.value = {}
  }

  function reset() {
    fields.value = initialValues
    errors.value = {}
  }

  return { fields, errors, validate, validateField, setError, hydrate, reset }
}
