<template>
  <ui-button variant="secondary" size="sm" @click="themeStore.toggleTheme">
    <BrushIcon />
  </ui-button>
</template>

<script setup lang="ts">
import BrushIcon from '@/icons/BrushIcon.vue'
import { useThemeStore } from '@/stores/theme'
import UiButton from '../ui/UiButton'

const themeStore = useThemeStore()
</script>
