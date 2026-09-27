<template>
  <SwitchRoot class="visibility-switch" v-model="modelValue">
    <SwitchThumb class="switch-knob" />
  </SwitchRoot>
</template>

<script setup lang="ts">
import { SwitchRoot, SwitchThumb } from 'reka-ui'

const modelValue = defineModel<boolean>()
</script>

<style>
.visibility-switch {
  position: relative;
  display: inline-flex;
  align-items: center;
  width: 3rem;
  height: 1.7rem;
  padding: 0.17rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: color-mix(in srgb, var(--foreground) 15%, transparent);
  cursor: pointer;
  flex-shrink: 0;
  transition: background 180ms ease;
}

.visibility-switch:focus-visible {
  outline: 2px solid var(--brand-500);
  outline-offset: 2px;
}

.visibility-switch[data-state='checked'] {
  background: var(--primary);
}

.switch-knob {
  width: 1.2rem;
  height: 1.2rem;
  border-radius: 999px;
  border: 1px solid white;
  background: white;
  transform: translateX(0);
  transition: transform 180ms ease;
}

.switch-knob[data-state='checked'] {
  transform: translateX(1.3rem);
  border-color: transparent;
  background: var(--primary-foreground);
}
</style>
