<template>
  <svg
    v-if="props.isCrossed"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path
      d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-5 0-9.27-3.11-11-8 1.07-2.99 3.16-5.42 5.74-6.88"
    />
    <path d="M1 1l22 22" />
    <path d="M9.9 4.24A10.5 10.5 0 0 1 12 4c5 0 9.27 3.11 11 8a11.54 11.54 0 0 1-4.17 5.94" />
    <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24" />
  </svg>
  <svg
    v-else
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
</template>

<script setup lang="ts">
interface Props {
  isCrossed?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  isCrossed: false,
})
</script>
