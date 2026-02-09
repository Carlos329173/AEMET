import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { Measurement } from '../types'

interface Props {
  data: Measurement[]
}

export function TimeSeriesChart({ data }: Props) {
  // Preparar datos para Recharts (necesita array de objetos con timestamp y valores)
  const chartData = data.map(d => ({
    datetime: d.datetime,
    temperature: d.temperature,
    pressure: d.pressure,
    speed: d.speed,
  }))

  return (
    <div className="h-96 w-full bg-white p-4 rounded-lg shadow">
      <ResponsiveContainer>
        <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="datetime" angle={-45} textAnchor="end" height={70} interval="preserveStartEnd" />
          <YAxis yAxisId="left" orientation="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip />
          <Legend />

          <Line yAxisId="left" type="monotone" dataKey="temperature" stroke="#8884d8" name="Temperatura (°C)" />
          <Line yAxisId="right" type="monotone" dataKey="speed" stroke="#82ca9d" name="Velocidad (m/s)" />
          <Line yAxisId="right" type="monotone" dataKey="pressure" stroke="#ffc658" name="Presión (hPa)" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}