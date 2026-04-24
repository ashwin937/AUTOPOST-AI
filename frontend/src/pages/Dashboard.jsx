import React, {useEffect, useState} from 'react'
import StatsCard from '../components/StatsCard'
import PostCard from '../components/PostCard'
import SearchBar from '../components/SearchBar'
import { getStats, getPosts, searchPosts, deletePost, publishPost } from '../api'

export default function Dashboard(){
  const [stats, setStats] = useState(null)
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(()=>{
    loadData()
  },[])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [statsData, postsData] = await Promise.all([getStats(), getPosts()])
      setStats(statsData)
      setPosts(postsData)
    } catch (err) {
      setError('Failed to load data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const onSearch = async (q)=>{
    if (!q.trim()) return
    try {
      const results = await searchPosts(q)
      setPosts(results)
    } catch (err) {
      setError('Search failed')
    }
  }

  const onDelete = async (id) => {
    try {
      await deletePost(id)
      await loadData()
    } catch (err) {
      setError('Failed to delete post')
    }
  }

  const onPublish = async (id) => {
    try {
      await publishPost(id)
      await loadData()
    } catch (err) {
      setError('Failed to publish post')
    }
  }

  if (loading) return <div className="text-gray-400">Loading dashboard...</div>

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="font-heading text-3xl">Dashboard</h1>
        <a href="/create" className="px-4 py-2 bg-primary rounded glow-hover transition">Create Post</a>
      </div>

      {error && <div className="p-3 bg-red-600/20 border border-red-600/50 rounded text-red-300">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard title="Total Posts" value={stats?.total ?? '...'} accent={'#7C3AED'} />
        <StatsCard title="Scheduled" value={stats?.by_status?.scheduled ?? 0} accent={'#06B6D4'} />
        <StatsCard title="Published" value={stats?.by_status?.published ?? 0} accent={'#10B981'} />
        <StatsCard title="Engagement Rate" value={Math.round((stats?.engagement_rate||0))} accent={'#F59E0B'} />
      </div>

      <div className="glass p-4">
        <SearchBar onSearch={onSearch} placeholder="Search semantically..."/>
      </div>

      <div className="space-y-3">
        {posts.length === 0 ? <div className="text-gray-400">No posts yet</div> : posts.map(p => (
          <PostCard key={p.id} post={p} onDelete={onDelete} onPublish={onPublish} />
        ))}
      </div>
    </div>
  )
}
