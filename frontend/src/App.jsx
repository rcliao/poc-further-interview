import { useState, useRef, useEffect } from 'react'
import ChatMessage from './components/ChatMessage'
import UnderstandingPanel from './components/UnderstandingPanel'
import ChatInput from './components/ChatInput'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([])
  const [currentUnderstanding, setCurrentUnderstanding] = useState({})
  const [sessionId, setSessionId] = useState(null)
  const [prospectId, setProspectId] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return

    // Add user message to chat
    const userMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageText,
          session_id: sessionId,
          prospect_id: prospectId
        })
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()

      // Update session and prospect IDs
      if (!sessionId) setSessionId(data.session_id)
      if (!prospectId) setProspectId(data.prospect_id)

      // Add assistant message to chat
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        intent: data.intent
      }
      setMessages(prev => [...prev, assistantMessage])

      // Update current understanding
      setCurrentUnderstanding(data.current_understanding)

    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Chat Panel */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-blue-600 text-white p-4 shadow-md">
          <h1 className="text-2xl font-bold">ACME Senior Living</h1>
          <p className="text-blue-100 text-sm">Chat with Sophie, your sales specialist</p>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-8">
              <h2 className="text-xl font-semibold mb-2">Welcome to ACME Senior Living!</h2>
              <p>Ask me about pricing, amenities, tours, or anything else.</p>
            </div>
          )}

          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <ChatInput onSend={sendMessage} disabled={isLoading} />
      </div>

      {/* Understanding Panel */}
      <UnderstandingPanel understanding={currentUnderstanding} />
    </div>
  )
}

export default App
