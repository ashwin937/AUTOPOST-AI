import React, {useState, useEffect} from 'react'
import { motion } from 'framer-motion'
import PlatformBadge from '../components/PlatformBadge'
import { searchPosts, generateContent, createPost } from '../api'

const PLATFORMS = ['twitter','linkedin','instagram']
const TONES = ['professional','casual','funny','inspirational']

export default function CreatePost(){
  const [topic, setTopic] = useState('')
  const [selected, setSelected] = useState(['twitter'])
  const [tone, setTone] = useState('professional')
  const [similar, setSimilar] = useState([])
  const [variants, setVariants] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  useEffect(()=>{
    if(topic.length > 3){
      searchPosts(topic).then(setSimilar).catch(e => console.error(e))
    }
  },[topic])

  const togglePlatform = (p)=>{
    setSelected(s => s.includes(p) ? s.filter(x=>x!==p) : [...s,p])
  }

  const generate = async ()=>{
    if (!topic.trim()) {
      setError('Please enter a topic')
      return
    }
    if (selected.length === 0) {
      setError('Please select at least one platform')
      return
    }
    
    setLoading(true)
    setError(null)
    setSuccess(null)
    try{
      const data = await generateContent(topic, selected, tone)
      setVariants(data)
      setSuccess('Content generated successfully!')
    }catch(e){
      setError('Failed to generate content')
      console.error(e)
    }finally{ 
      setLoading(false) 
    }
  }

  const savePost = async (content, platform)=>{
    try {
      const meta = {
        platform, 
        status: 'draft', 
        tone, 
        topic, 
        scheduled_at: '', 
        created_at: new Date().toISOString(), 
        engagement: 0
      }
      await createPost(content, meta)
      setSuccess(`Saved to ${platform}`)
      setTimeout(() => setSuccess(null), 2000)
    } catch (err) {
      setError('Failed to save post')
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="font-heading text-2xl">Create Post</h1>

      {error && <div className="p-3 bg-red-600/20 border border-red-600/50 rounded text-red-300">{error}</div>}
      {success && <div className="p-3 bg-green-600/20 border border-green-600/50 rounded text-green-300">{success}</div>}

      <div className="glass p-4 space-y-3">
        <label className="block text-sm text-gray-300">Topic / Brand brief</label>
        <textarea 
          value={topic} 
          onChange={e=>setTopic(e.target.value)} 
          placeholder="Enter what you want to post about..."
          className="w-full p-3 bg-transparent border border-white/5 rounded h-28 focus:outline-none focus:ring-2 focus:ring-primary" 
        />

        <div className="mt-3">
          <label className="text-sm text-gray-300 block mb-2">Platforms</label>
          <div className="flex gap-2 flex-wrap">
            {PLATFORMS.map(p => (
              <button 
                key={p} 
                onClick={()=>togglePlatform(p)} 
                className={`px-3 py-2 rounded transition ${selected.includes(p) ? 'bg-primary ring-2 ring-primary' : 'bg-white/5 hover:bg-white/10'}`}
              >
                <PlatformBadge platform={p} />
              </button>
            ))}
          </div>
        </div>

        <div className="mt-3">
          <label className="text-sm text-gray-300 block mb-2">Tone</label>
          <div className="flex gap-2 flex-wrap">
            {TONES.map(t => (
              <button 
                key={t} 
                onClick={()=>setTone(t)} 
                className={`px-3 py-1 rounded transition ${tone===t ? 'bg-cyan ring-2 ring-cyan' : 'bg-white/5 hover:bg-white/10'}`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-4 flex gap-2">
          <button 
            onClick={generate} 
            disabled={loading}
            className="px-4 py-2 bg-primary rounded glow-hover disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {loading ? 'Generating...' : 'Generate with AI'}
          </button>
        </div>
      </div>

      {similar.length > 0 && (
        <div>
          <h2 className="font-heading text-lg">Similar past posts</h2>
          <div className="mt-2 space-y-2">
            {similar.slice(0, 3).map(s => (
              <div key={s.id} className="glass p-3 rounded text-sm">{s.document}</div>
            ))}
          </div>
        </div>
      )}

      {Object.keys(variants).length > 0 && (
        <div>
          <h2 className="font-heading text-lg">Generated Variants</h2>
          <div className="mt-3 grid md:grid-cols-3 gap-3">
            {Object.entries(variants).map(([platform, arr]) => (
              <div key={platform} className="space-y-2">
                <div className="font-medium flex items-center gap-2">
                  <PlatformBadge platform={platform} />
                </div>
                {arr.map((v, i)=> (
                  <motion.div key={i} className="glass p-3 rounded" whileHover={{scale:1.02}}>
                    <p className="text-sm mb-2 text-gray-200">{v}</p>
                    <div className="flex gap-2">
                      <button 
                        onClick={()=>savePost(v, platform)} 
                        className="px-3 py-1 bg-primary rounded text-sm glow-hover"
                      >
                        Save
                      </button>
                      <button className="px-3 py-1 bg-white/5 rounded text-sm hover:bg-white/10">
                        Schedule
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
