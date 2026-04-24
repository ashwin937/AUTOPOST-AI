import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

export default function Settings(){
  const [apis, setApis] = useState({
    anthropic: '',
    facebook: '',
    instagram: '',
    linkedin: '',
    gmail: '',
    instagramUsername: '',
    instagramPassword: ''
  })
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem('ap_api_keys')
    if(saved) {
      try {
        setApis(JSON.parse(saved))
      } catch(e) {
        console.error('Failed to load API keys', e)
      }
    }
  }, [])

  const save = () => {
    localStorage.setItem('ap_api_keys', JSON.stringify(apis))
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const apiFields = [
    {key: 'anthropic', label: '🤖 Claude API Key', placeholder: 'sk-ant-...'},
    {key: 'facebook', label: '👍 Facebook Access Token', placeholder: 'EAABs...'},
    {key: 'instagram', label: '📸 Instagram Business Account ID', placeholder: '17841...'},
    {key: 'linkedin', label: '💼 LinkedIn Access Token', placeholder: 'AQU...'},
    {key: 'gmail', label: '📧 Gmail Credentials (JSON)', placeholder: '{...}'},
    {key: 'instagramUsername', label: '📸 Instagram Username', placeholder: 'your_username'},
    {key: 'instagramPassword', label: '📸 Instagram Password', placeholder: 'password'},
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">⚙️ Settings</h1>
          <p className="text-slate-300">Configure API keys for social media and AI integrations</p>
        </motion.div>

        {/* Success Message */}
        {saved && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mb-6 p-4 bg-green-500/10 border border-green-500/30 rounded-lg text-green-400 font-semibold"
          >
            ✅ Settings saved successfully!
          </motion.div>
        )}

        {/* API Configuration */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-8 backdrop-blur-xl bg-white/5 border border-white/10 space-y-6"
        >
          <div>
            <h2 className="text-2xl font-bold text-white mb-6">API Keys & Credentials</h2>
            <p className="text-slate-400 mb-6">Add your API keys to enable full functionality. All keys are stored locally in your browser.</p>
          </div>

          <div className="space-y-4">
            {apiFields.map(field => (
              <div key={field.key}>
                <label className="block text-white font-semibold mb-2">{field.label}</label>
                <input
                  type={field.key.includes('Password') ? 'password' : 'text'}
                  placeholder={field.placeholder}
                  value={apis[field.key] || ''}
                  onChange={e => setApis({...apis, [field.key]: e.target.value})}
                  className="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 transition"
                />
                <p className="text-xs text-slate-400 mt-1">
                  {field.key === 'anthropic' && 'Get from: https://console.anthropic.com'}
                  {field.key === 'facebook' && 'Get from: https://developers.facebook.com'}
                  {field.key === 'linkedin' && 'Get from: https://www.linkedin.com/developers'}
                  {field.key === 'gmail' && 'Download credentials JSON from Google Cloud Console'}
                </p>
              </div>
            ))}
          </div>

          {/* Save Button */}
          <button
            onClick={save}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold py-3 rounded-lg hover:shadow-lg hover:shadow-purple-500/50 transition mt-8"
          >
            💾 Save All Settings
          </button>
        </motion.div>

        {/* Info Box */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-8 glass rounded-2xl p-8 backdrop-blur-xl bg-blue-500/5 border border-blue-500/20"
        >
          <h3 className="text-xl font-bold text-blue-300 mb-4">ℹ️ How It Works</h3>
          <ul className="text-slate-300 space-y-2">
            <li>✅ Add API keys above for automatic posting</li>
            <li>✅ Without keys, the app uses mock generation (for testing)</li>
            <li>✅ Keys are stored securely in your browser localStorage</li>
            <li>✅ You can use the app with or without API keys</li>
            <li>✅ Real posting requires valid, authorized API credentials</li>
          </ul>
        </motion.div>
      </div>
    </div>
  )
}
