export default function UnderstandingPanel({ understanding }) {
  const isEmpty = Object.keys(understanding).length === 0

  return (
    <div className="w-80 bg-white border-l shadow-lg overflow-y-auto">
      {/* Header */}
      <div className="bg-gray-800 text-white p-4">
        <h2 className="text-lg font-bold">Current Understanding</h2>
        <p className="text-gray-300 text-xs mt-1">Real-time prospect insights</p>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {isEmpty ? (
          <div className="text-gray-500 text-sm text-center py-8">
            <svg
              className="w-12 h-12 mx-auto mb-2 text-gray-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            Start a conversation to see insights
          </div>
        ) : (
          <>
            {understanding.budget_interest && (
              <div className="bg-blue-50 p-3 rounded-lg">
                <div className="text-xs font-semibold text-blue-900 uppercase mb-1">
                  Budget Interest
                </div>
                <div className="text-sm text-blue-800">{understanding.budget_interest}</div>
              </div>
            )}

            {understanding.care_needs && understanding.care_needs.length > 0 && (
              <div className="bg-green-50 p-3 rounded-lg">
                <div className="text-xs font-semibold text-green-900 uppercase mb-1">
                  Care Needs
                </div>
                <div className="flex flex-wrap gap-1">
                  {understanding.care_needs.map((need, index) => (
                    <span
                      key={index}
                      className="inline-block bg-green-200 text-green-800 text-xs px-2 py-1 rounded"
                    >
                      {need}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {understanding.timeline && (
              <div className="bg-yellow-50 p-3 rounded-lg">
                <div className="text-xs font-semibold text-yellow-900 uppercase mb-1">
                  Timeline
                </div>
                <div className="text-sm text-yellow-800">{understanding.timeline}</div>
              </div>
            )}

            {understanding.preferences && understanding.preferences.length > 0 && (
              <div className="bg-purple-50 p-3 rounded-lg">
                <div className="text-xs font-semibold text-purple-900 uppercase mb-1">
                  Preferences
                </div>
                <ul className="text-sm text-purple-800 space-y-1">
                  {understanding.preferences.map((pref, index) => (
                    <li key={index} className="flex items-start">
                      <span className="mr-2">•</span>
                      <span>{pref}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {understanding.tour_interest && (
              <div className="bg-pink-50 p-3 rounded-lg">
                <div className="text-xs font-semibold text-pink-900 uppercase mb-1">
                  Tour Interest
                </div>
                <div className="text-sm text-pink-800">{understanding.tour_interest}</div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
