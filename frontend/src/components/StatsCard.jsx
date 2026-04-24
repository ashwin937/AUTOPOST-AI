import React from 'react'

export default function StatsCard({title, value, accent}){
  return (
    <div className="glass p-4 rounded-lg w-full">
      <div className="text-sm text-gray-300">{title}</div>
      <div className="mt-2 text-2xl font-heading" style={{color: accent}}>{value}</div>
    </div>
  )
}
