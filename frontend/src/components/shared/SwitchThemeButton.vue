<template>
  <ui-button variant="secondary" size="sm" @click="switchTheme">
    <BrushIcon />
  </ui-button>
</template>

<script setup lang="ts">
import BrushIcon from '@/icons/BrushIcon.vue'
import UiButton from '../ui/UiButton.vue'

const getCurrentTheme = () => {
  return document.documentElement.getAttribute('data-theme') || 'light'
}

const switchTheme = () => {
  const currentTheme = getCurrentTheme()

  const newTheme = currentTheme === 'dark' ? 'light' : 'dark'

  document.documentElement.setAttribute('data-theme', newTheme)
  document.documentElement.classList.toggle('dark', newTheme === 'dark')

  localStorage.setItem('theme', newTheme)
}
</script>
