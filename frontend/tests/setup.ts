
import { vi } from 'vitest'

// Mock de ofetch usado por useApi
vi.mock('ofetch', () => ({
  ofetch: Object.assign((url, opts) => Promise.resolve({}), {
    create: (opts) => (url, o) => Promise.resolve({})
  })
}))
