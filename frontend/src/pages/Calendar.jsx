import React, {useEffect, useState} from 'react'
import { getPosts } from '../api'

export default function Calendar(){
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(()=>{
    getPosts().then(setPosts).catch(console.error).finally(() => setLoading(false))
  },[])

  // Build a map of dates -> posts
  const map = {}
  posts.forEach(p=>{
    const dt = p.metadata.scheduled_at ? new Date(p.metadata.scheduled_at).toISOString().slice(0,10) : null
    if(dt){ map[dt] = map[dt] || []; map[dt].push(p) }
  })

  const today = new Date()
  const days = Array.from({length:30}).map((_,i)=>{
    const d = new Date()
    d.setDate(today.getDate() - (today.getDate()-1) + i)
    const key = d.toISOString().slice(0,10)
    return {key, day: d.getDate(), posts: map[key]||[]}
  })

  if (loading) return <div className="text-gray-400">Loading calendar...</div>

  return (
    <div>
      <h1 className="font-heading text-2xl">Calendar</h1>
      <div className="grid grid-cols-7 gap-2 mt-4">
        {days.map(d => (
          <div key={d.key} className="glass p-2 rounded h-20 hover:bg-white/10 transition">
            <div className="flex justify-between items-start">
              <div className="font-medium text-sm">{d.day}</div>
              {d.posts.length > 0 && <div className="text-xs bg-primary px-1.5 py-0.5 rounded">{d.posts.length}</div>}
            </div>
            <div className="mt-1 text-xs text-gray-400">
              {d.posts.map(p => <div key={p.id} title={p.document} className="truncate">{p.metadata.platform}</div>)}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
