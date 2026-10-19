import { defineStore } from 'pinia'
import { ref } from 'vue'

export type Theme = 'light' | 'dark'

function readSavedTheme(): Theme {
  return localStorage.getItem('theme') === 'dark' ? 'dark' : 'light'
}

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<Theme>(readSavedTheme())

  function applyTheme(value: Theme) {
    document.documentElement.setAttribute('data-theme', value)
    document.documentElement.classList.toggle('dark', value === 'dark')
  }

  function setTheme(value: Theme) {
    theme.value = value
    localStorage.setItem('theme', value)
    applyTheme(value)
  }

  function toggleTheme() {
    setTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  applyTheme(theme.value)

  return { theme, setTheme, toggleTheme }
})
