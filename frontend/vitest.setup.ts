// Import styles for browser test mode
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import './src/assets/main.css'

import { afterEach } from 'vitest'
import { cleanup } from 'vitest-browser-vue'

// Each render() mounts into document.body and Reka portals render outside
// the mount container, so unmount between tests to keep queries isolated.
afterEach(() => {
  cleanup()
})
