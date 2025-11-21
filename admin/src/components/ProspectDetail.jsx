export default function ProspectDetail({ prospect }) {
  const { prospect: info, sessions, enrichment_events } = prospect

  // Get the most recent session's current understanding
  const latestSession = sessions.length > 0 ? sessions[0] : null
  const understanding = latestSession?.current_understanding || {}

  return (
    <div className="p-6">
      {/* Prospect Info Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          {info.first_name || info.last_name
            ? `${info.first_name || ''} ${info.last_name || ''}`.trim()
            : 'Anonymous Prospect'}
        </h2>

        <div className="grid grid-cols-2 gap-4 mb-4">
          {info.email && (
            <div>
              <div className="text-sm text-gray-500">Email</div>
              <div className="text-gray-900">{info.email}</div>
            </div>
          )}
          {info.phone && (
            <div>
              <div className="text-sm text-gray-500">Phone</div>
              <div className="text-gray-900">{info.phone}</div>
            </div>
          )}
          <div>
            <div className="text-sm text-gray-500">Tour Status</div>
            <div className="text-gray-900">
              {info.tour_scheduled ? (
                <span className="text-green-600 font-semibold">
                  Scheduled for {new Date(info.tour_datetime).toLocaleString()}
                </span>
              ) : (
                <span className="text-gray-500">Not scheduled</span>
              )}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Total Sessions</div>
            <div className="text-gray-900">{sessions.length}</div>
          </div>
        </div>
      </div>

      {/* Current Understanding Summary */}
      {Object.keys(understanding).length > 0 && (
        <div className="bg-gradient-to-br from-slate-700 to-slate-800 rounded-lg shadow-sm p-6 mb-6 text-white">
          <h3 className="text-xl font-bold mb-4">Current Understanding</h3>
          <p className="text-sm text-slate-300 mb-6">Real-time prospect insights</p>

          <div className="space-y-6">
            {/* Budget Interest */}
            {understanding.budget_interest && (
              <div>
                <div className="text-xs font-semibold text-slate-300 mb-2">BUDGET INTEREST</div>
                <div className="text-lg text-blue-300">{understanding.budget_interest}</div>
              </div>
            )}

            {/* Care Needs */}
            {understanding.care_needs && understanding.care_needs.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-slate-300 mb-2">CARE NEEDS</div>
                <div className="flex flex-wrap gap-2">
                  {understanding.care_needs.map((need, i) => (
                    <span key={i} className="px-3 py-1 bg-green-600 text-white rounded-full text-sm">
                      {need}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Preferences */}
            {understanding.preferences && understanding.preferences.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-slate-300 mb-2">PREFERENCES</div>
                <ul className="space-y-2">
                  {understanding.preferences.map((pref, i) => (
                    <li key={i} className="text-purple-300">• {pref}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Financing Interests */}
            {understanding.financing_interests && understanding.financing_interests.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-slate-300 mb-2">FINANCING INTERESTS</div>
                <div className="flex flex-wrap gap-2">
                  {understanding.financing_interests.map((fin, i) => (
                    <span key={i} className="px-3 py-1 bg-yellow-600 text-white rounded-full text-sm">
                      {fin}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Tour Interest */}
            {understanding.tour_interest && (
              <div>
                <div className="text-xs font-semibold text-slate-300 mb-2">TOUR INTEREST</div>
                <div className="text-lg text-pink-300">{understanding.tour_interest}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Enrichment Events */}
      {enrichment_events.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Enrichment Events</h3>
          <div className="space-y-3">
            {enrichment_events.map((event, index) => (
              <div key={index} className="border-l-4 border-blue-500 pl-4 py-2 bg-blue-50 rounded">
                <div className="flex justify-between items-start mb-1">
                  <span className="font-semibold text-sm text-blue-900">
                    {event.event_type.replace(/_/g, ' ').toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(event.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="text-sm text-gray-700 mb-1">{event.source_message}</div>
                {Object.keys(event.event_data).length > 0 && (
                  <div className="text-xs text-gray-600 bg-white p-2 rounded mt-2">
                    <pre className="whitespace-pre-wrap">
                      {JSON.stringify(event.event_data, null, 2)}
                    </pre>
                  </div>
                )}
                <div className="text-xs text-gray-500 mt-1">
                  Extracted by: {event.extracted_by_agent} (confidence: {event.confidence})
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Conversation Sessions */}
      <div className="space-y-6">
        {sessions.map((session, sessionIndex) => (
          <div key={session.session_id} className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-bold text-gray-900">
                Session {sessions.length - sessionIndex}
              </h3>
              <div className="text-sm text-gray-500">
                {new Date(session.created_at).toLocaleString()}
              </div>
            </div>

            {/* Current Understanding */}
            {Object.keys(session.current_understanding).length > 0 && (
              <div className="mb-4 p-4 bg-gray-50 rounded">
                <div className="text-sm font-semibold text-gray-700 mb-2">
                  Current Understanding:
                </div>
                <div className="space-y-2">
                  {session.current_understanding.budget_interest && (
                    <div className="text-sm">
                      <span className="font-medium">Budget:</span>{' '}
                      {session.current_understanding.budget_interest}
                    </div>
                  )}
                  {session.current_understanding.care_needs && (
                    <div className="text-sm">
                      <span className="font-medium">Care Needs:</span>{' '}
                      {session.current_understanding.care_needs.join(', ')}
                    </div>
                  )}
                  {session.current_understanding.timeline && (
                    <div className="text-sm">
                      <span className="font-medium">Timeline:</span>{' '}
                      {session.current_understanding.timeline}
                    </div>
                  )}
                  {session.current_understanding.preferences && (
                    <div className="text-sm">
                      <span className="font-medium">Preferences:</span>
                      <ul className="ml-4 mt-1">
                        {session.current_understanding.preferences.map((pref, i) => (
                          <li key={i}>• {pref}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {session.current_understanding.tour_interest && (
                    <div className="text-sm">
                      <span className="font-medium">Tour Interest:</span>{' '}
                      {session.current_understanding.tour_interest}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Conversation History */}
            <div className="space-y-3">
              {session.conversation_history.map((message, msgIndex) => (
                <div
                  key={msgIndex}
                  className={`p-3 rounded ${
                    message.role === 'user'
                      ? 'bg-blue-100 ml-8'
                      : 'bg-gray-100 mr-8'
                  }`}
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className="font-semibold text-sm">
                      {message.role === 'user' ? 'User' : 'Assistant'}
                    </span>
                    {message.intent && (
                      <span className="text-xs text-gray-500">
                        Intent: {message.intent}
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-900">{message.content}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(message.timestamp).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
