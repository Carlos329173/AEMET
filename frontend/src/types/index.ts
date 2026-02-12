export interface Measurement {
  station: string
  datetime: string          // "2025-02-01T12:00:00+01:00"
  temperature?: number
  pressure?: number
  speed?: number
}
