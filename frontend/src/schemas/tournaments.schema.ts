import { combineDateAndTime } from '@/lib/date'
import { tiptapJsonToText } from '@/lib/utils'
import * as v from 'valibot'

export const TimeSchema = v.pipe(
  v.string(),
  v.regex(/^([01]\d|2[0-3]):[0-5]\d$/, 'Time must be in HH:MM format (00:00–23:59)'),
)

export const CreateTournamentSchema = v.pipe(
  v.object({
    name: v.pipe(v.string(), v.minLength(1, 'Tournament name is required')),
    description: v.pipe(
      v.string(),
      v.minLength(20, 'Description must be at least 20 characters long'),
    ),
    startDate: v.date(),
    startTime: TimeSchema,
    endDate: v.date(),
    endTime: TimeSchema,
    rounds_count: v.pipe(v.number('must be a number'), v.minValue(1, 'Rounds must be at least 1')),
    max_teams: v.pipe(
      v.number('must be a number'),
      v.minValue(2, 'Maximum teams must be at least 2'),
    ),
    min_team_members: v.pipe(
      v.number('must be a number'),
      v.minValue(2, 'Minimum team members must be at least 2'),
    ),
  }),

  v.forward(
    v.partialCheck(
      [['startDate'], ['endDate'], ['startTime'], ['endTime']],
      (input) => {
        const combinedStartDate = combineDateAndTime(input.startDate, input.startTime)
        const combinedEndDate = combineDateAndTime(input.endDate, input.endTime)
        return combinedEndDate > combinedStartDate
      },
      'End date/time must be after start date/time',
    ),
    ['endDate'],
  ),
)

function tiptapJsonMinLength(min: number, message: string) {
  return v.pipe(
    v.unknown(),
    v.check((value) => tiptapJsonToText(value).length >= min, message),
  )
}

export const CreateRoundSchema = v.pipe(
  v.object({
    name: v.pipe(v.string(), v.minLength(1, 'Name is required')),
    description: tiptapJsonMinLength(10, 'Description must be at least 10 characters long'),
    passing_count: v.pipe(v.number(), v.minValue(1, 'Minimum 1 team shoud pass')),
    tech_requirements: tiptapJsonMinLength(
      10,
      'Technical requirements must be at least 10 characters long',
    ),
    must_have_requirements: tiptapJsonMinLength(
      10,
      'Must have must be at least 10 characters long',
    ),
    criteria: v.pipe(
      v.array(
        v.object({
          id: v.string(),
          name: v.pipe(v.string(), v.minLength(1, 'Criterion name is required')),
          description: v.pipe(v.string(), v.minLength(1, 'Criterion description is required')),
          max_score: v.pipe(
            v.number('must be a number'),
            v.minValue(1, 'Max score must be at least 1'),
          ),
        }),
      ),
      v.minLength(1, 'At least one criterion is required'),
    ),

    start_date: v.date(),
    end_date: v.date(),
  }),

  v.forward(
    v.partialCheck(
      [['start_date'], ['end_date']],
      (input) => input.end_date > input.start_date,
      'End date must be after start date',
    ),
    ['end_date'],
  ),
)

export const SubmitRoundSchema = v.object({
  github_url: v.pipe(
    v.string('GitHub URL is required'),
    v.nonEmpty('GitHub URL cannot be empty'),
    v.url('Invalid GitHub URL format'),
  ),

  demo_video_url: v.pipe(
    v.string('Demo URL is required'),
    v.nonEmpty('Demo URL cannot be empty'),
    v.url('Invalid Demo URL format'),
  ),

  description: v.pipe(
    v.string('Description is required'),
    v.nonEmpty('Description cannot be empty'),
    v.minLength(10, 'Description must be at least 10 characters long'),
    v.maxLength(500, 'Description must not exceed 500 characters'),
  ),
})

export const EditEventSchema = v.object({
  title: v.pipe(
    v.string('Title is required'),
    v.nonEmpty('Title cannot be empty'),
    v.minLength(3, 'Title must be at least 3 characters long'),
    v.maxLength(100, 'Title must not exceed 100 characters'),
  ),

  startDate: v.pipe(v.date('Start date is required')),

  startTime: v.pipe(
    TimeSchema,
    v.custom((value) => value != null, 'Start time is required'),
  ),
})

export const AddEventSchema = v.object({
  title: v.pipe(
    v.string('Title is required'),
    v.nonEmpty('Title cannot be empty'),
    v.minLength(3, 'Title must be at least 3 characters long'),
    v.maxLength(100, 'Title must not exceed 100 characters'),
  ),

  description: v.pipe(
    v.string('Description is required'),
    v.nonEmpty('Description cannot be empty'),
    v.minLength(5, 'Description must be at least 5 characters long'),
    v.maxLength(500, 'Description must not exceed 500 characters'),
  ),

  link: v.optional(
    v.pipe(
      v.string('Link must be a string'),
      v.nonEmpty('Link cannot be empty'),
      v.url('Invalid URL format'),
    ),
  ),

  start_date: v.pipe(v.date('Start date is required')),
  start_time: TimeSchema,
})
