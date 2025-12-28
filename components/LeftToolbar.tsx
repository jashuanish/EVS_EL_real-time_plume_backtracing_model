'use client'

import { motion } from 'framer-motion'
import { Layers, Clock } from 'lucide-react'

interface LeftToolbarProps {
  activeLayers: Set<string>
  onLayerToggle: (layer: string) => void
  timePosition: 'past' | 'present' | 'future'
  onTimeChange: (position: 'past' | 'present' | 'future') => void
}

const layers = [
  { id: 'Air Pollution', color: 'text-red-400' },
  { id: 'Water Quality', color: 'text-blue-400' },
  { id: 'Deforestation', color: 'text-purple-400' },
  { id: 'Gas Plumes', color: 'text-orange-400' },
]

export default function LeftToolbar({
  activeLayers,
  onLayerToggle,
  timePosition,
  onTimeChange,
}: LeftToolbarProps) {
  return (
    <motion.div
      initial={{ x: -300 }}
      animate={{ x: 0 }}
      className="absolute left-4 top-20 z-30 bg-dark-panel border border-dark-border rounded-lg shadow-2xl p-4 w-64"
    >
      <div className="space-y-6">
        {/* Layers Section */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Layers className="w-4 h-4 text-gray-400" />
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Layers</h3>
          </div>
          <div className="space-y-2">
            {layers.map((layer) => {
              const isActive = activeLayers.has(layer.id)
              return (
                <button
                  key={layer.id}
                  onClick={() => onLayerToggle(layer.id)}
                  className={`w-full flex items-center justify-between p-3 rounded-lg border transition-all ${
                    isActive
                      ? 'bg-dark-border border-gray-500'
                      : 'bg-transparent border-dark-border hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${layer.color.replace('text-', 'bg-')}`} />
                    <span className="text-sm text-gray-200">{layer.id}</span>
                  </div>
                  {isActive && (
                    <div className="w-2 h-2 rounded-full bg-green-400" />
                  )}
                </button>
              )
            })}
          </div>
        </div>

        {/* Time Slider Section */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Clock className="w-4 h-4 text-gray-400" />
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Time</h3>
          </div>
          <div className="space-y-2">
            {(['past', 'present', 'future'] as const).map((position) => {
              const isActive = timePosition === position
              return (
                <button
                  key={position}
                  onClick={() => onTimeChange(position)}
                  className={`w-full text-left p-3 rounded-lg border transition-all capitalize ${
                    isActive
                      ? 'bg-dark-border border-gray-500 text-gray-100'
                      : 'bg-transparent border-dark-border hover:border-gray-600 text-gray-400'
                  }`}
                >
                  <span className="text-sm font-medium">{position}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Demo Indicator */}
        <div className="pt-4 border-t border-dark-border">
          <div className="text-xs text-gray-500 text-center">
            🧪 Demo Preview Mode
          </div>
        </div>
      </div>
    </motion.div>
  )
}

