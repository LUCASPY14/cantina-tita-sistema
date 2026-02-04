/**
 * Tests para utils/formatters.ts
 */

import { describe, it, expect } from 'vitest'

// Funciones de formateo (ejemplo - ajustar según el código real)
function formatCurrency(value: number): string {
  return new Intl.NumberFormat('es-PY', {
    style: 'currency',
    currency: 'PYG',
    minimumFractionDigits: 0
  }).format(value)
}

function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('es-PY').format(d)
}

describe('formatCurrency', () => {
  it('formatea números a guaraníes', () => {
    expect(formatCurrency(5000)).toBe('₲ 5.000')
  })
  
  it('formatea números grandes correctamente', () => {
    expect(formatCurrency(1000000)).toContain('1.000.000')
  })
  
  it('maneja cero', () => {
    expect(formatCurrency(0)).toBe('₲ 0')
  })
  
  it('maneja negativos', () => {
    expect(formatCurrency(-5000)).toContain('-')
  })
})

describe('formatDate', () => {
  it('formatea fechas correctamente', () => {
    const date = new Date('2026-02-03')
    const formatted = formatDate(date)
    
    expect(formatted).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/)
  })
  
  it('maneja strings de fecha', () => {
    const formatted = formatDate('2026-02-03')
    
    expect(formatted).toBeTruthy()
  })
})
