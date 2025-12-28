'use client'

import { motion } from 'framer-motion'
import { LocationResponse } from '@/lib/api'

interface RightPanelProps {
  locationData: LocationResponse
  loading?: boolean
}

function getSafetyBadge(level: string) {
  switch (level) {
    case 'SAFE':
      return { icon: '✅', label: 'SAFE', color: 'text-safe' }
    case 'MODERATE':
      return { icon: '⚠️', label: 'MODERATE', color: 'text-moderate' }
    case 'UNSAFE':
      return { icon: '❌', label: 'UNSAFE', color: 'text-unsafe' }
    default:
      return { icon: '⚠️', label: 'UNKNOWN', color: 'text-gray-400' }
  }
}

export default function RightPanel({ locationData, loading }: RightPanelProps) {
  const badge = getSafetyBadge(locationData.verdict.level)
  const air = locationData.metrics.air || {}
  
  // Get PM2.5 or NO2 as air quality indicator
  const airQualityValue = air.pm25?.value || air.no2?.value || air.so2?.value || null

  return (
    <motion.div
      initial={{ x: 400 }}
      animate={{ x: 0 }}
      className="absolute right-4 top-20 z-30 bg-dark-panel border border-dark-border rounded-lg shadow-2xl w-80 overflow-hidden"
    >
      <div className="p-6 space-y-4">
        {/* Location Name */}
        <div>
          <h2 className="text-lg font-semibold text-gray-100">{locationData.location.name}</h2>
          <p className="text-xs text-gray-400 mt-1">
            {locationData.location.lat.toFixed(4)}, {locationData.location.lng.toFixed(4)}
          </p>
        </div>

        {/* Safety Verdict */}
        <div className="pt-4 border-t border-dark-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs uppercase tracking-wide text-gray-400">Overall Verdict</span>
            <span className="text-xs px-2 py-1 bg-green-500/20 border border-green-500/50 rounded text-green-400">
              REAL DATA
            </span>
          </div>
          <div className={`flex items-center gap-3 mb-3 ${badge.color}`}>
            <span className="text-2xl">{badge.icon}</span>
            <span className="text-xl font-bold">{badge.label}</span>
          </div>

          {/* Confidence Bar */}
          <div>
            <div className="flex justify-between text-xs text-gray-400 mb-1">
              <span>Confidence</span>
              <span>{locationData.verdict.confidence.toFixed(1)}%</span>
            </div>
            <div className="w-full h-2 bg-dark-border rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${locationData.verdict.confidence}%` }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
                className="h-full bg-gradient-to-r from-blue-500 to-cyan-400"
              />
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="pt-4 border-t border-dark-border space-y-3">
          {airQualityValue && (
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Air Quality</span>
              <span className="text-sm font-semibold text-gray-200">
                {airQualityValue.toFixed(1)} {air.pm25?.unit || air.no2?.unit || 'μg/m³'}
              </span>
            </div>
          )}
          {locationData.metrics.water?.quality_score !== undefined && (
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Water Quality</span>
              <span className="text-sm font-semibold text-gray-200">
                {locationData.metrics.water.quality_score}/100
              </span>
            </div>
          )}
          {locationData.metrics.land?.deforestation_risk !== undefined && (
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Deforestation Risk</span>
              <span className="text-sm font-semibold text-gray-200">
                {locationData.metrics.land.deforestation_risk}%
              </span>
            </div>
          )}
        </div>

        {/* Data Timestamp */}
        <div className="pt-4 border-t border-dark-border">
          <p className="text-xs text-gray-500">
            Last updated: {new Date(locationData.data_timestamp.air_quality || locationData.timestamp).toLocaleString()}
          </p>
        </div>

        {/* Click instruction */}
        <div className="pt-2 border-t border-dark-border">
          <p className="text-xs text-gray-500 text-center">
            Click anywhere on the map to view detailed analysis
          </p>
        </div>
      </div>
    </motion.div>
  )
}
