import * as v from 'valibot'

export const CreateTeamSchema = v.object({
  name: v.pipe(v.string(), v.minLength(1, 'Team name cannot be empty')),
  email: v.pipe(v.string(), v.email('Invalid email')),
  organization: v.string(),
  contact_telegram: v.pipe(
    v.string(),
    v.regex(
      /^@?[A-Za-z][A-Za-z0-9_]{4,31}$/,
      'must be 5-32 characters, start with a letter, letters/digits/_',
    ),
  ),
  contact_discord: v.pipe(
    v.string(),
    v.regex(
      /^@?(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?$/,
      'must be 2-32 characters, letters/digits/._ with optional #1234',
    ),
  ),
  is_public: v.boolean(),
  member_ids: v.array(v.number()),
})

export const EditTeamSchema = v.object({
  email: v.pipe(v.string(), v.email('Invalid email')),
  name: v.pipe(v.string(), v.minLength(1, 'Team name cannot be empty')),
  organization: v.pipe(v.string()),
  contact_telegram: v.union([
    v.literal(''),
    v.pipe(
      v.string(),
      v.regex(
        /^@?[A-Za-z][A-Za-z0-9_]{4,31}$/,
        'must be 5–32 characters, start with a letter, letters/digits/_',
      ),
    ),
  ]),
  contact_discord: v.union([
    v.literal(''),
    v.pipe(
      v.string(),
      v.regex(
        /^@?(?=.{2,32}$)[A-Za-z0-9._]+(?:#[0-9]{4})?$/,
        'must be 2-32 characters, letters/digits/._ with optional #1234',
      ),
    ),
  ]),
})
