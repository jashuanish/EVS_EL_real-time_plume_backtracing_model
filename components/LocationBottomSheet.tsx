'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { X, ArrowRight } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { LocationResponse } from '@/lib/api'

interface LocationBottomSheetProps {
  isOpen: boolean
  onClose: () => void
  locationData: LocationResponse | null
}

export default function LocationBottomSheet({ isOpen, onClose, locationData }: LocationBottomSheetProps) {
  const router = useRouter()

  if (!locationData) return null

  const handleViewAnalysis = () => {
    const { lat, lng, name } = locationData.location
    const id = `${lat}-${lng}-${encodeURIComponent(name)}`
    router.push(`/analysis/${id}`)
    onClose()
  }

  const air = locationData.metrics.air || {}
  const water = locationData.metrics.water || {}
  const land = locationData.metrics.land || {}

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40"
          />

          {/* Bottom Sheet */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed bottom-0 left-0 right-0 z-50 bg-dark-panel border-t border-dark-border rounded-t-2xl shadow-2xl max-h-[80vh] overflow-hidden"
          >
            {/* Handle */}
            <div className="flex justify-center pt-3 pb-2">
              <div className="w-12 h-1 bg-gray-600 rounded-full" />
            </div>

            <div className="overflow-y-auto custom-scrollbar max-h-[calc(80vh-20px)] px-6 pb-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-100 mb-1">
                    Environmental Safety Summary
                  </h2>
                  <p className="text-sm text-gray-400">{locationData.location.name}</p>
                  <div className="mt-2 inline-block px-3 py-1 bg-green-500/20 border border-green-500/50 rounded text-xs text-green-400">
                    ✅ REAL DATA — Live from Public APIs
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-dark-border rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>

              {/* Verdict */}
              <div className="bg-dark-bg border border-dark-border rounded-lg p-4 mb-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs text-gray-400 mb-1">Risk Score</div>
                    <div className="text-3xl font-bold text-gray-100">{locationData.verdict.risk_score.toFixed(1)}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-400 mb-1">Verdict</div>
                    <div className={`text-2xl font-bold ${
                      locationData.verdict.level === 'SAFE' ? 'text-safe' :
                      locationData.verdict.level === 'MODERATE' ? 'text-moderate' :
                      'text-unsafe'
                    }`}>
                      {locationData.verdict.level}
                    </div>
                  </div>
                </div>
              </div>

              {/* Quick Stats Grid */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                {air.pm25 && (
                  <div className="bg-dark-bg border border-dark-border rounded-lg p-4">
                    <div className="text-xs text-gray-400 mb-1">PM2.5</div>
                    <div className="text-2xl font-bold text-gray-100 mb-2">
                      {air.pm25.value.toFixed(1)} {air.pm25.unit}
                    </div>
                    {air.pm25.threshold && (
                      <div className="text-xs text-gray-400">
                        Limit: {air.pm25.threshold} {air.pm25.unit}
                      </div>
                    )}
                  </div>
                )}

                {air.no2 && (
                  <div className="bg-dark-bg border border-dark-border rounded-lg p-4">
                    <div className="text-xs text-gray-400 mb-1">NO₂</div>
                    <div className="text-2xl font-bold text-gray-100 mb-2">
                      {air.no2.value.toFixed(1)} {air.no2.unit}
                    </div>
                    {air.no2.threshold && (
                      <div className="text-xs text-gray-400">
                        Limit: {air.no2.threshold} {air.no2.unit}
                      </div>
                    )}
                  </div>
                )}

                {air.so2 && (
                  <div className="bg-dark-bg border border-dark-border rounded-lg p-4">
                    <div className="text-xs text-gray-400 mb-1">SO₂</div>
                    <div className="text-2xl font-bold text-gray-100 mb-2">
                      {air.so2.value.toFixed(1)} {air.so2.unit}
                    </div>
                    {air.so2.threshold && (
                      <div className="text-xs text-gray-400">
                        Limit: {air.so2.threshold} {air.so2.unit}
                      </div>
                    )}
                  </div>
                )}

                {water.quality_score !== undefined && (
                  <div className="bg-dark-bg border border-dark-border rounded-lg p-4">
                    <div className="text-xs text-gray-400 mb-1">Water Quality</div>
                    <div className="text-2xl font-bold text-gray-100 mb-2">
                      {water.quality_score}/100
                    </div>
                    {water.status && (
                      <div className="text-xs text-gray-400">{water.status}</div>
                    )}
                  </div>
                )}
              </div>

              {/* Data Sources */}
              <div className="bg-dark-bg border border-dark-border rounded-lg p-4 mb-6">
                <div className="text-sm font-semibold text-gray-200 mb-3">Data Sources</div>
                <div className="space-y-2 text-xs text-gray-400">
                  {locationData.sources.satellite && (
                    <div>🛰️ {locationData.sources.satellite}</div>
                  )}
                  {locationData.sources.ground_sensors && locationData.sources.ground_sensors.length > 0 && (
                    <div>📡 {locationData.sources.ground_sensors.join(', ')}</div>
                  )}
                  {locationData.sources.weather && (
                    <div>🌤️ {locationData.sources.weather}</div>
                  )}
                </div>
              </div>

              {/* Action Button */}
              <button
                onClick={handleViewAnalysis}
                className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold py-4 rounded-lg transition-all flex items-center justify-center gap-2 shadow-lg"
              >
                View Detailed Analysis
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
