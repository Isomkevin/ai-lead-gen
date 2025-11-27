import { useState, useRef } from 'react'
import { Mic, Volume2, Play, Pause, Loader, AlertCircle } from 'lucide-react'
import { motion } from 'framer-motion'
import { API_BASE_URL } from '../config/api'

export default function AvatarAssistant({ lead, onVoiceGenerated }) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [audioUrl, setAudioUrl] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [error, setError] = useState(null)
  const audioRef = useRef(null)

  const generateVoice = async (messageType = 'introduction') => {
    setIsGenerating(true)
    setError(null)
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/avatar/generate-voice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_name: lead.company_name,
          message_type: messageType
        })
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to generate voice' }))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }
      
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      setAudioUrl(url)
      if (onVoiceGenerated) onVoiceGenerated(url)
    } catch (error) {
      console.error('Error generating voice:', error)
      setError(error.message || 'Failed to generate voice message')
    } finally {
      setIsGenerating(false)
    }
  }

  const playPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const handleAudioEnd = () => {
    setIsPlaying(false)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-4 sm:p-6 border border-purple-200"
    >
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center flex-shrink-0">
          <Volume2 className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 text-sm sm:text-base">AI Voice Assistant</h3>
          <p className="text-xs sm:text-sm text-gray-600">Generate personalized voice messages</p>
        </div>
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2"
        >
          <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-xs sm:text-sm text-red-800">{error}</p>
            <p className="text-xs text-red-600 mt-1">Make sure ELEVENLABS_API_KEY is configured on the server.</p>
          </div>
        </motion.div>
      )}

      <div className="space-y-3">
        <button
          onClick={() => generateVoice('introduction')}
          disabled={isGenerating}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm sm:text-base"
        >
          {isGenerating ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              <span>Generating...</span>
            </>
          ) : (
            <>
              <Mic className="w-4 h-4" />
              <span>Generate Voice Message</span>
            </>
          )}
        </button>

        {audioUrl && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-3 p-3 bg-white rounded-lg border border-purple-200"
          >
            <button
              onClick={playPause}
              className="p-2 bg-purple-100 rounded-full hover:bg-purple-200 transition-colors flex-shrink-0"
              aria-label={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? (
                <Pause className="w-4 h-4 text-purple-600" />
              ) : (
                <Play className="w-4 h-4 text-purple-600" />
              )}
            </button>
            <audio
              ref={audioRef}
              src={audioUrl}
              onEnded={handleAudioEnd}
              className="flex-1"
              controls
            />
          </motion.div>
        )}

        <div className="text-xs text-gray-500 pt-2 border-t border-purple-100">
          <p>💡 Voice messages can be downloaded and shared via email or SMS</p>
        </div>
      </div>
    </motion.div>
  )
}

