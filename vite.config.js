import { defineConfig } from 'vite'

export default defineConfig({
  root: '.',
  base: './',
  build: {
    outDir: 'docs_build',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        translator_cm: 'docs/translator_cm.html'
      }
    }
  },
  server: {
    port: 5173,
    strictPort: true
  }
})


