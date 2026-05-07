import { describe, it, expect } from 'vitest'
import { useForm } from '../useForm'
import * as v from 'valibot'

const schema = v.object({
  username: v.pipe(v.string(), v.minLength(3)),
  full_name: v.pipe(v.string(), v.minLength(3)),
})

describe('useForm', () => {
  const initial = {
    username: 'john',
    full_name: 'John Doe',
  }

  it('initializes fields correctly', () => {
    const form = useForm(schema, initial)

    expect(form.fields.value).toEqual(initial)
    expect(form.errors.value).toEqual({})
  })

  it('hydrates form values', () => {
    const form = useForm(schema, initial)

    form.hydrate({
      username: 'alice',
      full_name: 'Alice Smith',
    })

    expect(form.fields.value.username).toBe('alice')
    expect(form.fields.value.full_name).toBe('Alice Smith')
    expect(form.errors.value).toEqual({})
  })

  it('resets form values', () => {
    const form = useForm(schema, initial)

    form.hydrate({
      username: 'changed',
      full_name: 'Changed Name',
    })

    form.reset()

    expect(form.fields.value).toEqual(initial)
    expect(form.errors.value).toEqual({})
  })

  it('passes validation with valid data', () => {
    const form = useForm(schema, initial)

    const result = form.validate()

    expect(result).toBe(true)
    expect(form.errors.value).toEqual({})
  })

  it('fails validation with invalid data', () => {
    const form = useForm(schema, {
      username: 'a',
      full_name: 'b',
    })

    const result = form.validate()

    expect(result).toBe(false)
    expect(Object.keys(form.errors.value).length).toBeGreaterThan(0)
  })

  it('validates single field', () => {
    const form = useForm(schema, {
      username: 'a',
      full_name: 'John Doe',
    })

    form.validateField('username')

    expect(form.errors.value.username).toBeDefined()
  })

  it('sets error manually', () => {
    const form = useForm(schema, initial)

    form.setError('username', 'Custom error')

    expect(form.errors.value.username).toBe('Custom error')
  })
})
