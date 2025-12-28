export type SafetyLevel = 'safe' | 'moderate' | 'unsafe'

export interface LocationData {
  name: string
  lat: number
  lng: number
  safetyLevel: SafetyLevel
  confidence: number
  airPollution: {
    level: number
    trend: 'improving' | 'stable' | 'worsening'
    primarySources: string[]
  }
  waterQuality: {
    score: number
    contaminants: string[]
    status: string
  }
  deforestation: {
    risk: number
    trend: string
    affectedArea: string
  }
  gasPlumes: {
    detected: boolean
    intensity: number
    source: string
  }
  historicalData: {
    date: string
    airPollution: number
    waterQuality: number
  }[]
  predictions: {
    date: string
    airPollution: number
    waterQuality: number
    risk: number
  }[]
}

const cities = [
  { name: 'New York, NY', lat: 40.7128, lng: -74.0060 },
  { name: 'Los Angeles, CA', lat: 34.0522, lng: -118.2437 },
  { name: 'Chicago, IL', lat: 41.8781, lng: -87.6298 },
  { name: 'Houston, TX', lat: 29.7604, lng: -95.3698 },
  { name: 'San Francisco, CA', lat: 37.7749, lng: -122.4194 },
  { name: 'Seattle, WA', lat: 47.6062, lng: -122.3321 },
  { name: 'Boston, MA', lat: 42.3601, lng: -71.0589 },
  { name: 'Miami, FL', lat: 25.7617, lng: -80.1918 },
]

const safetyLevels: SafetyLevel[] = ['safe', 'moderate', 'unsafe']
const trends = ['improving', 'stable', 'worsening'] as const
const sources = ['Industrial emissions', 'Vehicle traffic', 'Construction', 'Wildfires', 'Agricultural activities']

export function generateDemoLocation(lat: number, lng: number, name: string): LocationData {
  // Generate deterministic but varied data based on coordinates
  const seed = Math.floor(lat * 1000 + lng * 1000)
  const safetyLevel = safetyLevels[seed % 3]
  
  const airPollutionLevel = 30 + (seed % 50)
  const waterQualityScore = 60 + (seed % 40)
  const confidence = 70 + (seed % 30)

  // Generate historical data (past 12 months)
  const historicalData = Array.from({ length: 12 }, (_, i) => {
    const month = new Date()
    month.setMonth(month.getMonth() - (11 - i))
    return {
      date: month.toISOString().split('T')[0],
      airPollution: airPollutionLevel + (Math.sin(i / 2) * 15) + (seed % 10),
      waterQuality: waterQualityScore + (Math.cos(i / 3) * 10) + (seed % 10),
    }
  })

  // Generate predictions (next 6 months)
  const predictions = Array.from({ length: 6 }, (_, i) => {
    const month = new Date()
    month.setMonth(month.getMonth() + (i + 1))
    return {
      date: month.toISOString().split('T')[0],
      airPollution: airPollutionLevel + (Math.sin((12 + i) / 2) * 15) + (seed % 10),
      waterQuality: waterQualityScore + (Math.cos((12 + i) / 3) * 10) + (seed % 10),
      risk: 20 + (seed % 40) + (i * 2),
    }
  })

  return {
    name,
    lat,
    lng,
    safetyLevel,
    confidence,
    airPollution: {
      level: airPollutionLevel,
      trend: trends[seed % 3],
      primarySources: sources.slice(0, 2 + (seed % 3)),
    },
    waterQuality: {
      score: waterQualityScore,
      contaminants: seed % 3 === 0 ? ['Heavy metals', 'Nitrates'] : seed % 3 === 1 ? ['Microplastics'] : [],
      status: waterQualityScore > 80 ? 'Excellent' : waterQualityScore > 60 ? 'Good' : 'Fair',
    },
    deforestation: {
      risk: 10 + (seed % 60),
      trend: trends[seed % 3],
      affectedArea: `${(seed % 500 + 50).toFixed(1)} km²`,
    },
    gasPlumes: {
      detected: seed % 3 !== 0,
      intensity: seed % 100,
      source: seed % 2 === 0 ? 'Industrial facility' : 'Natural seeps',
    },
    historicalData,
    predictions,
  }
}

export function getSafetyBadge(safetyLevel: SafetyLevel) {
  switch (safetyLevel) {
    case 'safe':
      return { icon: '✅', label: 'SAFE', color: 'text-safe' }
    case 'moderate':
      return { icon: '⚠️', label: 'MODERATE', color: 'text-moderate' }
    case 'unsafe':
      return { icon: '❌', label: 'UNSAFE', color: 'text-unsafe' }
  }
}

