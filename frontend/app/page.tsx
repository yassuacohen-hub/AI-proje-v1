import Link from 'next/link'

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Huginn Ticari İstihbarat
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Firma künyesi ve ticari istihbarat platformu
        </p>
        <div className="space-y-4">
          <Link
            href="/firma/1234567890"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Örnek Firma Künyesi (VKN: 1234567890)
          </Link>
        </div>
      </div>
    </main>
  )
}