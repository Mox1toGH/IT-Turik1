export interface PointsBalance {
  user_id: number
  balance: number
  updated_at: string
}

export interface PointsTransaction {
  id: number
  user_id: number
  order_id?: number | null
  amount: number
  reason: string
  created_at: string
}

export interface PaginatedPointsTransactions {
  count: number
  next: string | null
  previous: string | null
  results: PointsTransaction[]
}

export type PointsOrdering = '-created_at' | 'created_at' | 'amount' | '-amount'

export interface AdminModifyPointsBody {
  operation: 'add' | 'subtract' | 'set' | 'reset'
  amount?: number
  reason: string
}

export interface AdminModifyPointsResponse {
  user: {
    id: number
    username: string
    email: string
  }
  balance: PointsBalance
  transaction: PointsTransaction
}
