import { describe, it, expect } from 'vitest'
import { buildRequest } from '../src/lib/request'

describe('buildRequest', () => {
  it('sets temporal_mode to atemporal when clarifier is atemporal', () => {
    const body = buildRequest('blue elephants exist', 'atemporal', '')
    expect(body.temporal_mode).toBe('atemporal')
  })

  it('sets temporal_mode to invariant when clarifier is invariant', () => {
    const body = buildRequest('if a then b', 'invariant', '')
    expect(body.temporal_mode).toBe('invariant')
  })

  it('adds prefer_quantifier when selected', () => {
    const body = buildRequest('forall users ...', 'auto', 'all')
    expect(body.constraints).toBeDefined()
    expect((body.constraints as any).prefer_quantifier).toBe('all')
  })
})


