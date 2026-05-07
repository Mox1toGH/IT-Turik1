import type { User } from '@/api/dbTypes'
import * as v from 'valibot'

export const PasswordSchema = v.pipe(
  v.string(),
  v.minLength(8, 'Password must be at least 8 characters'),
  v.regex(/[A-Z]/, 'Password must contain at least one uppercase letter'),
  v.regex(/[a-z]/, 'Password must contain at least one lowercase letter'),
  v.regex(/[0-9]/, 'Password must contain at least one number'),
  v.regex(/[!@#$%^&*(),.?":{}|<>]/, 'Password must contain at least one special character'),
)

export const LoginSchema = v.object({
  username: v.pipe(v.string(), v.minLength(1, 'Username cannot be empty')),
  password: PasswordSchema,
})

export const RegisterSchema = v.object({
  username: v.pipe(
    v.string(),
    v.minLength(3, 'Username must be at least 3 characters.'),
    v.regex(/^[A-Za-z0-9@.+_-]+$/, 'Use letters, numbers, and @ . + - _ only.'),
  ),
  full_name: v.pipe(v.string(), v.minLength(1, 'Fullname cannot be empty')),
  email: v.pipe(v.string(), v.email('Invalid email')),
  password: PasswordSchema,
  role: v.picklist<User['role'][]>(['admin', 'jury', 'organizer', 'team']),
  phone: v.pipe(
    v.string(),
    v.trim(),
    v.regex(/^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/, 'Invalid phone number'),
  ),
  city: v.pipe(v.string(), v.minLength(2, 'City must be at least 2 characters.')),
})
