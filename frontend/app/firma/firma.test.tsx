import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import FirmaPage from './[vkn]/page'

vi.mock('next/navigation', () => ({
  notFound: vi.fn(() => { throw new Error('NOT_FOUND') }),
}))

const mockCompany = {
  firma: {
    legal_name: 'ARITES METAL SANAYI VE TICARET LTD. STI.',
    trade_name: 'ARITES METAL',
    company_registration_number: '1234567890',
    foundation_year: 1995,
    primary_phone: '02125551234',
    primary_email: 'info@arites.com.tr',
    website: 'arites.com.tr',
    address: 'Organize Sanayi Bölgesi 1. Cadde No:5',
    city: 'İstanbul',
    province: 'İstanbul',
    country: 'Türkiye',
    zip_code: '34000',
    nace_code: '24.10',
    nace_source: 'sector_default',
    identity_completeness: 85,
    score_version: 'v2.1',
  },
  kimlik_tamligi: '%85',
  tavan: 5000000,
  nace: {
    kod: '24.10',
    etiket: 'Demir ve Çelik Üretimi',
    tahmin_mi: false,
  },
}

describe('FirmaPage SSR', () => {
  beforeEach(() => {
    vi.resetModules()
    global.fetch = vi.fn()
  })

  it('404 when VKN not 10 digits', async () => {
    const { notFound } = await import('next/navigation')
    
    try {
      await FirmaPage({ params: Promise.resolve({ vkn: '123' }) })
    } catch (e) {
      expect(notFound).toHaveBeenCalled()
    }
  })

  it('renders company data when API returns success', async () => {
    ;(global.fetch as vi.Mock).mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockCompany),
    })

    const { container } = render(await FirmaPage({ params: Promise.resolve({ vkn: '1234567890' }) }))

    await waitFor(() => {
      expect(screen.getByText('ARITES METAL SANAYI VE TICARET LTD. STI.')).toBeInTheDocument()
    })

    expect(screen.getByText('ARITES METAL')).toBeInTheDocument()
    expect(screen.getByText('VKN: 1234567890')).toBeInTheDocument()
    expect(screen.getByText('Kuruluş: 1995')).toBeInTheDocument()
    expect(screen.getByText('Kimlik Tamlığı: %85')).toBeInTheDocument()
    expect(screen.getByText('Demir ve Çelik Üretimi')).toBeInTheDocument()
  })

  it('includes JSON-LD Organization schema', async () => {
    ;(global.fetch as vi.Mock).mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockCompany),
    })

    render(await FirmaPage({ params: Promise.resolve({ vkn: '1234567890' }) }))

    await waitFor(() => {
      const script = container.querySelector('script[type="application/ld+json"]')
      expect(script).toBeInTheDocument()
      
      const jsonLd = JSON.parse(script!.textContent!)
      expect(jsonLd['@context']).toBe('https://schema.org')
      expect(jsonLd['@type']).toBe('Organization')
      expect(jsonLd.name).toBe('ARITES METAL SANAYI VE TICARET LTD. STI.')
      expect(jsonLd.alternateName).toBe('ARITES METAL')
      expect(jsonLd.registrationNumber).toBe('1234567890')
      expect(jsonLd.foundingDate).toBe('1995-01-01')
    })
  })

  it('shows not found when API returns 404', async () => {
    const { notFound } = await import('next/navigation')
    ;(global.fetch as vi.Mock).mockResolvedValue({
      ok: false,
      status: 404,
    })

    try {
      await FirmaPage({ params: Promise.resolve({ vkn: '1234567890' }) })
    } catch (e) {
      expect(notFound).toHaveBeenCalled()
    }
  })

  it('shows not found when API fails', async () => {
    const { notFound } = await import('next/navigation')
    ;(global.fetch as vi.Mock).mockRejectedValue(new Error('Network error'))

    try {
      await FirmaPage({ params: Promise.resolve({ vkn: '1234567890' }) })
    } catch (e) {
      expect(notFound).toHaveBeenCalled()
    }
  })
})

const { container } = { container: document.body }