'use client'

import { AnalysisResponse } from '@/lib/api'
import { BarChart3, Activity, AlertTriangle } from 'lucide-react'

interface TechnicalPanelProps {
  analysisData: AnalysisResponse
}

export default function TechnicalPanel({ analysisData }: TechnicalPanelProps) {
  const technical = analysisData.technical
  const airQuality = technical.air_quality || {}
  const riskModel = technical.risk_model

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-100 mb-2">Technical Breakdown</h1>
        <p className="text-gray-400">
          Detailed metrics, thresholds, and confidence indicators
        </p>
        <div className="mt-4 inline-block px-3 py-1 bg-green-500/20 border border-green-500/50 rounded text-xs text-green-400">
          ✅ REAL DATA — Live from Public APIs
        </div>
      </div>

      {/* Risk Model Details */}
      {riskModel && (
        <div className="bg-dark-panel border border-dark-border rounded-xl p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <Activity className="w-5 h-5 text-cyan-400" />
            <h2 className="text-xl font-semibold text-gray-100">Risk Scoring Model</h2>
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-400">Final Risk Score</span>
                <span className="text-2xl font-bold text-gray-100">{riskModel.final_risk_score.toFixed(1)}</span>
              </div>
              <div className="w-full h-4 bg-dark-bg rounded-full overflow-hidden">
                <div
                  className={`h-full ${
                    riskModel.final_risk_score >= 67
                      ? 'bg-red-500'
                      : riskModel.final_risk_score >= 34
                      ? 'bg-yellow-500'
                      : 'bg-green-500'
                  }`}
                  style={{ width: `${riskModel.final_risk_score}%` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-dark-border">
              <div>
                <div className="text-xs text-gray-400 mb-1">Exposure</div>
                <div className="text-lg font-semibold text-gray-200">{riskModel.exposure_score.toFixed(1)}</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">Duration</div>
                <div className="text-lg font-semibold text-gray-200">{riskModel.duration_score.toFixed(1)}</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">Uncertainty</div>
                <div className="text-lg font-semibold text-gray-200">{riskModel.uncertainty_penalty.toFixed(1)}</div>
              </div>
            </div>

            {riskModel.feature_importance && (
              <div className="pt-4 border-t border-dark-border">
                <div className="text-sm text-gray-400 mb-3">Feature Importance</div>
                <div className="space-y-2">
                  {Object.entries(riskModel.feature_importance).map(([feature, importance]) => (
                    <div key={feature} className="flex items-center justify-between">
                      <span className="text-xs text-gray-300 capitalize">{feature}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 bg-dark-bg rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500"
                            style={{ width: `${importance * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-400 w-8 text-right">{(importance * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-4 border-t border-dark-border text-xs text-gray-500">
              Model Version: {riskModel.model_version}
            </div>
          </div>
        </div>
      )}

      {/* Air Quality Technical Data */}
      {Object.keys(airQuality).length > 0 && (
        <div className="bg-dark-panel border border-dark-border rounded-xl p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            <h2 className="text-xl font-semibold text-gray-100">Air Quality Metrics</h2>
          </div>
          <div className="space-y-4">
            {Object.entries(airQuality).map(([pollutant, data]: [string, any]) => (
              <div key={pollutant} className="bg-dark-bg border border-dark-border rounded-lg p-4">
                <div className="flex justify-between items-center mb-3">
                  <span className="text-sm font-semibold text-gray-200 uppercase">{pollutant}</span>
                  <span className="text-lg font-bold text-gray-100">
                    {data.raw_value?.toFixed(2)} {data.unit}
                  </span>
                </div>

                {data.threshold && (
                  <div className="mb-3">
                    <div className="flex justify-between text-xs text-gray-400 mb-1">
                      <span>Threshold ({data.threshold.source})</span>
                      <span>{data.threshold.value} {data.unit}</span>
                    </div>
                    <div className="w-full h-3 bg-dark-border rounded-full overflow-hidden">
                      <div
                        className={`h-full ${
                          data.raw_value > data.threshold.value
                            ? 'bg-red-500'
                            : data.raw_value > data.threshold.value * 0.8
                            ? 'bg-yellow-500'
                            : 'bg-green-500'
                        }`}
                        style={{ width: `${Math.min(100, (data.raw_value / data.threshold.value) * 100)}%` }}
                      />
                    </div>
                  </div>
                )}

                {data.exceedance_factor && data.exceedance_factor > 1 && (
                  <div className="flex items-center gap-2 text-xs text-red-400 mb-2">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Exceeds threshold by {(data.exceedance_factor - 1) * 100}%</span>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-3 pt-3 border-t border-dark-border text-xs">
                  <div>
                    <div className="text-gray-400 mb-1">Data Source</div>
                    <div className="text-gray-300">{data.data_source}</div>
                  </div>
                  {data.spatial_resolution_km && (
                    <div>
                      <div className="text-gray-400 mb-1">Resolution</div>
                      <div className="text-gray-300">{data.spatial_resolution_km} km</div>
                    </div>
                  )}
                  {data.spatial_coverage && (
                    <div>
                      <div className="text-gray-400 mb-1">Coverage</div>
                      <div className="text-gray-300 capitalize">{data.spatial_coverage}</div>
                    </div>
                  )}
                  {data.measurement_timestamp && (
                    <div>
                      <div className="text-gray-400 mb-1">Timestamp</div>
                      <div className="text-gray-300">
                        {new Date(data.measurement_timestamp).toLocaleString()}
                      </div>
                    </div>
                  )}
                </div>

                {data.uncertainty && (
                  <div className="mt-3 pt-3 border-t border-dark-border text-xs">
                    <div className="text-gray-400 mb-1">Uncertainty</div>
                    <div className="text-gray-300">
                      {JSON.stringify(data.uncertainty, null, 2)}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Model Info */}
      <div className="bg-dark-panel border border-dark-border rounded-xl p-6">
        <h2 className="text-xl font-semibold text-gray-100 mb-4">Model Information</h2>
        <div className="space-y-2 text-sm text-gray-400">
          <div>Version: {analysisData.model_info.risk_model_version}</div>
          <div>Generated: {new Date(analysisData.model_info.timestamp).toLocaleString()}</div>
        </div>
      </div>
    </div>
  )
}
