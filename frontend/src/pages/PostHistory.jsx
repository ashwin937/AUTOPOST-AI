import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function PostHistory() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPosts();
  }, [filter]);

  const loadPosts = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/posts');
      if (!response.ok) throw new Error('Failed to load posts');
      const data = await response.json();
      
      let filtered = data;
      if (filter !== 'all') {
        filtered = data.filter(p => p.status === filter);
      }
      
      setPosts(filtered);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const deletePost = async (postId) => {
    if (!confirm('Delete this post?')) return;
    
    try {
      const response = await fetch(`http://localhost:8000/api/posts/${postId}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error('Failed to delete');
      setPosts(posts.filter(p => p.id !== postId));
      alert('✅ Post deleted');
    } catch (err) {
      alert('❌ ' + err.message);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'posted': return 'text-green-400';
      case 'scheduled': return 'text-yellow-400';
      case 'failed': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  const getStatusBg = (status) => {
    switch (status) {
      case 'posted': return 'bg-green-500/10 border-green-500/30';
      case 'scheduled': return 'bg-yellow-500/10 border-yellow-500/30';
      case 'failed': return 'bg-red-500/10 border-red-500/30';
      default: return 'bg-slate-500/10 border-slate-500/30';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">📋 Post History</h1>
          <p className="text-slate-300">Track all your posts and their status</p>
        </motion.div>

        {/* Filter Buttons */}
        <div className="flex flex-wrap gap-3 mb-8">
          {['all', 'draft', 'scheduled', 'posted', 'failed'].map(status => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg font-semibold transition ${
                filter === status
                  ? 'bg-purple-600 text-white'
                  : 'bg-white/5 text-slate-300 hover:bg-white/10'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>

        {/* Posts Grid */}
        {loading ? (
          <div className="text-center py-12">
            <p className="text-slate-300">Loading posts...</p>
          </div>
        ) : error ? (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400">
            ❌ {error}
          </div>
        ) : posts.length === 0 ? (
          <div className="glass rounded-2xl p-12 text-center backdrop-blur-xl bg-white/5 border border-white/10">
            <p className="text-slate-300 text-lg">No posts found. Upload your first image! 📸</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {posts.map(post => (
              <motion.div
                key={post.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className={`glass rounded-xl p-4 backdrop-blur-xl border ${getStatusBg(post.status)}`}
              >
                {/* Thumbnail */}
                <img
                  src={post.image_path}
                  alt={post.description}
                  className="w-full h-40 object-cover rounded-lg mb-4"
                />

                {/* Description */}
                <p className="text-slate-300 text-sm mb-3 line-clamp-2">
                  {post.description}
                </p>

                {/* Status Badge */}
                <div className="mb-3">
                  <span className={`text-sm font-bold ${getStatusColor(post.status)}`}>
                    ● {post.status.toUpperCase()}
                  </span>
                </div>

                {/* Platform Badges */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {post.platforms_posted.instagram && (
                    <span className="bg-pink-500/20 text-pink-300 text-xs px-2 py-1 rounded">📸</span>
                  )}
                  {post.platforms_posted.facebook && (
                    <span className="bg-blue-500/20 text-blue-300 text-xs px-2 py-1 rounded">👍</span>
                  )}
                  {post.platforms_posted.linkedin && (
                    <span className="bg-blue-700/20 text-blue-300 text-xs px-2 py-1 rounded">💼</span>
                  )}
                  {post.platforms_posted.gmail && (
                    <span className="bg-red-500/20 text-red-300 text-xs px-2 py-1 rounded">📧</span>
                  )}
                </div>

                {/* Date */}
                <p className="text-xs text-slate-400 mb-4">
                  {new Date(post.created_at).toLocaleDateString()}
                </p>

                {/* Actions */}
                <button
                  onClick={() => deletePost(post.id)}
                  className="w-full bg-red-600/80 hover:bg-red-600 text-white font-semibold py-2 rounded-lg transition"
                >
                  🗑️ Delete
                </button>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
