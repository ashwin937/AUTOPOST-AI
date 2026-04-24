import React, { useState } from 'react';
import { motion } from 'framer-motion';

export default function UploadPhoto() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [platforms, setPlatforms] = useState([]);
  const [tone, setTone] = useState('professional');
  const [recipientEmail, setRecipientEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [postId, setPostId] = useState(null);
  const [error, setError] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  const platformOptions = [
    { id: 'instagram', label: '📸 Instagram', color: 'from-pink-500 to-orange-400' },
    { id: 'facebook', label: '👍 Facebook', color: 'from-blue-600 to-blue-400' },
    { id: 'linkedin', label: '💼 LinkedIn', color: 'from-blue-700 to-blue-500' },
    { id: 'gmail', label: '📧 Gmail', color: 'from-red-500 to-red-400' }
  ];

  const toneOptions = ['professional', 'casual', 'funny', 'inspirational'];

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const togglePlatform = (platformId) => {
    setPlatforms(prev =>
      prev.includes(platformId)
        ? prev.filter(p => p !== platformId)
        : [...prev, platformId]
    );
  };

  const handleGenerateContent = async () => {
    if (!selectedFile) {
      setError('Please select an image');
      return;
    }
    if (platforms.length === 0) {
      setError('Select at least one platform');
      return;
    }
    if (platforms.includes('gmail') && !recipientEmail) {
      setError('Enter recipient email for Gmail');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('platforms', platforms.join(','));
      formData.append('tone', tone);
      formData.append('recipient_email', recipientEmail);

      const response = await fetch('http://localhost:8000/api/posts/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to generate content');
      }

      const data = await response.json();
      setGeneratedContent(data);
      setPostId(data.post_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePostImmediately = async () => {
    if (!postId) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('platforms', platforms.join(','));
      formData.append('recipient_email', recipientEmail);

      const response = await fetch(`http://localhost:8000/api/posts/${postId}/post`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to post');
      }

      const data = await response.json();
      alert('✅ Posted successfully to: ' + Object.keys(data.results).filter(p => data.results[p].success).join(', '));
      
      // Reset
      setSelectedFile(null);
      setImagePreview(null);
      setPlatforms([]);
      setGeneratedContent(null);
      setPostId(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSchedulePost = async () => {
    if (!postId) return;

    const scheduledTime = new Date();
    scheduledTime.setHours(scheduledTime.getHours() + 2);

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('platforms', platforms.join(','));
      formData.append('scheduled_time', scheduledTime.toISOString());
      formData.append('recipient_email', recipientEmail);

      const response = await fetch(`http://localhost:8000/api/posts/${postId}/schedule`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to schedule');
      }

      alert(`✅ Post scheduled for ${scheduledTime.toLocaleString()}`);
      
      // Reset
      setSelectedFile(null);
      setImagePreview(null);
      setPlatforms([]);
      setGeneratedContent(null);
      setPostId(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl font-bold text-white mb-2">📸 Upload & Auto-Post</h1>
          <p className="text-slate-300">Upload a photo and instantly generate content for all platforms</p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass rounded-2xl p-8 backdrop-blur-xl bg-white/5 border border-white/10"
          >
            <h2 className="text-2xl font-bold text-white mb-6">Step 1: Upload Photo</h2>

            {/* File Upload */}
            <div className="mb-6">
              <label className="block text-white font-semibold mb-3">Select Image</label>
              <div className="relative">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div className="border-2 border-dashed border-purple-500/50 rounded-lg p-8 text-center hover:border-purple-500 transition">
                  {imagePreview ? (
                    <img src={imagePreview} alt="Preview" className="max-h-48 mx-auto rounded-lg" />
                  ) : (
                    <>
                      <p className="text-slate-300">Drag or click to upload</p>
                      <p className="text-sm text-slate-400">JPG, PNG, GIF up to 5MB</p>
                    </>
                  )}
                </div>
              </div>
              {selectedFile && (
                <p className="mt-2 text-green-400 text-sm">✅ {selectedFile.name}</p>
              )}
            </div>

            {/* Select Tone */}
            <div className="mb-6">
              <label className="block text-white font-semibold mb-3">Content Tone</label>
              <div className="grid grid-cols-2 gap-3">
                {toneOptions.map(t => (
                  <button
                    key={t}
                    onClick={() => setTone(t)}
                    className={`p-3 rounded-lg font-semibold transition ${
                      tone === t
                        ? 'bg-purple-600 text-white'
                        : 'bg-white/5 text-slate-300 hover:bg-white/10'
                    }`}
                  >
                    {t.charAt(0).toUpperCase() + t.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Select Platforms */}
            <div className="mb-6">
              <label className="block text-white font-semibold mb-3">Post Platforms</label>
              <div className="space-y-2">
                {platformOptions.map(platform => (
                  <button
                    key={platform.id}
                    onClick={() => togglePlatform(platform.id)}
                    className={`w-full p-3 rounded-lg font-semibold transition text-left ${
                      platforms.includes(platform.id)
                        ? `bg-gradient-to-r ${platform.color} text-white`
                        : 'bg-white/5 text-slate-300 hover:bg-white/10'
                    }`}
                  >
                    {platform.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Gmail Recipient */}
            {platforms.includes('gmail') && (
              <div className="mb-6">
                <label className="block text-white font-semibold mb-3">Recipient Email</label>
                <input
                  type="email"
                  value={recipientEmail}
                  onChange={(e) => setRecipientEmail(e.target.value)}
                  placeholder="recipient@example.com"
                  className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-slate-400"
                />
              </div>
            )}

            {/* Generate Button */}
            <button
              onClick={handleGenerateContent}
              disabled={loading}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold py-3 rounded-lg hover:shadow-lg hover:shadow-purple-500/50 transition disabled:opacity-50"
            >
              {loading ? '⏳ Generating...' : '🚀 Generate Content'}
            </button>

            {error && (
              <p className="mt-4 text-red-400 text-sm">❌ {error}</p>
            )}
          </motion.div>

          {/* Generated Content Section */}
          {generatedContent && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="glass rounded-2xl p-8 backdrop-blur-xl bg-white/5 border border-white/10"
            >
              <h2 className="text-2xl font-bold text-white mb-6">Step 2: Review & Post</h2>

              {/* Content Preview */}
              <div className="space-y-6 mb-6 max-h-96 overflow-y-auto">
                {generatedContent.generated_content.instagram_caption && (
                  <div className="bg-gradient-to-br from-pink-500/10 to-orange-500/10 border border-pink-500/30 rounded-lg p-4">
                    <h3 className="text-pink-400 font-bold mb-2">📸 Instagram</h3>
                    <p className="text-slate-300 text-sm">{generatedContent.generated_content.instagram_caption}</p>
                  </div>
                )}
                {generatedContent.generated_content.facebook_text && (
                  <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/10 border border-blue-500/30 rounded-lg p-4">
                    <h3 className="text-blue-400 font-bold mb-2">👍 Facebook</h3>
                    <p className="text-slate-300 text-sm">{generatedContent.generated_content.facebook_text}</p>
                  </div>
                )}
                {generatedContent.generated_content.linkedin_text && (
                  <div className="bg-gradient-to-br from-blue-700/10 to-blue-600/10 border border-blue-700/30 rounded-lg p-4">
                    <h3 className="text-blue-400 font-bold mb-2">💼 LinkedIn</h3>
                    <p className="text-slate-300 text-sm">{generatedContent.generated_content.linkedin_text}</p>
                  </div>
                )}
                {generatedContent.generated_content.gmail_subject && (
                  <div className="bg-gradient-to-br from-red-500/10 to-red-600/10 border border-red-500/30 rounded-lg p-4">
                    <h3 className="text-red-400 font-bold mb-2">📧 Gmail</h3>
                    <p className="text-slate-300 text-sm"><strong>Subject:</strong> {generatedContent.generated_content.gmail_subject}</p>
                    <p className="text-slate-300 text-sm mt-2">{generatedContent.generated_content.gmail_body}</p>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="space-y-3">
                <button
                  onClick={handlePostImmediately}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white font-bold py-3 rounded-lg hover:shadow-lg hover:shadow-green-500/50 transition disabled:opacity-50"
                >
                  {loading ? '⏳ Posting...' : '✅ Post Now'}
                </button>
                <button
                  onClick={handleSchedulePost}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-orange-600 to-yellow-600 text-white font-bold py-3 rounded-lg hover:shadow-lg hover:shadow-orange-500/50 transition disabled:opacity-50"
                >
                  {loading ? '⏳ Scheduling...' : '📅 Schedule for Later'}
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
