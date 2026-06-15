import * as v from 'valibot'
import { PasswordSchema } from './auth.schema'

export const EditProfileSchema = v.object({
  username: v.pipe(
    v.string(),
    v.minLength(3, 'Username must be at least 3 characters.'),
    v.regex(/^[A-Za-z0-9@.+_-]+$/, 'Use letters, numbers, and @ . + - _ only.'),
  ),
  full_name: v.pipe(v.string(), v.minLength(1, 'Fullname cannot be empty')),
  phone: v.pipe(
    v.string(),
    v.trim(),
    v.regex(/^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/, 'Invalid phone number'),
  ),
  city: v.pipe(v.string(), v.minLength(2, 'City must be at least 2 characters.')),
})

export const CompleteProfileSchema = v.pipe(
  v.object({
    username: v.pipe(
      v.string(),
      v.minLength(3, 'Username must be at least 3 characters.'),
      v.regex(/^[A-Za-z0-9@.+_-]+$/, 'Use letters, numbers, and @ . + - _ only.'),
    ),

    password: PasswordSchema,

    redeem_code: v.optional(v.string(), ''),

    role: v.union([
      v.literal('team'),
      v.literal('organizer'),
      v.literal('jury'),
      v.literal('admin'),
    ]),

    full_name: v.pipe(v.string(), v.minLength(1, 'Fullname cannot be empty')),

    phone: v.pipe(
      v.string(),
      v.trim(),
      v.regex(/^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/, 'Invalid phone number'),
    ),

    city: v.pipe(v.string(), v.minLength(2, 'City must be at least 2 characters.')),
  }),

  v.forward(
    v.check((input) => {
      if (['admin', 'jury', 'organizer'].includes(input.role)) {
        return input.redeem_code.trim().length > 0
      }
      return true
    }, 'Redeem code is required for this role.'),
    ['redeem_code'],
  ),
)

export const ChangePasswordSchema = v.pipe(
  v.object({
    current_password: PasswordSchema,
    new_password: PasswordSchema,
    confirm_password: PasswordSchema,
  }),

  v.forward(
    v.partialCheck(
      [['new_password'], ['confirm_password']],
      (input) => {
        return input.new_password === input.confirm_password
      },
      'The two passwords do not match.',
    ),
    ['confirm_password'],
  ),

  v.forward(
    v.partialCheck(
      [['current_password'], ['new_password']],
      (input) => {
        return input.new_password !== input.current_password
      },
      'New password must be different from current password',
    ),
    ['new_password'],
  ),
)
