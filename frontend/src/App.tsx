import { QueryForm } from './components/QueryForm'
import { DataTable } from './components/DataTable'
import { TimeSeriesChart } from './components/TimeSeriesChart'
import { Measurement } from './types'

import { useState } from 'react'

function App() {
  const [data, setData] = useState<Measurement[]>([])

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          AEMET Antártida - Datos Meteorológicos
        </h1>

        <QueryForm onDataReceived={setData} />

        {data.length > 0 && (
          <>
            <div className="mt-10">
              <h2 className="text-2xl font-semibold mb-4">Gráfico de series temporales</h2>
              <TimeSeriesChart data={data} />
            </div>

            <div className="mt-10">
              <h2 className="text-2xl font-semibold mb-4">Tabla de datos</h2>
              <DataTable data={data} />
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default App