import React from 'react'

const map = {
  twitter: {label: 'Twitter', color: 'bg-[#1DA1F2]'},
  linkedin: {label: 'LinkedIn', color: 'bg-[#0A66C2]'},
  instagram: {label: 'Instagram', color: 'bg-gradient-to-r from-[#f77737] via-[#f56040] to-[#833ab4]'}
}

export default function PlatformBadge({platform}){
  const p = map[platform] || {label: platform, color: 'bg-gray-500'}
  return (
    <div className={`text-xs px-2 py-1 rounded-full text-white ${p.color}`}>{p.label}</div>
  )
}
