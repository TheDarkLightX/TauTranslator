import { describe, it, expect } from 'vitest'
import { rankCandidates } from '../src/lib/ranker'

describe('ranker', () => {
  it('ranks existential ex above always for existence prompts', () => {
    const prompt = 'blue elephants exist'
    const ranked = rankCandidates(prompt, [
      { text: 'always ( )', kind: 'snippet' },
      { text: 'ex x ( )', kind: 'snippet' },
      { text: 'all x ( )', kind: 'snippet' },
    ])
    expect(ranked[0].text).toBe('ex x ( )')
    expect(ranked.findIndex(c => c.text.includes('always'))).toBeGreaterThan(0)
  })

  it('ranks all above ex for universal prompts', () => {
    const prompt = 'for all users policy holds'
    const ranked = rankCandidates(prompt, [
      { text: 'ex x ( )', kind: 'snippet' },
      { text: 'all x ( )', kind: 'snippet' },
    ])
    expect(ranked[0].text).toBe('all x ( )')
  })

  it('prefers implication for causal cues', () => {
    const prompt = 'if payment is approved then order is shipped'
    const ranked = rankCandidates(prompt, [
      { text: '(cond) -> (act)', kind: 'snippet' },
      { text: 'ex x ( )', kind: 'snippet' },
    ])
    expect(ranked[0].text).toContain('->')
  })
})


