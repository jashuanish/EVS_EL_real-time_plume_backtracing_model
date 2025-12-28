'use client'

import dynamic from 'next/dynamic'
import { useState, useEffect } from 'react'
import LeftToolbar from '@/components/LeftToolbar'
import RightPanel from '@/components/RightPanel'
import LocationBottomSheet from '@/components/LocationBottomSheet'
import { apiClient, LocationResponse } from '@/lib/api'

// Dynamically import map component to avoid SSR issues with Leaflet
const MapComponent = dynamic(() => import('@/components/MapComponent'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-screen bg-dark-bg flex items-center justify-center">
      <div className="text-gray-400">Loading map...</div>
    </div>
  ),
})

export default function Home() {
  const [selectedLocation, setSelectedLocation] = useState<{
    lat: number
    lng: number
    name: string
  } | null>(null)
  const [activeLayers, setActiveLayers] = useState<Set<string>>(new Set())
  const [timePosition, setTimePosition] = useState<'past' | 'present' | 'future'>('present')
  const [isBottomSheetOpen, setIsBottomSheetOpen] = useState(false)
  const [locationData, setLocationData] = useState<LocationResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [mapCenter, setMapCenter] = useState<[number, number]>([12.9716, 77.5946]) // Default: Bangalore

  // Request geolocation on mount
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords
          setMapCenter([latitude, longitude])
          loadLocationData(latitude, longitude)
        },
        () => {
          // User denied or error - use default location
          loadLocationData(mapCenter[0], mapCenter[1])
        }
      )
    } else {
      // Geolocation not supported - use default
      loadLocationData(mapCenter[0], mapCenter[1])
    }
  }, [])

  const loadLocationData = async (lat: number, lng: number) => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.fetchLocation(lat, lng)
      setLocationData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load location data')
      console.error('Error loading location data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleLocationClick = async (lat: number, lng: number, name: string) => {
    setSelectedLocation({ lat, lng, name })
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.fetchLocation(lat, lng)
      setLocationData(data)
      setIsBottomSheetOpen(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load location data')
      console.error('Error loading location data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleLayerToggle = (layer: string) => {
    const newLayers = new Set(activeLayers)
    if (newLayers.has(layer)) {
      newLayers.delete(layer)
    } else {
      newLayers.add(layer)
    }
    setActiveLayers(newLayers)
  }

  return (
    <main className="relative w-full h-screen overflow-hidden">
      <div className="absolute top-0 left-0 right-0 z-30 p-4">
        <div className="max-w-2xl mx-auto">
          <div className="bg-dark-panel border border-dark-border rounded-lg shadow-2xl p-3">
            <input
              type="text"
              placeholder="Search locations..."
              className="w-full bg-transparent text-gray-100 placeholder-gray-400 outline-none text-lg"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="absolute top-20 left-1/2 transform -translate-x-1/2 z-40 bg-red-500/20 border border-red-500 rounded-lg px-4 py-2 text-red-400 text-sm">
          {error} - Using placeholder data
        </div>
      )}

      <LeftToolbar
        activeLayers={activeLayers}
        onLayerToggle={handleLayerToggle}
        timePosition={timePosition}
        onTimeChange={setTimePosition}
      />

      <MapComponent
        onLocationClick={handleLocationClick}
        activeLayers={activeLayers}
        timePosition={timePosition}
        center={mapCenter}
      />

      {locationData && (
        <>
          <RightPanel locationData={locationData} loading={loading} />
          <LocationBottomSheet
            isOpen={isBottomSheetOpen}
            onClose={() => setIsBottomSheetOpen(false)}
            locationData={locationData}
          />
        </>
      )}
    </main>
  )
}
