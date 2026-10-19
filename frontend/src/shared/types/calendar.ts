export interface CalendarEvent {
  id: number
  tournament: number
  type: string
  title: string
  description: string
  link: string
  start_datetime: string
}

export interface CalendarRound {
  id: number
  tournament: number
  name: string
  start_date: string
  end_date: string
}
