'use client'

import { use } from 'react'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import ELI15Panel from '@/components/ELI15Panel'
import TechnicalPanel from '@/components/TechnicalPanel'
import { apiClient, AnalysisResponse } from '@/lib/api'
import { ArrowLeft } from 'lucide-react'

export default function AnalysisPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const router = useRouter()
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Parse location from ID (format: lat-lng-name)
  const [lat, lng, ...nameParts] = id.split('-')
  const locationName = decodeURIComponent(nameParts.join('-'))
  const latitude = parseFloat(lat)
  const longitude = parseFloat(lng)
  
  useEffect(() => {
    const loadAnalysis = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await apiClient.fetchAnalysis(latitude, longitude)
        setAnalysisData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load analysis')
        console.error('Error loading analysis:', err)
      } finally {
        setLoading(false)
      }
    }
    loadAnalysis()
  }, [latitude, longitude])

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-gray-400">Loading analysis...</div>
      </div>
    )
  }

  if (error || !analysisData) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 mb-4">Error: {error || 'Failed to load analysis'}</div>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-bg">
      <div className="sticky top-0 z-50 bg-dark-panel border-b border-dark-border px-6 py-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.back()}
            className="p-2 hover:bg-dark-border rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-xl font-semibold">{locationName}</h1>
            <p className="text-sm text-gray-400">Environmental Safety Analysis</p>
          </div>
          <div className="ml-auto px-3 py-1 bg-green-500/20 border border-green-500/50 rounded text-xs text-green-400">
            ✅ REAL DATA — Live from Public APIs
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-0 min-h-[calc(100vh-80px)]">
        <div className="border-r border-dark-border overflow-y-auto custom-scrollbar">
          <ELI15Panel analysisData={analysisData} />
        </div>
        <div className="overflow-y-auto custom-scrollbar">
          <TechnicalPanel analysisData={analysisData} />
        </div>
      </div>
    </div>
  )
}
