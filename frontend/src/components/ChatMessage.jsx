export default function ChatMessage({ message }) {
  const isUser = message.role === 'user'
  const isError = message.isError

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl rounded-lg p-4 shadow-sm ${
          isUser
            ? 'bg-blue-600 text-white'
            : isError
            ? 'bg-red-100 text-red-900'
            : 'bg-white text-gray-900'
        }`}
      >
        <div className="text-sm">{message.content}</div>
        {message.intent && (
          <div className={`text-xs mt-2 ${isUser ? 'text-blue-200' : 'text-gray-500'}`}>
            Intent: {message.intent.replace('_', ' ')}
          </div>
        )}
        <div className={`text-xs mt-1 ${isUser ? 'text-blue-200' : 'text-gray-400'}`}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}
