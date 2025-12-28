'use client'

import { AnalysisResponse } from '@/lib/api'
import { AlertCircle, CheckCircle, XCircle, Droplets, Wind, Trees, Flame } from 'lucide-react'

interface ELI15PanelProps {
  analysisData: AnalysisResponse
}

export default function ELI15Panel({ analysisData }: ELI15PanelProps) {
  const humanReadable = analysisData.human_readable
  const technical = analysisData.technical
  const riskModel = technical.risk_model

  // Determine verdict from risk score
  const riskScore = riskModel?.final_risk_score || 50
  const verdict = riskScore >= 67 ? 'UNSAFE' : riskScore >= 34 ? 'MODERATE' : 'SAFE'

  const badge = {
    SAFE: { icon: <CheckCircle className="w-8 h-8 text-safe" />, color: 'text-safe', label: 'SAFE' },
    MODERATE: { icon: <AlertCircle className="w-8 h-8 text-moderate" />, color: 'text-moderate', label: 'MODERATE' },
    UNSAFE: { icon: <XCircle className="w-8 h-8 text-unsafe" />, color: 'text-unsafe', label: 'UNSAFE' }
  }[verdict]

  const airQuality = technical.air_quality || {}

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-100 mb-2">Explain Like I'm 15</h1>
        <p className="text-gray-400">
          Simple explanations without all the technical jargon
        </p>
        <div className="mt-4 inline-block px-3 py-1 bg-green-500/20 border border-green-500/50 rounded text-xs text-green-400">
          ✅ REAL DATA — Live from Public APIs
        </div>
      </div>

      {/* Overall Verdict */}
      <div className="bg-dark-panel border border-dark-border rounded-xl p-6 mb-8">
        <div className="flex items-center gap-4 mb-4">
          {badge.icon}
          <div>
            <div className="text-sm text-gray-400 uppercase tracking-wide">Overall Verdict</div>
            <div className={`text-2xl font-bold ${badge.color}`}>{badge.label}</div>
          </div>
        </div>
        <p className="text-gray-300 leading-relaxed">
          {humanReadable.summary}
        </p>
      </div>

      {/* Reasons */}
      <div className="bg-dark-panel border border-dark-border rounded-xl p-6 mb-8">
        <h3 className="text-xl font-semibold text-gray-100 mb-4">Why is this the verdict?</h3>
        <ul className="space-y-3">
          {humanReadable.reasons.map((reason, i) => (
            <li key={i} className="flex items-start gap-3">
              <span className="text-blue-400 mt-1">•</span>
              <span className="text-gray-300">{reason}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Recommendations */}
      {humanReadable.recommendations && humanReadable.recommendations.length > 0 && (
        <div className="bg-dark-panel border border-dark-border rounded-xl p-6 mb-8">
          <h3 className="text-xl font-semibold text-gray-100 mb-4">What should you do?</h3>
          <ul className="space-y-3">
            {humanReadable.recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-3">
                <span className="text-green-400 mt-1">✓</span>
                <span className="text-gray-300">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Air Quality Details */}
      {Object.keys(airQuality).length > 0 && (
        <div className="bg-dark-panel border border-dark-border rounded-xl p-6 mb-8">
          <h3 className="text-xl font-semibold text-gray-100 mb-4 flex items-center gap-2">
            <Wind className="w-5 h-5 text-blue-400" />
            Air Quality Details
          </h3>
          <div className="space-y-4">
            {Object.entries(airQuality).map(([pollutant, data]: [string, any]) => (
              <div key={pollutant} className="bg-dark-bg border border-dark-border rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-semibold text-gray-200 uppercase">{pollutant}</span>
                  <span className="text-lg font-bold text-gray-100">
                    {data.raw_value?.toFixed(1)} {data.unit}
                  </span>
                </div>
                {data.threshold && (
                  <div className="text-xs text-gray-400">
                    WHO Limit: {data.threshold.value} {data.unit}
                    {data.exceedance_factor && data.exceedance_factor > 1 && (
                      <span className="text-red-400 ml-2">
                        (Exceeds by {(data.exceedance_factor - 1) * 100}%)
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bottom Note */}
      <div className="mt-8 p-4 bg-dark-panel/50 border border-dark-border rounded-lg">
        <p className="text-sm text-gray-500 text-center">
          This analysis is based on real-time data from public environmental monitoring sources.
          Always verify critical information with local authorities.
        </p>
      </div>
    </div>
  )
}
