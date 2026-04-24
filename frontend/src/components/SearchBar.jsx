import React, {useState} from 'react'

export default function SearchBar({placeholder='Search', onSearch}){
  const [q, setQ] = useState('')
  return (
    <div className="flex items-center gap-2">
      <input value={q} onChange={e=>setQ(e.target.value)} placeholder={placeholder} className="flex-1 p-2 rounded bg-white/5" />
      <button onClick={()=>onSearch && onSearch(q)} className="px-3 py-2 bg-primary rounded">Search</button>
    </div>
  )
}
