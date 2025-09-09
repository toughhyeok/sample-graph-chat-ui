// 채팅 메시지 타입
export interface ChatMessage {
  role: 'user' | 'assistant'
  text: string
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

// Neo4j 연결 설정 타입
export interface Neo4jConfig {
  url: string
  user: string
  password: string
  database: string
  initialCypher: string
}

// 모크 데이터 타입
export interface MockGraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

// 그래프 모드 타입
export type GraphMode = 'mock' | 'neovis'

// 그래프 상태 타입
export type GraphStatus = 'ready' | 'rendering' | 'connecting' | 'error'