import * as v from 'valibot'

export const CreateCertificateSchema = v.object({
  user: v.pipe(v.number(), v.integer(), v.minValue(1, 'User is required')),
  tournament: v.pipe(v.number(), v.integer(), v.minValue(1, 'Tournament is required')),
  team: v.pipe(v.number(), v.integer(), v.minValue(1, 'Team is required')),
  template: v.pipe(v.number(), v.integer(), v.minValue(1, 'Template is required')),
  placement: v.pipe(v.string(), v.nonEmpty('Placement is required')),
  certificate_number: v.pipe(v.string(), v.nonEmpty('Certificate number is required')),
})
