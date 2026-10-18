<template>
  <SelectRoot v-model="model" :multiple="multiple" :disabled="isLoading" class="select-wrapper">
    <SelectTrigger as-child>
      <UiButton
        variant="ghost"
        class="select-trigger"
        :disabled="isLoading"
        data-testid="trigger-wrapper"
        :style="{ minWidth: props.minWidth }"
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
            :disabled="option.disabled"
            class="select-option"
          >
            <div class="select-option-main">
              <SelectItemText class="select-option-text">
                {{ option.label }}
              </SelectItemText>

              <ui-hover-card v-if="option.reason" class="select-option-warning">
                <template #trigger>
                  <button
                    type="button"
                    class="select-option-warning-trigger"
                    :aria-label="`Unavailable: ${option.reason}`"
                    @click.stop
                  >
                    <triangle-alert :size="16" aria-hidden="true" />
                  </button>
                </template>
                {{ option.reason }}
              </ui-hover-card>
            </div>

            <SelectItemIndicator class="select-indicator">
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

import UiButton from '../UiButton'
import UiHoverCard from '../UiHoverCard'
import ArrowDown from '@/icons/ArrowDown.vue'
import SelectedIcon from '@/icons/SelectedIcon.vue'
import LoadingIcon from '@/icons/LoadingIcon.vue'
import { TriangleAlert } from 'lucide-vue-next'

type alignPositions = 'start' | 'end' | 'center'

export type SelectOptionValue = string | number

export interface SelectOption {
  value: SelectOptionValue
  label: string
  disabled?: boolean
  reason?: string | null
}

type Props = {
  multiple?: boolean
  options?: SelectOption[]
  placeholder?: string
  isLoading?: boolean
  isError?: boolean
  error?: string
  align?: alignPositions
  minWidth?: string
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
  color: var(--placeholder);
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
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  box-shadow: var(--shadow-overlay);
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

.select-option-text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.select-option-main {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
  gap: 0.5rem;
}

.select-option-warning {
  display: inline-flex;
  flex: 0 0 auto;
}

.select-option-warning-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--warning);
  cursor: help;
}

.select-indicator {
  display: inline-flex;
  flex: 0 0 auto;
}

.select-option:hover,
.select-option[data-highlighted] {
  background: var(--hover);
}

.select-option[data-disabled] {
  color: var(--muted-foreground);
  cursor: not-allowed;
  opacity: 0.72;
}

.select-option[data-state='checked'] {
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: 500;
}

.select-option[data-state='checked'][data-highlighted] {
  background: var(--primary-soft);
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
