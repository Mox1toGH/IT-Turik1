import { defineConfig } from 'orval'

export default defineConfig({
  api: {
    input: '../backend/schema.yml',
    output: {
      mode: 'tags-split',
      target: './src/api',
      formatter: 'prettier',
      generateErrorTypes: true,
      httpClient: 'axios',
      client: 'vue-query',
      clean: false,
      baseUrl: 'http://localhost:8000',
      override: {
        mutator: {
          path: './src/lib/apiClient.ts',
          name: 'customInstance',
        },
      },
    },
  },
})
