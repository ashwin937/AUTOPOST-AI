import React, {useEffect, useState} from 'react'
import PostCard from '../components/PostCard'
import SearchBar from '../components/SearchBar'
import { getPosts, searchPosts, deletePost, publishPost } from '../api'

export default function Posts(){
  const [posts, setPosts] = useState([])
  const [platform, setPlatform] = useState('')
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = async ()=>{
    try {
      setLoading(true)
      setError(null)
      const data = await getPosts(platform, status)
      setPosts(data)
    } catch (err) {
      setError('Failed to load posts')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(()=>{ load() },[])

  const onSearch = async (q)=>{
    if (!q.trim()) {
      load()
      return
    }
    try {
      const data = await searchPosts(q)
      setPosts(data)
    } catch (err) {
      setError('Search failed')
    }
  }

  const onDelete = async (id)=> {
    try {
      await deletePost(id)
      load()
    } catch (err) {
      setError('Failed to delete post')
    }
  }

  const onPublish = async (id)=> {
    try {
      await publishPost(id)
      load()
    } catch (err) {
      setError('Failed to publish post')
    }
  }

  const applyFilters = () => load()

  if (loading) return <div className="text-gray-400">Loading posts...</div>

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="font-heading text-2xl">Posts</h1>
        <div className="flex gap-2">
          <select value={platform} onChange={e=>setPlatform(e.target.value)} className="bg-white/5 p-2 rounded focus:outline-none focus:ring-2 focus:ring-primary">
            <option value="">All platforms</option>
            <option value="twitter">Twitter</option>
            <option value="linkedin">LinkedIn</option>
            <option value="instagram">Instagram</option>
          </select>
          <select value={status} onChange={e=>setStatus(e.target.value)} className="bg-white/5 p-2 rounded focus:outline-none focus:ring-2 focus:ring-primary">
            <option value="">All status</option>
            <option value="draft">Draft</option>
            <option value="scheduled">Scheduled</option>
            <option value="published">Published</option>
          </select>
          <button onClick={applyFilters} className="px-3 py-2 bg-primary rounded glow-hover">Filter</button>
        </div>
      </div>

      {error && <div className="p-3 bg-red-600/20 border border-red-600/50 rounded text-red-300">{error}</div>}

      <div className="glass p-4">
        <SearchBar onSearch={onSearch} placeholder="Search semantically..." />
      </div>

      <div className="space-y-3">
        {posts.length === 0 ? <div className="text-gray-400">No posts found</div> : posts.map(p=> <PostCard key={p.id} post={p} onDelete={onDelete} onPublish={onPublish} />)}
      </div>
    </div>
  )
}
