// API Configuration
// Automatically uses the correct API URL based on environment

const getApiUrl = () => {
  // Check if we have environment variable
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // In development, use proxy
  if (import.meta.env.DEV) {
    return ''  // Empty string uses proxy configured in vite.config.js
  }
  
  // In production, if no env var set, show error
  console.error('⚠️ VITE_API_URL not configured! Set it in .env.production')
  return '/api'  // Fallback (will likely fail)
}

export const API_BASE_URL = getApiUrl()

export const API_ENDPOINTS = {
  health: '/health',
  generateLeads: '/api/v1/leads/generate',
  generateLeadsAsync: '/api/v1/leads/generate-async',
  jobStatus: (jobId) => `/api/v1/leads/status/${jobId}`,
  sendEmail: '/api/v1/email/send',
  generateEmailContent: '/api/v1/email/generate-content'
}

