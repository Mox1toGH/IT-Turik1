<template>
  <ui-button variant="secondary" size="sm" @click="themeStore.toggleTheme">
    <Palette :size="16" />
  </ui-button>
</template>

<script setup lang="ts">
import { Palette } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'
import UiButton from '../ui/UiButton'

const themeStore = useThemeStore()
</script>
