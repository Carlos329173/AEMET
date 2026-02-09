import { useMemo } from 'react'
import {
  useReactTable,
  getCoreRowModel,
  ColumnDef,
  flexRender,
} from '@tanstack/react-table'
import { Measurement } from '../types'

interface Props {
  data: Measurement[]
}

export function DataTable({ data }: Props) {
  const columns = useMemo<ColumnDef<Measurement>[]>(
    () => [
      { accessorKey: 'datetime', header: 'Fecha/Hora (CET/CEST)' },
      { accessorKey: 'station',  header: 'Estación' },
      { accessorKey: 'temperature', header: 'Temperatura (°C)', cell: info => info.getValue()?.toFixed(1) ?? '-' },
      { accessorKey: 'pressure',    header: 'Presión (hPa)',    cell: info => info.getValue()?.toFixed(0) ?? '-' },
      { accessorKey: 'speed',       header: 'Velocidad (m/s)',  cell: info => info.getValue()?.toFixed(1) ?? '-' },
    ],
    []
  )

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-100">
          {table.getHeaderGroups().map(headerGroup => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map(header => (
                <th key={header.id} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {table.getRowModel().rows.map(row => (
            <tr key={row.id}>
              {row.getVisibleCells().map(cell => (
                <td key={cell.id} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}