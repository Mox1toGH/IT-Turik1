import { describe, it, expect } from 'vitest'
import * as v from 'valibot'
import { useForm } from '../useForm'

const schema = v.object({
  username: v.pipe(v.string(), v.minLength(3, 'username short')),
  full_name: v.pipe(v.string(), v.minLength(3, 'name short')),
})

const nestedSchema = v.object({
  items: v.array(v.object({ name: v.pipe(v.string(), v.minLength(2, 'item short')) })),
})

describe('useForm', () => {
  const initial = { username: 'john', full_name: 'John Doe' }

  it('initializes fields correctly', () => {
    const form = useForm(schema, initial)

    expect(form.fields.value).toEqual(initial)
    expect(form.errors.value).toEqual({})
    expect(form.isDirty.value).toBe(false)
  })

  it('does not mutate or share reference with initialValues', () => {
    const source = { items: [{ name: 'ab' }] }
    const form = useForm(nestedSchema, source)

    form.fields.value.items[0]!.name = 'changed'

    expect(source.items[0]!.name).toBe('ab')
  })

  it('hydrates form values and clears errors', () => {
    const form = useForm(schema, initial)
    form.setError('username', 'boom')

    form.hydrate({ username: 'alice', full_name: 'Alice Smith' })

    expect(form.fields.value).toEqual({ username: 'alice', full_name: 'Alice Smith' })
    expect(form.errors.value).toEqual({})
    expect(form.isDirty.value).toBe(false)
  })

  it('reset returns to initial values and clears errors', () => {
    const form = useForm(schema, initial)

    form.fields.value.username = 'changed'
    form.setError('username', 'boom')
    form.reset()

    expect(form.fields.value).toEqual(initial)
    expect(form.errors.value).toEqual({})
  })

  it('reset after hydrate returns to hydrated values, not the original', () => {
    const form = useForm(schema, initial)

    form.hydrate({ username: 'server', full_name: 'Server Name' })
    form.fields.value.username = 'edited'
    form.reset()

    expect(form.fields.value).toEqual({ username: 'server', full_name: 'Server Name' })
  })

  it('reset restores nested values (deep clone)', () => {
    const form = useForm(nestedSchema, { items: [{ name: 'ab' }] })

    form.fields.value.items[0]!.name = 'changed'
    form.fields.value.items.push({ name: 'new' })
    form.reset()

    expect(form.fields.value).toEqual({ items: [{ name: 'ab' }] })
  })

  it('tracks isDirty', () => {
    const form = useForm(schema, initial)

    form.fields.value.username = 'other'
    expect(form.isDirty.value).toBe(true)

    form.fields.value.username = 'john'
    expect(form.isDirty.value).toBe(false)
  })

  it('passes validation with valid data', () => {
    const form = useForm(schema, initial)

    expect(form.validate()).toBe(true)
    expect(form.errors.value).toEqual({})
  })

  it('fails validation and fills errors per field', () => {
    const form = useForm(schema, { username: 'a', full_name: 'b' })

    expect(form.validate()).toBe(false)
    expect(form.errors.value).toEqual({
      username: 'username short',
      full_name: 'name short',
    })
  })

  it('clears errors after the data becomes valid', () => {
    const form = useForm(schema, { username: 'a', full_name: 'John Doe' })

    expect(form.validate()).toBe(false)
    form.fields.value.username = 'alice'

    expect(form.validate()).toBe(true)
    expect(form.errors.value).toEqual({})
  })

  it('validates a single field without touching others', () => {
    const form = useForm(schema, { username: 'a', full_name: 'b' })

    form.validateField('username')

    expect(form.errors.value.username).toBe('username short')
    expect(form.errors.value.full_name).toBeUndefined()
  })

  it('validateField clears the error when the field becomes valid', () => {
    const form = useForm(schema, { username: 'a', full_name: 'John Doe' })

    form.validateField('username')
    form.fields.value.username = 'alice'
    form.validateField('username')

    expect(form.errors.value.username).toBeUndefined()
  })

  it('uses dot path for nested errors', () => {
    const form = useForm(nestedSchema, { items: [{ name: 'ok' }, { name: 'x' }] })

    form.validate()

    expect(form.errors.value['items.1.name']).toBe('item short')
  })

  it('sets error manually', () => {
    const form = useForm(schema, initial)

    form.setError('username', 'Custom error')

    expect(form.errors.value.username).toBe('Custom error')
  })

  it('setApiErrors merges with existing errors', () => {
    const form = useForm(schema, initial)

    form.setError('username', 'local')
    form.setApiErrors({ full_name: 'from api' })

    expect(form.errors.value).toEqual({ username: 'local', full_name: 'from api' })
  })
})
