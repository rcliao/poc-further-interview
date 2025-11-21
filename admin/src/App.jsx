import { useState, useEffect } from 'react'
import ProspectsList from './components/ProspectsList'
import ProspectDetail from './components/ProspectDetail'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [prospects, setProspects] = useState([])
  const [selectedProspect, setSelectedProspect] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchProspects()
  }, [])

  const fetchProspects = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/api/admin/prospects`)

      if (!response.ok) {
        throw new Error('Failed to fetch prospects')
      }

      const data = await response.json()
      setProspects(data.prospects)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectProspect = async (prospectId) => {
    try {
      const response = await fetch(`${API_URL}/api/admin/prospects/${prospectId}`)

      if (!response.ok) {
        throw new Error('Failed to fetch prospect details')
      }

      const data = await response.json()
      setSelectedProspect(data)
    } catch (err) {
      console.error('Error fetching prospect details:', err)
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar with prospects list */}
      <div className="w-96 bg-white border-r shadow-sm overflow-y-auto">
        <div className="bg-gray-800 text-white p-4">
          <h1 className="text-xl font-bold">ACME Admin Dashboard</h1>
          <p className="text-gray-300 text-sm mt-1">Prospects & Conversations</p>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : error ? (
          <div className="p-8 text-center text-red-500">{error}</div>
        ) : (
          <ProspectsList
            prospects={prospects}
            selectedProspectId={selectedProspect?.prospect?.prospect_id}
            onSelectProspect={handleSelectProspect}
          />
        )}
      </div>

      {/* Main content area with prospect details */}
      <div className="flex-1 overflow-y-auto">
        {selectedProspect ? (
          <ProspectDetail prospect={selectedProspect} />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <svg
                className="w-16 h-16 mx-auto mb-4 text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
              <p className="text-lg">Select a prospect to view details</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
