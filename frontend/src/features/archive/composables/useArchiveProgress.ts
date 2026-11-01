import { computed, ref } from 'vue'

const STORAGE_KEY = 'found-archive-progress'
type StoredArchiveProgress = { visitedFolders: string[]; photosUnlocked: boolean }

function readProgress(): StoredArchiveProgress {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored) as Partial<StoredArchiveProgress>

      if (Array.isArray(parsed.visitedFolders)) {
        return {
          visitedFolders: parsed.visitedFolders.filter(
            (id): id is string => typeof id === 'string',
          ),
          photosUnlocked: parsed.visitedFolders.length >= 3,
        }
      }
    }
  } catch {
    // Progress remains available for this visit if storage is unavailable.
  }
  return { visitedFolders: [], photosUnlocked: false }
}

export function useArchiveProgress() {
  const initial = readProgress()
  const visitedFolders = ref(initial.visitedFolders)
  const photosUnlocked = computed(() => visitedFolders.value.length >= 3)

  function markFolderVisited(folderId: string) {
    if (visitedFolders.value.includes(folderId)) return
    visitedFolders.value = [...visitedFolders.value, folderId]

    const value = { visitedFolders: visitedFolders.value, photosUnlocked: photosUnlocked.value }

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(value))
    } catch {
      // The in-memory progress still works for the current visit.
    }
    window.dispatchEvent(new CustomEvent('found-archive-progress', { detail: value }))
  }

  return { visitedFolders, photosUnlocked, markFolderVisited }
}
