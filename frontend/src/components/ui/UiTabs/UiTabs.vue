<template>
  <div class="ui-tabs">
    <TabsRoot
      v-model="active"
      :unmount-on-hide="false"
      orientation="horizontal"
      class="ui-tabs__root"
    >
      <div class="ui-tabs__bar" :class="{ 'ui-tabs__bar--sticky': sticky }">
        <TabsList class="ui-tabs__list" aria-label="Sections">
          <TabsTrigger
            v-for="item in items"
            :key="item.value"
            :value="item.value"
            :disabled="item.disabled"
            class="ui-tabs__trigger"
          >
            <slot :name="`label-${item.value}`">
              <span class="ui-tabs__label">{{ item.label }}</span>
              <span v-if="item.count !== undefined" class="ui-tabs__count">{{
                item.count
              }}</span>
            </slot>
          </TabsTrigger>
        </TabsList>
        <div v-if="$slots.trailing" class="ui-tabs__trailing">
          <slot name="trailing" />
        </div>
      </div>

      <TabsContent
        v-for="item in items"
        :key="item.value"
        :value="item.value"
        class="ui-tabs__panel"
      >
        <slot v-if="isVisited(item.value)" :name="item.value" />
      </TabsContent>
    </TabsRoot>
  </div>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance, ref, watch } from 'vue'
import { TabsContent, TabsList, TabsRoot, TabsTrigger } from 'reka-ui'
import { routerKey, useRoute, useRouter } from 'vue-router'

export interface TabItem {
  value: string
  label: string
  disabled?: boolean
  count?: number
}

interface Props {
  items: TabItem[]
  queryKey?: string | null
  lazy?: boolean
  sticky?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  queryKey: 'tab',
  lazy: true,
  sticky: false,
})

const model = defineModel<string>({ default: undefined })

const fallbackValue = computed(() => {
  const firstEnabled = props.items.find((item) => !item.disabled)
  return (firstEnabled ?? props.items[0])?.value ?? ''
})

const isValidValue = (value: unknown): value is string =>
  typeof value === 'string' && props.items.some((item) => item.value === value)

// Router sync is optional: without a router (e.g. Storybook) the tabs stay uncontrolled.
const instance = getCurrentInstance()
const hasRouter = !!instance && routerKey in instance.appContext.provides
const router = hasRouter ? useRouter() : null
const route = hasRouter ? useRoute() : null

const queryEnabled = computed(() => !!props.queryKey && !!router && !!route)

const internalValue = ref<string | undefined>(undefined)

const readQuery = (): string | undefined => {
  if (!queryEnabled.value || !route || !props.queryKey) return undefined
  const raw = route.query[props.queryKey]
  const value = Array.isArray(raw) ? raw[0] : raw
  return isValidValue(value) ? value : undefined
}

const active = computed<string>({
  get: () => {
    if (model.value !== undefined) {
      return isValidValue(model.value) ? model.value : fallbackValue.value
    }
    if (internalValue.value !== undefined) return internalValue.value
    return fallbackValue.value
  },
  set: (value: string) => {
    if (!isValidValue(value)) return
    internalValue.value = value
    model.value = value
    if (queryEnabled.value && router && route && props.queryKey) {
      const current = readQuery()
      if (current !== value) {
        void router.replace({ query: { ...route.query, [props.queryKey]: value } })
      }
    }
  },
})

// Initial value from the URL wins over the default tab.
const initialQuery = readQuery()
if (initialQuery !== undefined) {
  internalValue.value = initialQuery
  model.value = initialQuery
}

const visited = ref<Set<string>>(new Set([active.value]))

const isVisited = (value: string) => !props.lazy || visited.value.has(value)

watch(active, (value) => {
  if (!visited.value.has(value)) visited.value = new Set([...visited.value, value])
})

if (queryEnabled.value && route && props.queryKey) {
  const key = props.queryKey
  watch(
    () => route.query[key],
    (raw) => {
      const value = Array.isArray(raw) ? raw[0] : raw
      if (isValidValue(value) && value !== active.value) {
        internalValue.value = value
        model.value = value
      }
    },
  )
}
</script>

<style scoped>
.ui-tabs {
  min-width: 0;
}

.ui-tabs__bar {
  display: flex;
  align-items: stretch;
  gap: 0.75rem;
  border-bottom: 1px solid var(--border);
}

.ui-tabs__bar--sticky {
  position: sticky;
  top: var(--nav-offset);
  z-index: 5;
  background: var(--background);
}

.ui-tabs__list {
  display: flex;
  align-items: stretch;
  gap: 0.25rem;
  flex: 1 1 auto;
  min-width: 0;
  overflow-x: auto;
  scrollbar-width: none;
}

.ui-tabs__list::-webkit-scrollbar {
  display: none;
}

.ui-tabs__trigger {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  flex: 0 0 auto;
  min-height: 40px;
  padding: 0.55rem 0.8rem;
  border: 0;
  background: transparent;
  color: var(--muted-foreground);
  font: inherit;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
  transition: color 0.15s ease;
}

.ui-tabs__trigger:hover {
  color: var(--foreground);
}

.ui-tabs__trigger:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: -2px;
}

.ui-tabs__trigger[data-state='active'] {
  color: var(--foreground);
}

.ui-tabs__trigger[data-state='active']::after {
  content: '';
  position: absolute;
  left: 0.4rem;
  right: 0.4rem;
  bottom: -1px;
  height: 2px;
  border-radius: 2px;
  background: var(--foreground);
}

.ui-tabs__trigger[data-disabled] {
  opacity: 0.45;
  cursor: not-allowed;
}

.ui-tabs__label {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ui-tabs__count {
  color: var(--muted-foreground);
  font-weight: 600;
}

.ui-tabs__trailing {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 0 0 auto;
  padding-bottom: 0.25rem;
}

.ui-tabs__panel {
  min-width: 0;
  padding-top: 1.25rem;
}

.ui-tabs__panel:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
  .ui-tabs__trigger {
    transition: none;
  }
}
</style>
