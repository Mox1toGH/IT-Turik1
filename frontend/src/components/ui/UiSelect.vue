<template>
  <SelectRoot v-model="model" :multiple="multiple" :disabled="isLoading" class="select-wrapper">
    <SelectTrigger as-child>
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
    </SelectTrigger>

    <SelectPortal>
      <SelectContent
        class="select-dropdown"
        position="popper"
        :align="props.align"
        :side-offset="3"
        :style="{
          zIndex: 9999,
          width: 'var(--reka-select-trigger-width)',
          minWidth: 'var(--reka-select-trigger-width)',
        }"
      >
        <SelectViewport class="select-list">
          <div v-if="isError" role="alert" class="select-error">
            {{ error }}
          </div>

          <div v-else-if="!options.length" class="select-empty" data-testid="select-empty">
            No options found
          </div>

          <SelectItem
            v-for="option in options"
            :key="option.value"
            :value="option.value"
            class="select-option"
          >
            <SelectItemText>
              {{ option.label }}
            </SelectItemText>

            <SelectItemIndicator>
              <SelectedIcon class="select-check" />
            </SelectItemIndicator>
          </SelectItem>
        </SelectViewport>
      </SelectContent>
    </SelectPortal>
  </SelectRoot>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  SelectContent,
  SelectItem,
  SelectItemIndicator,
  SelectItemText,
  SelectPortal,
  SelectRoot,
  SelectTrigger,
  SelectViewport,
} from 'reka-ui'

import UiButton from './UiButton.vue'
import ArrowDown from '@/icons/ArrowDown.vue'
import SelectedIcon from '@/icons/SelectedIcon.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'

type alignPositions = 'start' | 'end' | 'center'

export type SelectOptionValue = string | number

export interface SelectOption {
  value: SelectOptionValue
  label: string
}

type Props = {
  multiple?: boolean
  options?: SelectOption[]
  placeholder?: string
  isLoading?: boolean
  isError?: boolean
  error?: string
  align?: alignPositions
}

const props = withDefaults(defineProps<Props>(), {
  options: () => [],
  placeholder: 'Select an option',
  align: 'end',
})

const model = defineModel<SelectOptionValue | SelectOptionValue[] | null>({ default: null })

const selectedLabel = computed(() => {
  if (props.multiple) {
    const values = Array.isArray(model.value) ? model.value : []

    if (!values.length) {
      return props.placeholder
    }

    const labels = values.map(
      (value) => props.options.find((option) => option.value === value)?.label ?? value,
    )

    return labels.length === 1 ? labels[0] : `${labels[0]} +${labels.length - 1} more`
  }

  const option = props.options.find((option) => option.value === model.value)

  return option?.label ?? props.placeholder
})
</script>

<style scoped>
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
  gap: 10px;
  outline: none;
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
.select-empty {
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
