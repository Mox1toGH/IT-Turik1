import type { ComputedRef, InjectionKey } from 'vue'

/** Reactive query state inherited by query fields inside the nearest block. */
export interface QueryContext {
  isInitialLoading: ComputedRef<boolean>
  isFetching: ComputedRef<boolean>
}

export const queryContextKey: InjectionKey<QueryContext> = Symbol('query-context')
