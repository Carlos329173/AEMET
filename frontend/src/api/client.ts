import axios from 'axios'
import type { Measurement } from '../types'

const api = axios.create({
  baseURL: '/api', // proxied por vite → backend:8000
})

export interface QueryParams {
  fechaIniStr: string
  fechaFinStr: string
  identificacion: '89064' | '89070'
  location?: string
  aggregation?: 'None' | 'Hourly' | 'Daily' | 'Monthly'
  variables?: ('temperature' | 'pressure' | 'speed')[]
}

export const fetchAntartidaData = async (params: QueryParams): Promise<Measurement[]> => {
  const response = await api.get<Measurement[]>(
    `/antartida/datos/fechaini/${params.fechaIniStr}/fechafin/${params.fechaFinStr}/estacion/${params.identificacion}`,
    {
      params: {
        location: params.location,
        aggregation: params.aggregation,
        variables: params.variables?.join(','),
      }
    }
  )
  return response.data
}