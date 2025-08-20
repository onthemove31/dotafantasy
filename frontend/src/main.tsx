import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'
import './index.css'

const qc = new QueryClient()

function Health() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['healthz'],
    queryFn: async () => {
      const res = await fetch('http://localhost:8000/healthz')
      if (!res.ok) throw new Error('Healthz failed')
      return res.json()
    },
  })

  if (isLoading) return <div className="p-6">Loading…</div>
  if (error) return <div className="p-6 text-red-600">Error: {(error as Error).message}</div>

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold">dota-fantasy</h1>
      <pre className="mt-4 rounded bg-slate-100 p-4 text-sm">{JSON.stringify(data, null, 2)}</pre>
    </div>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={qc}>
      <Health />
    </QueryClientProvider>
  </React.StrictMode>,
)
