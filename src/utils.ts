import { format as formatDate } from 'light-date'

export const formatTime = (time: number) => formatDate(
  new Date(time), '{yyyy}-{MM}-{dd} {HH}:{mm}:{ss}',
)
