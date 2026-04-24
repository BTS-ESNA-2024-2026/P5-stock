import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    // In CI (GitHub Actions sets CI=true automatically):
    //   - 'github-actions' emits ::error:: annotations on failing tests
    //   - 'vitest-ctrf-reporter' writes ctrf/ctrf-report.json for the PR comment
    reporters: process.env.CI
      ? ['verbose', 'github-actions', ['vitest-ctrf-json-reporter', {}]]
      : ['verbose'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov', 'html'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: [
        'src/main.tsx',
        'src/test/**',
        'src/**/*.d.ts',
      ],
    },
  },
})
