import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import Sidebar from './components/Sidebar'
import AgentChat from './pages/AgentChat'
import UploadPhoto from './pages/UploadPhoto'
import PostHistory from './pages/PostHistory'
import Settings from './pages/Settings'

export default function App(){
  return (
    <div className="min-h-screen flex bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <Sidebar />
      <main className="flex-1">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <Routes>
            <Route path="/" element={<AgentChat/>} />
            <Route path="/upload" element={<UploadPhoto/>} />
            <Route path="/history" element={<PostHistory/>} />
            <Route path="/settings" element={<Settings/>} />
          </Routes>
        </motion.div>
      </main>
    </div>
  )
}
