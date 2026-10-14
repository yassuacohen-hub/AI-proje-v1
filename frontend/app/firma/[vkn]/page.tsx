import { Metadata } from 'next'
import { notFound } from 'next/navigation'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

interface NaceInfo {
  kod: string | null
  etiket: string
  tahmin_mi: boolean
}

interface FirmaResponse {
  firma: {
    legal_name: string
    trade_name: string
    company_registration_number: string | null
    foundation_year: number | null
    primary_phone: string | null
    primary_email: string | null
    website: string | null
    address: string | null
    city: string | null
    province: string | null
    country: string
    zip_code: string | null
    nace_code: string | null
    nace_source: string | null
    identity_completeness: number | null
    score_version: string | null
  }
  kimlik_tamligi: string
  tavan: number
  nace: NaceInfo
}

interface JsonLdOrganization {
  '@context': 'https://schema.org'
  '@type': 'Organization'
  name: string
  alternateName?: string
  registrationNumber?: string
  foundingDate?: string
  address?: {
    '@type': 'PostalAddress'
    streetAddress?: string
    addressLocality?: string
    addressRegion?: string
    postalCode?: string
    addressCountry?: string
  }
  telephone?: string
  email?: string
  url?: string
  naics?: string
  description?: string
}

async function fetchCompany(vkn: string): Promise<FirmaResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/v1/companies/${vkn}`, {
      headers: {
        'Accept': 'application/json',
        'X-Source': 'huginn-frontend-ssr',
      },
      cache: 'no-store',
    })

    if (res.status === 404) {
      return null
    }

    if (!res.ok) {
      console.error(`API error: ${res.status} ${res.statusText}`)
      return null
    }

    return await res.json()
  } catch (error) {
    console.error('Fetch error:', error)
    return null
  }
}

function generateJsonLd(firma: FirmaResponse['firma'], nace: FirmaResponse['nace']): JsonLdOrganization {
  const jsonLd: JsonLdOrganization = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: firma.legal_name || '',
  }

  if (firma.trade_name && firma.trade_name !== firma.legal_name) {
    jsonLd.alternateName = firma.trade_name
  }

  if (firma.company_registration_number) {
    jsonLd.registrationNumber = firma.company_registration_number
  }

  if (firma.foundation_year) {
    jsonLd.foundingDate = `${firma.foundation_year}-01-01`
  }

  const addressParts: Omit<NonNullable<JsonLdOrganization['address']>, '@type'> = {}
  if (firma.address) addressParts.streetAddress = firma.address
  if (firma.city) addressParts.addressLocality = firma.city
  if (firma.province) addressParts.addressRegion = firma.province
  if (firma.zip_code) addressParts.postalCode = firma.zip_code
  if (firma.country) addressParts.addressCountry = firma.country
  if (Object.keys(addressParts).length > 0) {
    jsonLd.address = {
      '@type': 'PostalAddress',
      ...addressParts,
    }
  }

  if (firma.primary_phone) {
    jsonLd.telephone = firma.primary_phone
  }

  if (firma.primary_email) {
    jsonLd.email = firma.primary_email
  }

  if (firma.website) {
    jsonLd.url = firma.website.startsWith('http') ? firma.website : `https://${firma.website}`
  }

  if (firma.nace_code) {
    jsonLd.naics = firma.nace_code
  }

  const descParts: string[] = []
  if (nace && nace.etiket) {
    descParts.push(`Sektör: ${nace.etiket}`)
  }
  if (firma.identity_completeness !== null) {
    descParts.push(`Kimlik Tamlığı: %${firma.identity_completeness}`)
  }
  if (descParts.length > 0) {
    jsonLd.description = descParts.join(' | ')
  }

  return jsonLd
}

function CompanyCard({ firma, kimlik_tamligi, tavan, nace }: FirmaResponse) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(generateJsonLd(firma, nace)) }}
      />

      <header className="mb-6 pb-4 border-b border-gray-200">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
          {firma.legal_name}
        </h1>
        {firma.trade_name && firma.trade_name !== firma.legal_name && (
          <p className="text-lg text-gray-600">Tabela: <span className="font-medium">{firma.trade_name}</span></p>
        )}
        <div className="flex flex-wrap gap-4 mt-4 text-sm text-gray-500">
          <span>VKN: {firma.company_registration_number || '—'}</span>
          {firma.foundation_year && <span>Kuruluş: {firma.foundation_year}</span>}
          <span>Kimlik Tamlığı: {kimlik_tamligi}</span>
          <span>Tavan: {tavan.toLocaleString('tr-TR')}</span>
        </div>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">İletişim</h2>
          <dl className="space-y-2 text-sm">
            {firma.primary_phone && (
              <div className="flex justify-between">
                <dt className="text-gray-500">Telefon</dt>
                <dd className="font-medium text-gray-900">{firma.primary_phone}</dd>
              </div>
            )}
            {firma.primary_email && (
              <div className="flex justify-between">
                <dt className="text-gray-500">E-posta</dt>
                <dd className="font-medium text-gray-900">{firma.primary_email}</dd>
              </div>
            )}
            {firma.website && (
              <div className="flex justify-between">
                <dt className="text-gray-500">Web</dt>
                <dd className="font-medium text-gray-900">
                  <a href={firma.website.startsWith('http') ? firma.website : `https://${firma.website}`} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    {firma.website}
                  </a>
                </dd>
              </div>
            )}
            {!firma.primary_phone && !firma.primary_email && !firma.website && (
              <p className="text-gray-400">İletişim bilgisi bulunamadı</p>
            )}
          </dl>
        </div>

        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Adres</h2>
          <address className="not-italic text-sm space-y-1">
            {firma.address && <p className="font-medium text-gray-900">{firma.address}</p>}
            {firma.city && firma.province && (
              <p className="text-gray-600">
                {firma.city} / {firma.province}
                {firma.zip_code && ` ${firma.zip_code}`}
              </p>
            )}
            {firma.country && <p className="text-gray-600">{firma.country}</p>}
            {!firma.address && !firma.city && !firma.province && (
              <p className="text-gray-400">Adres bilgisi bulunamadı</p>
            )}
          </address>
        </div>
      </section>

      <section className="mb-6">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Sektör Bilgisi</h2>
        <dl className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <dt className="text-gray-500">NACE Kodu</dt>
            <dd className="font-medium text-gray-900">{nace.kod || '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Sektör Etiketi</dt>
            <dd className="font-medium text-gray-900">{nace.etiket || '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Kaynak</dt>
            <dd className="font-medium text-gray-900">
              {nace.tahmin_mi ? 'Tahmini' : 'Resmi'}
            </dd>
          </div>
        </dl>
      </section>

      <footer className="pt-4 border-t border-gray-200 text-xs text-gray-500">
        <p>Veri kaynağı: Huginn Data Insights API v1</p>
        <p className="mt-1">Bu sayfa sunucu taraflı render edilmiştir (SSR)</p>
      </footer>
    </div>
  )
}

export async function generateMetadata({ params }: { params: Promise<{ vkn: string }> }): Promise<Metadata> {
  const { vkn } = await params
  const data = await fetchCompany(vkn)

  if (!data) {
    return {
      title: 'Firma Bulunamadı',
      robots: 'noindex, nofollow',
    }
  }

  return {
    title: `${data.firma.legal_name} | Huginn Ticari İstihbarat`,
    description: `${data.firma.trade_name || data.firma.legal_name} - VKN: ${vkn} - ${data.nace.etiket || 'Sektör bilgisi yok'}`,
    openGraph: {
      title: data.firma.legal_name,
      description: `${data.firma.trade_name || data.firma.legal_name} firma künyesi`,
      type: 'website',
    },
  }
}

export default async function FirmaPage({ params }: { params: Promise<{ vkn: string }> }) {
  const { vkn } = await params

  if (!/^\d{10}$/.test(vkn)) {
    notFound()
  }

  const data = await fetchCompany(vkn)

  if (!data) {
    notFound()
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <nav className="mb-6 text-sm text-gray-500" aria-label="Breadcrumb">
          <ol className="flex items-center gap-2">
            <li><a href="/" className="hover:text-gray-700">Ana Sayfa</a></li>
            <li aria-hidden="true">/</li>
            <li><a href="/firma" className="hover:text-gray-700">Firmalar</a></li>
            <li aria-hidden="true">/</li>
            <li aria-current="page" className="text-gray-900 font-medium">{vkn}</li>
          </ol>
        </nav>

        <CompanyCard {...data} />
      </div>
    </div>
  )
}