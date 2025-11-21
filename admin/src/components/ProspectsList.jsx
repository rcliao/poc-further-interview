export default function ProspectsList({ prospects, selectedProspectId, onSelectProspect }) {
  return (
    <div className="divide-y">
      {prospects.length === 0 ? (
        <div className="p-8 text-center text-gray-500">No prospects yet</div>
      ) : (
        prospects.map((prospect) => (
          <div
            key={prospect.prospect_id}
            onClick={() => onSelectProspect(prospect.prospect_id)}
            className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
              selectedProspectId === prospect.prospect_id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
            }`}
          >
            <div className="flex justify-between items-start mb-2">
              <div className="font-semibold text-gray-900">
                {prospect.first_name || prospect.last_name
                  ? `${prospect.first_name || ''} ${prospect.last_name || ''}`.trim()
                  : 'Anonymous'}
              </div>
              {prospect.tour_scheduled && (
                <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                  Tour Scheduled
                </span>
              )}
            </div>

            {prospect.email && (
              <div className="text-sm text-gray-600 mb-1">{prospect.email}</div>
            )}

            {prospect.phone && (
              <div className="text-sm text-gray-600 mb-2">{prospect.phone}</div>
            )}

            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{prospect.total_sessions} session(s)</span>
              {prospect.last_interaction && (
                <span>Last: {new Date(prospect.last_interaction).toLocaleDateString()}</span>
              )}
            </div>

            {Object.keys(prospect.current_understanding).length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {prospect.current_understanding.budget_interest && (
                  <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded">
                    Budget
                  </span>
                )}
                {prospect.current_understanding.care_needs && (
                  <span className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded">
                    Care Needs
                  </span>
                )}
                {prospect.current_understanding.tour_interest && (
                  <span className="bg-pink-100 text-pink-700 text-xs px-2 py-0.5 rounded">
                    Tour Interest
                  </span>
                )}
              </div>
            )}
          </div>
        ))
      )}
    </div>
  )
}
