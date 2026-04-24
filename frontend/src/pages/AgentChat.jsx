import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function AgentChat() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [imageUploaded, setImageUploaded] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const [agentContext, setAgentContext] = useState(null);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Initialize agent conversation
    initializeAgent();
  }, []);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const initializeAgent = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/agent/reset', {
        method: 'POST'
      });
      const data = await response.json();
      
      setMessages([
        {
          type: 'agent',
          text: '👋 Hi! I\'m your AI posting agent. Tell me what you\'d like to do:\n\n• "Post to Instagram" \n• "Share on Facebook and LinkedIn"\n• "Schedule a post for tomorrow"\n• "Email this to contacts"\n\nWhat\'s your plan?'
        }
      ]);
      setImageUploaded(false);
      setImagePreview(null);
    } catch (err) {
      console.error('Failed to initialize agent:', err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    const userMsg = userInput;
    setUserInput('');
    setMessages(prev => [...prev, { type: 'user', text: userMsg }]);
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });

      if (!response.ok) throw new Error('Failed to chat');
      const data = await response.json();

      setAgentContext(data.context);
      setMessages(prev => [...prev, { type: 'agent', text: data.response }]);

      // Handle agent actions
      if (data.action === 'ask_for_image') {
        setMessages(prev => [...prev, {
          type: 'system',
          text: '📸 Please upload an image to continue'
        }]);
      } else if (data.action === 'ready_to_post') {
        setMessages(prev => [...prev, {
          type: 'system',
          text: '✅ Ready! Say "Post now" or "Schedule it" to proceed'
        }]);
      } else if (data.action === 'ask_for_schedule') {
        setMessages(prev => [...prev, {
          type: 'system',
          text: '⏰ When should I schedule this? (e.g., "tomorrow at 2pm", "in 2 hours")'
        }]);
      }
    } catch (err) {
      setError(err.message);
      setMessages(prev => [...prev, {
        type: 'agent',
        text: '❌ Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/agent/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Upload failed');
      const data = await response.json();

      setImageUploaded(true);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target.result);
      reader.readAsDataURL(file);

      setMessages(prev => [...prev, {
        type: 'user',
        text: '📸 [Image uploaded]'
      }, {
        type: 'agent',
        text: data.message
      }]);
    } catch (err) {
      setError('Failed to upload image: ' + err.message);
      setMessages(prev => [...prev, {
        type: 'agent',
        text: '❌ ' + err.message
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handlePostNow = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/agent/post-now', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) throw new Error('Failed to post');
      const data = await response.json();

      setMessages(prev => [...prev, {
        type: 'agent',
        text: data.message + '\n\n Ready for another post? Upload an image or tell me your next plan!'
      }]);

      // Reset for next post
      setImageUploaded(false);
      setImagePreview(null);
      initializeAgent();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSchedulePost = async () => {
    const time = prompt('When should this post? (e.g., "2024-04-08 14:00:00")');
    if (!time) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/agent/schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `scheduled_time=${encodeURIComponent(time)}`
      });

      if (!response.ok) throw new Error('Failed to schedule');
      const data = await response.json();

      setMessages(prev => [...prev, {
        type: 'agent',
        text: data.message + '\n\nReady for another post? Upload an image or tell me your next plan!'
      }]);

      // Reset for next post
      setImageUploaded(false);
      setImagePreview(null);
      initializeAgent();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-6 text-white">
        <h1 className="text-3xl font-bold">🤖 AI Posting Agent</h1>
        <p className="text-purple-100">Chat naturally to post and schedule content</p>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        <AnimatePresence>
          {messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                  msg.type === 'user'
                    ? 'bg-purple-600 text-white rounded-br-none'
                    : msg.type === 'system'
                    ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-bl-none'
                    : 'bg-slate-700 text-slate-100 rounded-bl-none'
                }`}
              >
                <p className="whitespace-pre-line text-sm">{msg.text}</p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Image Preview */}
        {imagePreview && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex justify-start"
          >
            <div className="bg-slate-700 rounded-lg p-4 rounded-bl-none">
              <img src={imagePreview} alt="Upload preview" className="max-w-xs rounded-lg" />
            </div>
          </motion.div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-red-500/10 border border-red-500/30 text-red-400 p-3 rounded-lg text-sm"
          >
            ❌ {error}
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Action Buttons - Show when context is ready */}
      {agentContext && agentContext.has_image && agentContext.platforms.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="px-6 pb-4 flex gap-3"
        >
          <button
            onClick={handlePostNow}
            disabled={loading}
            className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-bold py-3 rounded-lg hover:shadow-lg hover:shadow-green-500/50 transition disabled:opacity-50"
          >
            {loading ? '⏳ Posting...' : '✅ Post Now'}
          </button>
          <button
            onClick={handleSchedulePost}
            disabled={loading}
            className="flex-1 bg-gradient-to-r from-orange-600 to-yellow-600 text-white font-bold py-3 rounded-lg hover:shadow-lg hover:shadow-orange-500/50 transition disabled:opacity-50"
          >
            {loading ? '⏳ Scheduling...' : '📅 Schedule'}
          </button>
        </motion.div>
      )}

      {/* Image Upload */}
      {!imageUploaded && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="px-6 pb-4"
        >
          <label className="block">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              disabled={loading}
              className="hidden"
            />
            <div className="border-2 border-dashed border-purple-500/50 rounded-lg p-4 text-center cursor-pointer hover:border-purple-500 transition">
              <p className="text-slate-300 font-semibold">
                {loading ? '⏳ Uploading...' : '📸 Click to upload image or drag & drop'}
              </p>
            </div>
          </label>
        </motion.div>
      )}

      {/* Input Area */}
      <div className="border-t border-white/10 p-6 bg-slate-800/50">
        <form onSubmit={handleSendMessage} className="flex gap-3">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Tell me what to do... (e.g., 'Post to Instagram', 'Schedule for tomorrow')"
            disabled={loading}
            className="flex-1 px-4 py-3 rounded-lg bg-slate-700 border border-slate-600 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !userInput.trim()}
            className="bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold px-6 py-3 rounded-lg hover:shadow-lg hover:shadow-purple-500/50 transition disabled:opacity-50"
          >
            {loading ? '⏳' : '📤 Send'}
          </button>
        </form>
      </div>
    </div>
  );
}
