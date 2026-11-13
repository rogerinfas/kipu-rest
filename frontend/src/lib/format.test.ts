import { describe, expect, it } from 'vitest'
import { fmtClock } from './format'

describe('fmtClock', () => {
  it('formats minutes and seconds', () => {
    expect(fmtClock(0)).toBe('00:00')
    expect(fmtClock(860)).toBe('14:20')
  })
  it('adds hours from 3600 s', () => {
    expect(fmtClock(3725)).toBe('01:02:05')
  })
  it('clamps negatives', () => {
    expect(fmtClock(-5)).toBe('00:00')
  })
})
