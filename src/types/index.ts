import type { Dayjs } from 'dayjs'

// 채팅 메시지 타입
export interface ChatMessage {
  role: 'user' | 'assistant'
  text: string
  timestamp: Dayjs
}

// 그래프 노드 타입
export interface GraphNode {
  id: string
  label: string
  group: string
}

// 그래프 엣지 타입
export interface GraphEdge {
  id: string
  from: string
  to: string
  label: string
}

// 모크 데이터 타입
export interface MockGraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

// 그래프 상태 타입
export type GraphStatus = 'ready' | 'rendering' | 'error'