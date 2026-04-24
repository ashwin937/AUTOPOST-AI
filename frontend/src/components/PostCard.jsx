import React from 'react'
import { motion } from 'framer-motion'
import PlatformBadge from './PlatformBadge'

export default function PostCard({post, onEdit, onDelete, onPublish}){
  return (
    <motion.div whileHover={{ y: -4 }} className="glass p-4 rounded-lg shadow-sm">
      <div className="flex justify-between items-start">
        <div>
          <div className="text-sm text-gray-300">{new Date(post.metadata.created_at).toLocaleString()}</div>
          <div className="mt-2 text-white">{post.document}</div>
        </div>
        <div className="ml-4 flex flex-col items-end gap-2">
          <PlatformBadge platform={post.metadata.platform} />
          <div className="text-xs text-gray-400">{post.metadata.status}</div>
        </div>
      </div>
      <div className="mt-3 flex gap-2">
        <button onClick={()=>onEdit && onEdit(post)} className="px-3 py-1 bg-white/5 rounded text-sm">Edit</button>
        <button onClick={()=>onDelete && onDelete(post.id)} className="px-3 py-1 bg-red-600/30 rounded text-sm">Delete</button>
        <button onClick={()=>onPublish && onPublish(post.id)} className="px-3 py-1 bg-primary text-white rounded text-sm glow-hover">Publish</button>
      </div>
    </motion.div>
  )
}
