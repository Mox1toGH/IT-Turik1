<template>
  <div class="select-wrapper" :class="{ open: isOpen }" ref="wrapperRef">
    <div
      @click="toggleOpen"
      @keydown="handleTriggerKeydown"
      :aria-expanded="isOpen"
      aria-haspopup="listbox"
      data-testid="trigger-wrapper"
    >
      <slot name="trigger" :selectedLabel="selectedLabel">
        <ui-button variant="ghost" class="select-trigger" :disabled="isLoading">
          <span class="select-value">{{ selectedLabel }}</span>

          <LoadingIcon v-if="isLoading" data-testid="loading-icon" />
          <arrow-down v-else class="select-chevron" data-testid="arrow-icon" />
        </ui-button>
      </slot>
    </div>

    <Transition name="dropdown">
      <div
        v-if="isOpen"
        class=""
        data-testid="select-dropdown"
        :class="['select-dropdown', dropdownPosition, dropdownAlign]"
        :style="{ minWidth: props.minWidth ?? '100%' }"
        ref="dropdownRef"
      >
        <div class="select-search-wrapper">
          <input
            :disabled="isError || isLoading"
            ref="searchInputRef"
            v-model="searchQuery"
            class="select-search"
            data-testid="select-search"
            type="text"
            placeholder="Search..."
            @keydown="handleSearchKeydown"
          />
        </div>

        <ul
          class="select-list"
          role="listbox"
          :aria-multiselectable="multiple"
          :aria-activedescendant="activeDescendant"
          ref="listRef"
          tabindex="-1"
        >
          <li v-if="isError" role="alert" class="select-error">{{ error }}</li>
          <li v-else-if="!filteredOptions.length" data-testid="select-empty" class="select-empty">
            No options found
          </li>
          <li
            v-else
            v-for="(option, index) in filteredOptions"
            :key="option.value"
            :id="`option-${option.value}`"
            class="select-option"
            :class="{
              selected: isSelected(option),
              focused: index === focusedIndex,
            }"
            role="option"
            :aria-selected="isSelected(option)"
            @click.prevent="selectOption(option)"
            @mouseenter="focusedIndex = index"
          >
            {{ option.label }}
            <selected-icon v-if="isSelected(option)" class="select-check" />
          </li>
        </ul>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
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
  height?: number
  minWidth?: string
  alignTo?: 'left' | 'right'
  isLoading?: boolean
  isError?: boolean
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  options: () => [],
  alignTo: 'left',
  placeholder: 'Select an option',
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: SelectOptionValue | SelectOptionValue[]): void
}>()

const isOpen = ref<boolean>(false)
const focusedIndex = ref<number>(-1)
const searchQuery = ref<string>('')
const dropdownPosition = ref<'bottom' | 'top'>('bottom')
const dropdownAlign = computed(() => props.alignTo)
const wrapperRef = ref<HTMLDivElement | null>(null)
const listRef = ref<HTMLUListElement | null>(null)
const searchInputRef = ref<HTMLInputElement | null>(null)

const filteredOptions = computed(() =>
  searchQuery.value.trim()
    ? props.options.filter((option) =>
        option.label.toLowerCase().includes(searchQuery.value.toLowerCase()),
      )
    : props.options,
)

function isSelected(option: SelectOption): boolean {
  if (props.multiple) {
    return (props.modelValue as SelectOptionValue[]).includes(option.value)
  }
  return option.value === props.modelValue
}

const selectedLabel = computed<SelectOptionValue>(() => {
  if (props.multiple) {
    const arr = props.modelValue as SelectOptionValue[]
    if (!arr.length) return props.placeholder
    const labels = arr.map(
      (value) => props.options.find((option) => option.value === value)?.label ?? value,
    )
    return labels.length === 1 ? labels[0]! : `${labels[0]!} +${labels.length - 1} more`
  }
  const found = props.options.find((option) => option.value === props.modelValue)
  return found ? found.label : props.placeholder
})

const activeDescendant = computed<string | undefined>(() => {
  if (focusedIndex.value < 0) return undefined
  const opt = filteredOptions.value[focusedIndex.value]
  return opt ? `option-${opt.value}` : undefined
})

function computeDropdownPosition() {
  if (!wrapperRef.value) return
  const rect = wrapperRef.value.getBoundingClientRect()
  const spaceBelow = window.innerHeight - rect.bottom
  const spaceAbove = rect.top

  const dropdownHeight =
    (listRef.value?.clientHeight ?? 220) + (searchInputRef.value?.clientHeight ?? 40) + 15

  dropdownPosition.value = spaceBelow < dropdownHeight && spaceAbove > spaceBelow ? 'top' : 'bottom'
}

watch(isOpen, async (opened) => {
  if (opened) {
    computeDropdownPosition()
    searchQuery.value = ''
    const selectedIdx = filteredOptions.value.findIndex((option) =>
      props.multiple
        ? (props.modelValue as SelectOptionValue[]).includes(option.value)
        : option.value === props.modelValue,
    )
    focusedIndex.value = selectedIdx >= 0 ? selectedIdx : 0
    await nextTick()
    searchInputRef.value?.focus()
    scrollToFocused()
  } else {
    focusedIndex.value = -1
    searchQuery.value = ''
  }
})

watch(filteredOptions, () => {
  if (searchQuery.value.trim()) {
    focusedIndex.value = 0
  }
})

function toggleOpen() {
  isOpen.value = !isOpen.value
}

function selectOption(option: SelectOption) {
  if (props.multiple) {
    const arr = [...(props.modelValue as SelectOptionValue[])]
    const idx = arr.indexOf(option.value)
    if (idx >= 0) {
      arr.splice(idx, 1)
    } else {
      arr.push(option.value)
    }
    emit('update:modelValue', arr)
  } else {
    emit('update:modelValue', option.value)
    isOpen.value = false
    wrapperRef.value?.querySelector<HTMLElement>('.select-trigger')?.focus()
  }
}

function handleTriggerKeydown(e: KeyboardEvent) {
  switch (e.key) {
    case 'Enter':
    case 'ArrowDown':
    case 'ArrowUp':
      e.preventDefault()
      isOpen.value = true
      break
    case 'Escape':
      isOpen.value = false
      break
  }
}

function handleSearchKeydown(e: KeyboardEvent) {
  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault()
      focusedIndex.value = Math.min(focusedIndex.value + 1, filteredOptions.value.length - 1)
      scrollToFocused()
      break
    case 'ArrowUp':
      e.preventDefault()
      focusedIndex.value = Math.max(focusedIndex.value - 1, 0)
      scrollToFocused()
      break
    case 'Enter':
      e.preventDefault()
      if (focusedIndex.value >= 0 && filteredOptions.value[focusedIndex.value]) {
        selectOption(filteredOptions.value[focusedIndex.value]!)
      }
      break
    case 'Escape':
    case 'Tab':
      e.preventDefault()
      isOpen.value = false
      wrapperRef.value?.querySelector<HTMLElement>('.select-trigger')?.focus()
      break
  }
}

function scrollToFocused() {
  nextTick(() => {
    const list = listRef.value
    if (!list) return
    const focused = list.children[focusedIndex.value] as HTMLElement | undefined
    if (!focused) return

    const listPadding = parseFloat(getComputedStyle(list).paddingBottom)
    const itemBottom = focused.offsetTop + focused.offsetHeight
    const visibleBottom = list.scrollTop + list.clientHeight

    if (itemBottom + listPadding > visibleBottom) {
      list.scrollTop = itemBottom + listPadding - list.clientHeight
    }

    const listPaddingTop = parseFloat(getComputedStyle(list).paddingTop)
    if (focused.offsetTop - listPaddingTop < list.scrollTop) {
      list.scrollTop = focused.offsetTop - listPaddingTop
    }
  })
}

function handleOutsideClick(e: MouseEvent) {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', handleOutsideClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', handleOutsideClick))
</script>

<style scoped>
.select-wrapper {
  position: relative;
  display: inline-block;
}

.select-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  cursor: pointer;
  color: inherit;
  text-align: left;
}

.select-chevron {
  flex-shrink: 0;
  color: color-mix(in srgb, var(--foreground) 42%, transparent);
  transition: transform 0.2s ease;
}

.select-wrapper.open .select-chevron {
  transform: rotate(180deg);
}

.select-value {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.select-dropdown {
  position: absolute;
  z-index: 50;
  background: var(--popover);
  color: var(--foreground);
  border: 1px solid color-mix(in srgb, var(--border) 40%, transparent);
  border-radius: 12px;
  box-shadow: 0 8px 20px rgb(0 0 0 / 11%);
  overflow: hidden;
}

.select-dropdown.bottom {
  top: calc(100% + 3px);
}

.select-dropdown.top {
  bottom: calc(100% + 3px);
}

.select-dropdown.left {
  left: 0;
}

.select-dropdown.right {
  right: 0;
}

.select-search-wrapper {
  padding: 0.35rem 0.35rem 0;
}

.select-search {
  width: 100%;
  box-sizing: border-box;
  padding: 0.5rem 0.75rem;
  border: 1px solid color-mix(in srgb, var(--border) 40%, transparent);
  border-radius: 8px;
  font: inherit;
  font-size: 0.875rem;
  background: transparent;
  color: inherit;
  outline: none;
  transition: border-color 0.15s ease;
}

.select-search:focus {
  border-color: var(--primary);
}

.select-search:disabled {
  cursor: not-allowed;
}

.select-search::placeholder {
  color: color-mix(in srgb, var(--foreground) 42%, transparent);
}

.select-list {
  list-style: none;
  margin: 0;
  padding: 0.35rem;
  max-height: 220px;
  overflow-y: auto;
  outline: none;
}

.select-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
  color: inherit;
  transition: background 0.1s ease;
}

.select-option:hover,
.select-option.focused {
  background: color-mix(in srgb, var(--foreground) 5%, transparent);
}

.select-option.selected {
  background: color-mix(in srgb, var(--primary) 12%, transparent);
  color: color-mix(in srgb, var(--primary) 88%, var(--foreground));
  font-weight: 500;
}

.select-option.selected.focused {
  background: color-mix(in srgb, var(--primary) 18%, transparent);
}

.select-error,
.select-empty {
  padding: 0.75rem;
  text-align: center;
  font-size: 0.875rem;
  color: var(--muted-foreground);
}

.select-check {
  flex-shrink: 0;
  color: var(--primary);
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
}
</style>
