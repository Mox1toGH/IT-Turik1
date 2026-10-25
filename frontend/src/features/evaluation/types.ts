export interface Criterion {
  id: string
  name: string
  description: string
  max_score: number
}

export interface EvaluationScore {
  criterion_id: string
  criterion_name?: string | null
  score: number
}

export interface Evaluation {
  id?: number
  assignment?: number
  scores: EvaluationScore[]
  total_score?: number | null
  final_score?: number | null
  comment?: string | null
  created_at?: string
}

export interface JuryAssignment {
  id: number
  submission: number
  submission_details: {
    id: number
    team: number
    round: number
    team_details: { id: number; name: string; is_public: boolean }
    round_details: { id: number; name: string; status: string; tournament: number; criteria: Criterion[] }
    github_url: string
    demo_video_url: string
    live_demo_url: string
    description: string
  }
  round_details: { id: number; name: string; status: string; tournament: number; criteria: Criterion[] }
  evaluation?: Evaluation | null
  is_evaluated: boolean
  created_at: string
}

export type JuryEvaluation = Evaluation

export type { Criterion as EvaluationCriterion }

