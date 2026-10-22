These rules define the frontend architecture and coding conventions.

## Normative Terminology

- **MUST** — absolute requirement.
- **MUST NOT** — absolute prohibition.
- **SHOULD** — recommended practice.
- **MAY** — optional behavior.

## FE-001 Feature Boundaries and Dependency Direction

Features MUST remain independent of other features.

- A feature MUST NOT import another feature's internal implementation, including its components, composables, utilities, or other internal modules.
- A feature MAY import its own modules.
- `shared/` MUST NOT import from `features/`. Shared code MUST NOT depend on a specific feature.
- Functionality genuinely needed by multiple features SHOULD be moved to an appropriate shared location rather than imported directly from another feature.
- Application-shell files MAY compose features through their route entry points.
- Feature-specific code MUST remain in the feature that owns it.

The current ESLint rule allows imports matching `@/features/<feature>/routes` from anywhere. These route entry points SHOULD be used for application composition, not to create dependencies between features. If imports of another feature's routes must be forbidden inside features too, the ESLint rule MUST be tightened accordingly.

**Examples**

Forbidden: importing a component from another feature.

```ts
// features/news/components/CreateNewsModal.vue
import EditorModal from '@/features/tournaments/components/EditorModal.vue'
```

If the component is genuinely reusable, move it to an appropriate shared location. Otherwise, keep it inside the owning feature and avoid the cross-feature dependency.

Forbidden: a shared component depending on a feature.

```ts
// components/shared/AppSidebar.vue
import NotificationDropdown from '@/features/profile/components/NotificationDropdown.vue'
```

Allowed: importing within the same feature.

```ts
// features/tournaments/pages/TournamentDetailsPage.vue
import TournamentHeader from '@/features/tournaments/components/TournamentHeader.vue'
```

## FE-002 Feature Organization

The project SHOULD use feature-based vertical slices. Each feature SHOULD keep the pages, components, composables, and pure helpers that belong to its functionality together.

- Page-specific components SHOULD live near the page that uses them.
- Components shared by multiple pages within one feature MAY live in that feature's top-level `components/` directory.
- A folder MUST NOT be created pre-emptively when it has no meaningful grouping purpose.
- Files SHOULD be grouped by ownership and responsibility, not solely by technical type.
- The project MUST NOT adopt Atomic Design as a mandatory organizational model.
- Folder names and depth SHOULD remain simple enough that code ownership is easy to understand.

**Example**

```text
features/
  tournaments/
    pages/
      list/
        TournamentsPage.vue
        components/
          TournamentList.vue
          TournamentFilters.vue
        modals/
          CreateTournamentModal.vue
      details/
        TournamentDetailsPage.vue
        components/
          TournamentHeader.vue
        modals/
          EditTournamentModal.vue
    components/       # Used by multiple pages in this feature
    composables/
    lib/
```

The structure is illustrative, not mandatory. Create `components/` or `modals/` directories only when they improve organization.

## FE-003 Component Responsibilities

Components SHOULD primarily handle presentation and local user interaction. They MAY also fetch and display data when that is the component's primary responsibility.

Components MAY:

- Contain local reactive state, computed values, and event handlers.
- Use generated API query or mutation hooks directly for a straightforward fetch-and-display workflow.
- Render loading, error, empty, and success states for the data they display.
- Perform small, view-specific data transformations.

Components SHOULD NOT coordinate complex workflows, accumulate unrelated responsibilities, or duplicate business rules already implemented elsewhere.

Components MUST NOT be split solely because they exceed a particular line count. They SHOULD be split when separate responsibilities can be understood and maintained more clearly as separate components.

Unused components, props, imports, and styles SHOULD be removed.

**Example**

A component that displays a list MAY own the query and its display states directly:

```ts
const { data, isLoading, error } = useGetTournamentsQuery()
```

A component that coordinates several queries and mutations for a multi-step workflow SHOULD delegate that orchestration to a feature composable.

## FE-004 Component Logic and Composables

Components MUST keep logic that is local to their presentation and interactions.

Components MAY contain:

- Local reactive state (`ref`, `computed`).
- Event handlers.
- Simple derived values.
- API query and mutation hooks when fetching and displaying data is the component's primary responsibility.

Composables SHOULD encapsulate meaningful reactive behavior, reusable logic, or coordination of multiple operations.

Logic SHOULD be extracted into a composable when:

- It has an independent responsibility.
- It is reused in multiple places.
- It coordinates multiple queries, mutations, or other operations.
- Its complexity makes the component difficult to understand and maintain.

Feature-specific composables MUST remain within their owning feature. Shared composables MAY be used when the same reactive behavior is genuinely needed by multiple features.

Pure functions that do not require Vue reactivity or lifecycle MUST be implemented as ordinary functions, not composables.

Composables MUST NOT be created solely to wrap a single API query, mutation, `ref`, or `computed` without adding meaningful behavior.

The decision to extract logic MUST be based on responsibility, complexity, and reuse — NOT component line count.

**Examples**

Keep local UI state in the component:

```ts
const isMenuOpen = ref(false)

const displayName = computed(() =>
  user.value ? `${user.value.firstName} ${user.value.lastName}` : '',
)

function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value
}
```

A direct API query is acceptable when fetching and displaying data is the component's primary responsibility:

```ts
const { data, isLoading, error } = useGetTournamentQuery({
  path: { id: tournamentId },
})
```

Extract orchestration of multiple operations into a composable:

```ts
// useTournamentManagement.ts
export function useTournamentManagement() {
  const tournament = useGetTournamentQuery()
  const updateTournament = useUpdateTournamentMutation()
  const deleteTournament = useDeleteTournamentMutation()

  // Coordinate operations and related reactive behavior.
}
```

Use an ordinary function for pure logic:

```ts
// tournamentStatus.ts
export function getEffectiveTournamentStatus(tournament: Tournament) {
  // Calculate status without Vue reactivity or lifecycle.
}
```

Avoid a composable that only wraps an existing query without adding behavior:

```ts
// Unnecessary abstraction
export function useTournament() {
  return useGetTournamentQuery()
}
```

## FE-005 Business Logic and Pure Utilities

Pure, deterministic logic that does not require Vue reactivity or lifecycle MUST be implemented as ordinary functions.

- Pure logic used by only one feature SHOULD remain in that feature's `lib/` directory or near its only use when sufficiently small and local.
- Pure logic genuinely used across features with the same meaning MAY live in `shared/lib/`.
- Shared helpers MUST have consistent semantics for all consumers. Similar-looking logic MUST NOT be unified if it represents different business rules.
- Business rules SHOULD have one authoritative implementation when multiple parts of the application need the same rule.
- Time-dependent values used in reactive UI MUST be updated reactively when time passing can change the displayed result. Calling `Date.now()` in a render path alone MUST NOT be relied on to trigger updates.
- Permission checks SHOULD be centralized when their semantics are the same across the application. Different permission semantics MUST NOT be forced into one helper.

**Examples**

Feature-specific calculation:

```ts
// features/tournaments/lib/tournamentStatus.ts
export function getEffectiveTournamentStatus(tournament: Tournament) {
  // Pure tournament-specific business rule.
}
```

Shared formatting helper, only when multiple features use it consistently:

```ts
// shared/lib/formatDate.ts
export function formatDate(value: Date | string) {
  // Pure formatting function.
}
```

## FE-006 Avoiding Unnecessary Abstractions

Developers MUST NOT introduce abstractions without a concrete benefit.

- Potential future reuse alone MUST NOT justify extracting logic.
- A small amount of duplication MAY be preferable to an abstraction that obscures the original behavior.
- Existing abstractions SHOULD be reused when they genuinely match the required behavior.
- Code SHOULD remain close to where it is used unless separating it improves clarity, reuse, or maintainability.
- Helpers SHOULD be consolidated only when behavior and responsibilities genuinely match.
- Large catch-all modules such as `domain.ts` MUST NOT become dumping grounds for unrelated helpers.

**Examples**

Keep a simple event handler in the component:

```ts
function closeModal() {
  isModalOpen.value = false
}
```

Keep a simple one-off transformation local to its use:

```ts
const options = users.value.map((user) => ({
  label: user.name,
  value: user.id,
}))
```

Do not force unrelated behavior into one generic abstraction just because the code looks similar. Prefer a straightforward implementation over an abstraction that adds indirection without improving clarity or maintainability.

## FE-007 Generated API Code and Data Access

The `src/api/` directory is generated by Orval and MUST be treated as read-only.

- Developers MUST NOT manually edit files in `src/api/`.
- Custom types and handwritten API helpers MUST NOT be placed inside `src/api/`, because regeneration may delete them.
- Changes to generated API code MUST be made through its source schema or generator configuration, followed by regeneration.
- Feature-specific data orchestration SHOULD live in the owning feature's composables when it coordinates multiple operations or contains meaningful workflow logic.
- Components MAY use generated API hooks directly for straightforward fetch-and-display use cases.
- Small, local response-to-view mappings MAY remain in a component. Complex or reused mapping SHOULD live in an appropriate feature helper or composable.
- Query-client configuration, authentication persistence, and application-level connection lifecycle SHOULD remain separate responsibilities rather than accumulating in a single module.
- API origins MUST come from the configured shared API client/helper, not hardcoded component URLs.

This document does not prescribe a global query-invalidation registry. Cache updates and refetching SHOULD be implemented only when required by the relevant user flow and data consistency needs.

## FE-008 Query State and Presentational Containers

`UiCard` MUST remain a presentational container. It MUST NOT own API-query orchestration or interpret query lifecycle state. Query-state UI is independent of cards and MUST work inside any layout.

The legacy monolithic `UiQueryState` component is deprecated and has been removed. It MUST NOT be reintroduced; use `UiQueryBlock` for query-level errors and retry behavior, and `UiQueryField` for per-region skeletons and background-fetch dimming. The `useQueryState.ts` composable remains the shared internal lifecycle adapter used by `UiQueryBlock`; it is not the deprecated component.

The query UI has three separate responsibilities:

- `useQueryState.ts` derives reactive query data, initial loading, fetching, errors, error codes, and refetch behavior.
- `UiQueryBlock` owns initial query errors, retry, offline handling, stale-data retry feedback, and provides reactive query context. It MUST always render its default slot during loading and success. It MUST NOT render skeletons or interpret empty data.
- `UiQueryField` owns optional loading presentation and background-fetch dimming. It works inside and outside a block, and MUST NOT handle query errors, retries, or empty states.
- The feature consuming the data MUST decide what empty or missing data means and render the appropriate message, action, or fallback.

### Choosing a component

- Use one `UiQueryBlock` for a region that shares error and retry feedback. Nested blocks provide an isolated context to their descendant fields.
- Use fields for logical UI sections that need skeletons; keep static headings, labels, and role-independent controls outside them.
- A field uses its explicit `loading` prop when supplied, otherwise it inherits initial loading from the nearest block, otherwise it is not loading.
- A field without a skeleton always renders its default content. A standalone field can use `:loading` but has no inherited background-fetch state.
- `isFetching` dims existing field content. Initial loading controls skeleton visibility; background fetching never swaps existing content for a skeleton.
- Do not add `isEmpty`, `#empty`, `#empty-action`, or other empty-state APIs to either query component.

### State behavior

- Initial loading: render the block default slot; fields with a skeleton show it, while fields without one keep content visible.
- Initial error with no data: replace the block default content with its custom `#error` slot or the default full error UI.
- Background refetch: preserve content and dim fields. Never dim a skeleton.
- Refetch failure after data loaded: keep old content and show one block-level “Update failed” / Retry banner. Fields do not show errors or skeletons.
- Refetch success: preserve content and restore field opacity.

### Public API examples

Named slots MUST be declared before default content. The block supports only `#error`; fields support only `#skeleton` and the default slot.

Block content with feature-owned empty-state handling:

```vue
<script setup lang="ts">
import { useListTournaments } from '@/api/tournaments/tournaments'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'
import TournamentList from './TournamentList.vue'

const tournamentsQuery = useListTournaments()
const { data: tournaments } = tournamentsQuery
</script>

<template>
  <ui-query-block :query="tournamentsQuery" title="tournaments">
    <template #error="{ errorCode, retry }">
      <div role="alert">
        <p>Could not load tournaments ({{ errorCode }}).</p>
        <button type="button" @click="retry">Retry</button>
      </div>
    </template>

    <ui-query-field>
      <template #skeleton><ui-skeleton v-for="i in 3" :key="i" width="100%" /></template>
      <p v-if="tournaments?.length === 0">No tournaments yet.</p>
      <TournamentList v-else :tournaments="tournaments" />
    </ui-query-field>
  </ui-query-block>
</template>
```

Mixed static and query-backed content, with per-field skeletons:

```vue
<script setup lang="ts">
import { useGetTournament } from '@/api/tournaments/tournaments'
import { UiQueryBlock, UiQueryField } from '@/components/query'
import UiSkeleton from '@/components/ui/UiSkeleton'

const tournamentQuery = useGetTournament(1)
const { data: tournament } = tournamentQuery
</script>

<template>
  <ui-query-block :query="tournamentQuery">
    <template #error="{ errorCode, retry }">
      <div role="alert">
        <p>Could not load tournament ({{ errorCode }}).</p>
        <button type="button" @click="retry">Retry</button>
      </div>
    </template>

    <h2>Tournament info</h2>
    <p>Dates and limits</p>

    <ui-query-field>
      <template #skeleton><ui-skeleton width="120px" /></template>
      <span>{{ tournament?.start_date ?? '-' }}</span>
    </ui-query-field>

    <ui-query-field>
      <template #skeleton><ui-skeleton width="40px" /></template>
      <span>{{ tournament?.participants_count ?? '-' }}</span>
    </ui-query-field>
  </ui-query-block>
</template>
```

Fields inherit loading and background-fetch state unless `loading` is explicitly supplied. The block `#error` slot is optional; without it, the shared error component and offline message are shown. Empty data is handled by normal consumer template logic.

### Additional requirements

- Existing skeleton, error, error-boundary, and connection-state components SHOULD be reused when they fit.
- Query-state behavior MUST be tested independently of card presentation. Tests SHOULD cover default-slot rendering during initial loading, explicit and inherited field loading, initial errors, retry, offline handling, background refetch, nested context isolation, and opacity restoration.
- Existing `UiSkeletonLoader` usages SHOULD be migrated when they represent query state. Components MUST NOT be mechanically wrapped when they do not need query-state handling.
- `UiQueryBlock` and `UiQueryField` are not globally registered; each single-file component MUST import the components it uses.
- A disabled query stays pending forever. Guard it with `v-if` or a matching `enabled` computed rather than mounting its `UiQueryBlock` while disabled.
- Query lifecycle interpretation MUST NOT be duplicated in other composables. A composable MAY expose the query object, but `useQueryState` remains the shared lifecycle logic.
- Page and feature code MUST use `UiQueryBlock` and `UiQueryField` for query-state UI.

## FE-009 Forms and Validation

Form schemas, defaults, and payload mappings SHOULD be shared when create and edit flows genuinely have the same behavior.

- Create and edit forms SHOULD NOT be unified if their behavior or validation requirements meaningfully differ.
- Duplicated payload mapping SHOULD be consolidated when both flows map the same fields with the same semantics.
- Existing project utilities for form state and validation SHOULD be preferred when they fit the use case.
- Validation schemas MUST NOT be shared only because they have similar fields if their actual constraints or semantics differ.
- API-specific types generated in `src/api/` MUST NOT be manually extended or edited to accommodate custom form behavior. Custom form types belong outside the generated directory.

## FE-010 Shared UI Components

Components in `shared/ui/` SHOULD be generic, presentational primitives.

- Shared UI primitives MUST NOT perform API fetching or contain feature-specific business rules.
- Feature-specific composite components SHOULD remain in their feature unless genuinely reused across features with the same behavior and responsibility.
- Shared components SHOULD expose clear props, events, and slots rather than depending on feature stores or feature internals.
- The existing shared UI convention of a component, barrel export, Storybook story, and test SHOULD be preserved for new or substantially changed primitives, consistent with the project's setup.
- Shared UI components MUST NOT import from `features/`.

## FE-011 Modal Components

Modal dialogs SHOULD be extracted into separate Vue components rather than being declared directly inside page templates. This applies even to simple modals when extraction keeps page templates clean and improves separation of responsibilities.

- Modal components SHOULD encapsulate their own content and modal-specific behavior.
- Modal components MAY use controlled or uncontrolled visibility, depending on the use case.
- Controlled visibility SHOULD be used when the parent needs to coordinate modal visibility with external state or behavior.
- Uncontrolled visibility SHOULD be used when the modal can manage its visibility independently.
- Modal components SHOULD be located near the page or feature that owns them.
- A dedicated `modals/` directory MAY be used when it improves organization. It MUST NOT be mandatory.
- The generic `UiModal` primitive MUST remain generic and MUST NOT contain feature-specific content or business logic.

**Examples**

A page should render a dedicated modal component rather than include all modal content inline:

```vue
<template>
  <TournamentList />
  <CreateTournamentModal ref="createModal" />
</template>
```

An uncontrolled feature modal MAY expose `open()` and `close()` for its owning page to invoke. A controlled modal MAY instead receive visibility via `v-model` when external coordination is needed. Neither approach is mandatory for every modal.

## FE-012 Testing

Tests SHOULD focus on behavior and meaningful risk, not simply line or component count.

- Pure utilities in shared libraries MUST have tests for relevant behavior and edge cases.
- Shared composables MUST have tests for their meaningful reactive behavior.
- Shared UI primitives SHOULD have corresponding tests and Storybook stories, following the project's established convention.
- Feature tests SHOULD prioritize business logic, composables with meaningful behavior, critical user workflows, and areas with known regressions.
- Simple presentational components MUST NOT require tests solely because a file exists; test them when their behavior or risk warrants it.
- Bug fixes SHOULD include regression tests when practical.
- Tests SHOULD verify observable behavior rather than implementation details.

## FE-013 TypeScript and General Code Quality

- Types SHOULD describe actual domain and API contracts rather than conceal uncertainty through broad assertions.
- Type assertions MUST NOT be used to silence errors without a justified reason.
- Unused code, imports, props, and styles SHOULD be removed.
- Environment-specific configuration MUST be read from the appropriate configuration source rather than duplicated as literals throughout components.
- Duplicated helpers SHOULD be consolidated only when they have the same semantics.
- Developers SHOULD prefer straightforward code over speculative abstractions.

## FE-014 ESLint Architecture Enforcement

Feature boundaries MUST be enforced by ESLint through the `arch/feature-boundaries` rule.

- Developers MUST fix reported boundary violations rather than disabling or suppressing the rule.
- The rule MUST allow imports within the same feature and MUST reject imports that violate the configured dependency boundaries.
- The rule MUST prevent `shared/` code from depending on `features/`.
- The application shell (`src/router/`, `src/App.vue`, and `src/main.ts`) MAY compose features. Route entry points are explicitly allowed by the current configuration.
- When ESLint reports a violation, developers SHOULD resolve it by moving genuinely shared code to `shared/`, keeping feature-specific code within its owning feature, or adjusting the dependency structure.

**Examples**

Forbidden: feature-to-feature implementation import.

```ts
import EditorModal from '@/features/tournaments/components/EditorModal.vue'
```

Forbidden: a shared module depending on a feature.

```ts
// shared/composables/useSomething.ts
import { useProfile } from '@/features/profile/composables/useProfile'
```

The `arch/feature-boundaries` rule checks imports and re-exports. Route entry points matching `@/features/<feature>/routes` are allowed anywhere by the current implementation. If this exception is broader than intended, the rule SHOULD be updated to limit it to application-shell files.

## FE-015 No Hardcoded Environment-Specific URLs in Vue Components

Vue components MUST NOT contain hardcoded absolute URLs using `localhost` or `127.0.0.1`.

- Components MUST use the configured API base URL through the shared API helper instead of embedding environment-specific origins.
- ESLint MUST report matching plain string literals and interpolated template literals in `.vue` files.
- The shared API helper MAY define a deliberate fallback for local development. Vue components MUST NOT duplicate that fallback or define their own API origin.

**Examples**

Forbidden:

```ts
const url = 'http://localhost:8000/api/tournaments'
```

Forbidden:

```ts
const url = `http://127.0.0.1:8000/api/tournaments/${id}`
```

Expected: use the shared API helper, which obtains its base URL from `VITE_API_BASE_URL`.

```ts
const url = buildApiUrl(`/api/tournaments/${id}`)
```

## FE-016 Explicitly Avoid

The project MUST NOT require or encourage the following patterns without a concrete reason:

- Maximum line counts as the primary component design rule.
- A composable for every API query, `ref`, `computed`, or event handler.
- A blanket ban on API query hooks inside components.
- Extracting every small duplication into a helper or shared module.
- A mandatory folder structure that creates empty or unnecessary directories.
- Atomic Design as a required organizational system.
- Hand-editing generated files in `src/api/`.
- Putting modal markup directly in page templates when a dedicated modal component would keep the page clearer.
- A global abstraction that hides business behavior without reducing meaningful complexity.

## FE-017 Frontend Types and Orval Compatibility

Generated Orval types represent backend API request and response contracts. They MUST remain isolated at the API integration boundary and MUST NOT be used as frontend application types.

The frontend MUST maintain its own types for application models, component props, and feature-level data contracts. API-to-frontend and frontend-to-API transformations MUST be handled explicitly at the integration boundary.

### Frontend-Owned Types

- All frontend application models MUST use frontend-owned types rather than generated Orval types.
- Shared UI components MUST define their own frontend prop types.
- Feature components SHOULD use feature-owned types describing only the data they actually need.
- Feature-level models MUST be owned by the feature that uses them.
- Shared frontend types MAY live in `shared/` only when the same contract is genuinely used by multiple features.
- Frontend types MUST describe frontend requirements and MUST NOT automatically mirror complete backend API schemas.
- Developers MUST NOT create separate types for every component automatically. Existing frontend types SHOULD be reused when their semantics match.

### Orval Type Isolation

- Generated Orval types MUST NOT be imported directly into Vue components, feature composables, frontend models, or shared frontend modules.
- Generated Orval types MUST NOT be used directly or indirectly as frontend component prop contracts.
- TypeScript utilities such as `Pick`, `Omit`, and `Partial` MUST NOT be used to derive frontend types from generated Orval schemas.
- Generated Orval types MAY be used only at the API integration boundary, including API request and response handling, validation of compatibility, and data mapping.
- API query and mutation hooks MAY expose generated types internally, but their results MUST be converted into frontend-owned types before being passed into frontend application logic.
- Generated Orval types MUST NOT leak into feature-level business logic or application state.

### API-to-Frontend Mapping

- API responses MUST be mapped into frontend-owned types at the API integration boundary.
- Mapping MUST explicitly select the properties required by the frontend rather than forwarding complete API response objects.
- Mapping SHOULD normalize nullable values, apply frontend defaults, rename fields, and perform other necessary transformations.
- API response changes that affect frontend requirements MUST be addressed in the corresponding mapping function.
- Changes to unrelated API properties MUST NOT require changes to frontend models or components.
- Mapping functions SHOULD be located in the owning feature's API integration layer or another appropriate feature-specific module.
- Mapping MUST NOT be duplicated across multiple consumers. Shared mapping logic SHOULD have one authoritative implementation.

### Frontend-to-API Mapping

- Frontend-owned form and application models MUST remain independent of generated API request types.
- Mapping from frontend models to API request payloads MUST be performed at the API integration boundary.
- Mutation payloads MUST be checked against the generated Orval request types.
- API-specific fields, naming conventions, and serialization requirements MUST NOT leak into frontend form models unnecessarily.

### Type Compatibility and Safety

- TypeScript MUST verify compatibility between mapped frontend data and frontend-owned types.
- TypeScript MUST verify compatibility between mapped request payloads and generated API request types.
- Developers MUST NOT silence type incompatibilities using unjustified type assertions or casts.
- API changes affecting frontend requirements MUST produce errors at the integration boundary rather than propagating generated types throughout the frontend.
- Frontend-owned types MUST NOT depend on generated Orval declarations.

### Examples

**API response mapping**

```ts
// features/news/api/news.mapper.ts
import type { NewsArticleResponse } from '@/api/backendAPINinja.schemas'
import type { NewsCardItem } from '../types'

export function mapNewsArticle(article: NewsArticleResponse): NewsCardItem {
  return {
    id: article.id,
    title: article.title ?? 'Untitled',
  }
}
```

**Frontend-owned type**

```ts
// features/news/types.ts
export interface NewsCardItem {
  id: number
  title: string
}
```

**Using the mapped result**

```ts
const { data: newsResponse } = useListNews()

const newsItems = computed<NewsCardItem[]>(() =>
  (newsResponse.value?.items ?? []).map(mapNewsArticle),
)
```

**Component contract**

```vue
<script setup lang="ts">
import type { NewsCardItem } from '../types'

defineProps<{
  article: NewsCardItem
}>()
</script>
```

**Frontend-to-API mapping**

```ts
import type { UpdateNewsRequest } from '@/api/backendAPINinja.schemas'

interface EditNewsForm {
  title: string
}

function mapEditNewsForm(form: EditNewsForm): UpdateNewsRequest {
  return {
    title: form.title,
  }
}
```

**Mutation**

```ts
updateNews({
  articleId,
  data: mapEditNewsForm(form),
})
```
