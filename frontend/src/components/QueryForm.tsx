// frontend/src/components/QueryForm.tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useState } from 'react'
import { format, parseISO, isBefore } from 'date-fns'
import { fetchAntartidaData, QueryParams } from '../api/client'
import { Measurement } from '../types'

const schema = z.object({
  fechaIni: z.string().min(1, 'Fecha de inicio es obligatoria'),
  fechaFin: z.string().min(1, 'Fecha de fin es obligatoria'),
  estacion: z.enum(['89064', '89070'], {
    required_error: 'Selecciona una estación',
  }),
  location: z.string().min(1, 'Zona horaria es obligatoria').default('Europe/Berlin'),
  aggregation: z.enum(['None', 'Hourly', 'Daily', 'Monthly']).default('None'),
  temperature: z.boolean().optional(),
  pressure: z.boolean().optional(),
  speed: z.boolean().optional(),
}).refine(
  (data) => {
    if (!data.fechaIni || !data.fechaFin) return true
    return isBefore(parseISO(data.fechaIni), parseISO(data.fechaFin))
  },
  {
    message: 'La fecha de inicio debe ser anterior a la fecha de fin',
    path: ['fechaFin'],
  }
)

type FormData = z.infer<typeof schema>

interface Props {
  onDataReceived: (data: Measurement[]) => void
}

export function QueryForm({ onDataReceived }: Props) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      fechaIni: format(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), "yyyy-MM-dd'T'HH:mm"),
      fechaFin: format(new Date(), "yyyy-MM-dd'T'HH:mm"),
      estacion: '89064',                    // Juan Carlos I por defecto
      location: 'Europe/Berlin',
      aggregation: 'None',
      temperature: true,
      pressure: false,
      speed: true,
    },
  })

  const onSubmit = async (form: FormData) => {
    setLoading(true)
    setError(null)

    try {
      // Añadimos :00 para segundos (el backend lo espera)
      const fechaIniStr = form.fechaIni + ':00'
      const fechaFinStr = form.fechaFin + ':00'

      const params: QueryParams = {
        fechaIniStr,
        fechaFinStr,
        identificacion: form.estacion as '89064' | '89070',
        location: form.location,
        aggregation: form.aggregation,
        variables: [
          ...(form.temperature ? ['temperature'] : []),
          ...(form.pressure    ? ['pressure']    : []),
          ...(form.speed       ? ['speed']       : []),
        ],
      }

      const data = await fetchAntartidaData(params)
      onDataReceived(data)

      // Opcional: resetear formulario después de éxito
      // reset()
    } catch (err: any) {
      console.error(err)
      setError(err.response?.data?.detail || 'Error al obtener los datos. Intenta de nuevo.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="bg-white shadow-lg rounded-xl p-8 space-y-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-2">Consulta datos meteorológicos Antártida</h2>
      <p className="text-gray-600 mb-6">Selecciona el rango, estación y variables deseadas</p>

      {/* Mensaje de error */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 text-red-700">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Fecha Inicio */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Fecha y hora de inicio
          </label>
          <input
            type="datetime-local"
            {...register('fechaIni')}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
          {errors.fechaIni && (
            <p className="mt-1 text-sm text-red-600">{errors.fechaIni.message}</p>
          )}
        </div>

        {/* Fecha Fin */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Fecha y hora de fin
          </label>
          <input
            type="datetime-local"
            {...register('fechaFin')}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
          {errors.fechaFin && (
            <p className="mt-1 text-sm text-red-600">{errors.fechaFin.message}</p>
          )}
        </div>
      </div>

      {/* Estación */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Estación meteorológica
        </label>
        <select
          {...register('estacion')}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        >
          <option value="89064">Meteo Station Juan Carlos I (89064)</option>
          <option value="89070">Meteo Station Gabriel de Castilla (89070)</option>
        </select>
        {errors.estacion && (
          <p className="mt-1 text-sm text-red-600">{errors.estacion.message}</p>
        )}
      </div>

      {/* Zona horaria del input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Zona horaria de las fechas ingresadas
        </label>
        <input
          type="text"
          {...register('location')}
          placeholder="Ej: Europe/Berlin, America/Santiago, +02:00"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
        <p className="mt-1 text-xs text-gray-500">
          Ejemplos: Europe/Madrid, Europe/Berlin, UTC, +01:00
        </p>
        {errors.location && (
          <p className="mt-1 text-sm text-red-600">{errors.location.message}</p>
        )}
      </div>

      {/* Agregación */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Nivel de agregación
        </label>
        <select
          {...register('aggregation')}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        >
          <option value="None">Sin agregación (10 minutos)</option>
          <option value="Hourly">Horaria</option>
          <option value="Daily">Diaria</option>
          <option value="Monthly">Mensual</option>
        </select>
      </div>

      {/* Variables */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Variables a consultar (dejar sin marcar = todas)
        </label>
        <div className="flex flex-wrap gap-6">
          <label className="flex items-center">
            <input type="checkbox" {...register('temperature')} className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
            <span className="ml-2 text-sm text-gray-700">Temperatura (°C)</span>
          </label>

          <label className="flex items-center">
            <input type="checkbox" {...register('pressure')} className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
            <span className="ml-2 text-sm text-gray-700">Presión (hPa)</span>
          </label>

          <label className="flex items-center">
            <input type="checkbox" {...register('speed')} className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
            <span className="ml-2 text-sm text-gray-700">Velocidad viento (m/s)</span>
          </label>
        </div>
      </div>

      {/* Botón */}
      <div>
        <button
          type="submit"
          disabled={loading || isSubmitting}
          className={`
            w-full py-3 px-6 rounded-lg font-medium text-white
            ${loading || isSubmitting
              ? 'bg-blue-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'}
            transition-colors
          `}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Consultando...
            </span>
          ) : (
            'Consultar datos'
          )}
        </button>
      </div>
    </form>
  )
}