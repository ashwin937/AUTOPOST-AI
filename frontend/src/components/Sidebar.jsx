import React from 'react'
import { NavLink } from 'react-router-dom'

const links = [
  {to: '/', label: '🤖 AI Agent', icon: '🤖'},
  {to: '/upload', label: '📸 Quick Upload', icon: '📸'},
  {to: '/history', label: '📋 Post History', icon: '📋'},
  {to: '/settings', label: '⚙️ Settings', icon: '⚙️'}
]

export default function Sidebar(){
  return (
    <aside className="w-20 md:w-64 p-4 glass bg-gradient-to-b from-slate-800 to-slate-900 border-r border-white/10">
      <div className="hidden md:flex items-center space-x-3 mb-8 p-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center text-white font-bold">AP</div>
        <div>
          <div className="font-heading text-xl font-bold text-white">AutoPost</div>
          <div className="text-xs text-slate-400">AI Agent</div>
        </div>
      </div>
      <nav className="flex flex-col gap-3">
        {links.map(l => (
          <NavLink 
            key={l.to} 
            to={l.to} 
            className={({isActive}) => `py-3 px-4 rounded-lg hover:bg-white/10 transition font-medium ${
              isActive 
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg shadow-purple-500/50' 
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <span className="md:hidden">{l.icon}</span>
            <span className="hidden md:inline">{l.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
