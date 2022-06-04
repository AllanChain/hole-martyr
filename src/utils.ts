import { format } from 'light-date'

export const formatDate = (date: Date) => format(date, '{yyyy}-{MM}-{dd} {HH}:{mm}:{ss}')

export const formatTime = (time: number) => formatDate(new Date(time))
