export interface Hole {
  pid: number
  text: string
  image?: string
  like_count?: number
  reply_count?: number
  created_at?: number
  deleted_at?: number
}

export interface HoleComment {
  cid: number
  pid: number
  text: string
  created_at: number
}
