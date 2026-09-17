<template>
  <ComboboxRoot v-model="value" :multiple="multiple" :disabled="isLoading" class="select-wrapper">
    <ComboboxAnchor as-child>
      <ComboboxTrigger as-child>
        <UiButton
          variant="ghost"
          class="select-trigger"
          :disabled="isLoading"
          data-testid="trigger-wrapper"
        >
          <span class="select-value">
            {{ selectedLabel }}
          </span>

          <LoadingIcon v-if="isLoading" data-testid="loading-icon" />

          <ArrowDown v-else class="select-chevron" data-testid="arrow-icon" />
        </UiButton>
      </ComboboxTrigger>
    </ComboboxAnchor>

    <ComboboxPortal>
      <ComboboxContent
        class="select-dropdown"
        position="popper"
        :side-offset="3"
        :style="{
          zIndex: 9999,
        }"
      >
        <div class="select-search-wrapper">
          <ComboboxInput
            class="select-search"
            placeholder="Search..."
            :disabled="isError || isLoading"
            data-testid="select-search"
          />
        </div>

        <ComboboxViewport class="select-list">
          <div v-if="isError" role="alert" class="select-error">
            {{ error }}
          </div>

          <ComboboxEmpty v-else class="select-empty" data-testid="select-empty">
            No options found
          </ComboboxEmpty>

          <ComboboxItem
            v-for="option in options"
            :key="option.value"
            :value="option.value"
            class="select-option"
          >
            <span>
              {{ option.label }}
            </span>

            <ComboboxItemIndicator>
              <SelectedIcon class="select-check" />
            </ComboboxItemIndicator>
          </ComboboxItem>
        </ComboboxViewport>
      </ComboboxContent>
    </ComboboxPortal>
  </ComboboxRoot>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  ComboboxAnchor,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxInput,
  ComboboxItem,
  ComboboxItemIndicator,
  ComboboxPortal,
  ComboboxRoot,
  ComboboxTrigger,
  ComboboxViewport,
} from 'reka-ui'

import UiButton from './UiButton.vue'
import ArrowDown from '@/icons/ArrowDown.vue'
import SelectedIcon from '@/icons/SelectedIcon.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'

export type SelectOptionValue = string | number

export interface SelectOption {
  value: SelectOptionValue
  label: string
}

type Props = {
  multiple?: boolean
  modelValue: SelectOptionValue | SelectOptionValue[] | null
  options?: SelectOption[]
  placeholder?: string
  isLoading?: boolean
  isError?: boolean
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  options: () => [],
  placeholder: 'Select an option',
})

const value = defineModel<SelectOptionValue | SelectOptionValue[] | null>()

const selectedLabel = computed(() => {
  if (props.multiple) {
    const values = Array.isArray(props.modelValue) ? props.modelValue : []

    if (!values.length) {
      return props.placeholder
    }

    const labels = values.map(
      (value) => props.options.find((option) => option.value === value)?.label ?? value,
    )

    return labels.length === 1 ? labels[0] : `${labels[0]} +${labels.length - 1} more`
  }

  const option = props.options.find((option) => option.value === props.modelValue)

  return option?.label ?? props.placeholder
})
</script>

<style scoped>
.select-trigger {
  width: 100%;
}

.select-chevron {
  flex-shrink: 0;
  color: color-mix(in srgb, var(--foreground) 42%, transparent);
  transition: transform 0.2s ease;
}

.select-value {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.select-dropdown) {
  background: var(--popover);
  color: var(--foreground);
  border: 1px solid color-mix(in srgb, var(--border) 40%, transparent);
  border-radius: 12px;
  box-shadow: 0 8px 20px rgb(0 0 0 / 11%);
  overflow: hidden;
}

.select-search-wrapper {
  padding: 0.35rem 0.35rem 0;
}

:deep(.select-search) {
  width: 100%;
  box-sizing: border-box;
  padding: 0.5rem 0.75rem;
  border: 1px solid color-mix(in srgb, var(--border) 40%, transparent);
  border-radius: 8px;
  font: inherit;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  background: var(--secondary);
  color: inherit;
  outline: none;
  transition: border-color 0.15s ease;
}

:deep(.select-search:focus) {
  outline: none;
  box-shadow: 0 0 0 2px var(--ring);
  border-color: color-mix(in srgb, var(--secondary) 80%, white);
}

:deep(.select-search:disabled) {
  cursor: not-allowed;
}

:deep(.select-search::placeholder) {
  color: color-mix(in srgb, var(--foreground) 42%, transparent);
}

:deep(.select-list) {
  list-style: none;
  margin: 0;
  padding: 0.35rem;
  max-height: 220px;
  overflow-y: auto;
  outline: none;
}

:deep(.select-option) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  color: inherit;
  transition: background 0.1s ease;
}

.select-option:hover,
.select-option[data-highlighted] {
  background: color-mix(in srgb, var(--foreground) 5%, transparent);
}

.select-option[data-state='checked'] {
  background: color-mix(in srgb, var(--primary) 12%, transparent);
  color: color-mix(in srgb, var(--primary) 88%, var(--foreground));
  font-weight: 500;
}

.select-option[data-state='checked'][data-highlighted] {
  background: color-mix(in srgb, var(--primary) 18%, transparent);
}

.select-error,
:deep(.select-empty) {
  padding: 0.75rem;
  text-align: center;
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  color: var(--muted-foreground);
}

.select-check {
  flex-shrink: 0;
  color: var(--primary);
}
</style>
```
