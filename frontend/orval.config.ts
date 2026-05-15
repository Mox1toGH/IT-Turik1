import { defineConfig } from 'orval'

const ORVAL_INPUT = process.env.ORVAL_INPUT ?? 'http://localhost:8000/api/schema/'
const ORVAL_BASE_URL = process.env.ORVAL_BASE_URL ?? 'http://localhost:8000'

export default defineConfig({
  api: {
    input: ORVAL_INPUT,
    output: {
      mode: 'tags-split',
      target: './src/api',
      httpClient: 'axios',
      client: 'vue-query',
      clean: true,
      baseUrl: ORVAL_BASE_URL,
      override: {
        mutator: {
          path: './src/lib/apiClient.ts',
          name: 'customInstance',
        },
      },
    },
  },
})
