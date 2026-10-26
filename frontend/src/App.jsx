import { useState } from 'react'
import './App.css'
import AdminPanel from './pages/AdminPanel'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <AdminPanel />
    </>
  )
}

export default App
