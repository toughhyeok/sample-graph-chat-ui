<template>
  <div class="space-y-3">
    <!-- 컨트롤 패널 -->
    <div class="flex flex-wrap items-center gap-2">
      <!-- 물리 효과 체크박스 -->
      <label class="inline-flex items-center gap-2 bg-white px-3 py-2 rounded-md shadow">
        <input type="checkbox" v-model="physics" class="rounded">
        <span class="text-sm">Physics</span>
      </label>
      
      <!-- 계층 구조 체크박스 -->
      <label class="inline-flex items-center gap-2 bg-white px-3 py-2 rounded-md shadow">
        <input type="checkbox" v-model="hierarchical" class="rounded">
        <span class="text-sm">Hierarchical</span>
      </label>
      
      <!-- Fit 버튼 -->
      <button @click="fit" class="px-3 py-2 rounded-md bg-white shadow hover:bg-gray-50">
        Fit
      </button>
      
    </div>

    <!-- 그래프 컨테이너 -->
    <div :style="{ height: height }" class="bg-white rounded-lg shadow relative">
      <div id="graph-container" ref="container" class="absolute inset-0 rounded-lg"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import type { 
  GraphStatus, 
  MockGraphData 
} from '../types'
import { useEventBus, EVENTS } from '../composables/useEventBus'

// vis.js는 전역으로 로드되므로 window에서 가져옴
declare global {
  interface Window {
    vis: {
      Network: any
      DataSet: any
    }
  }
}

// Props 정의
interface Props {
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: '540px'
})

// 반응성 데이터
const container = ref<HTMLElement | null>(null)
const network = ref<any>(null) // vis.Network 인스턴스

// UI 상태
const physics = ref<boolean>(true)
const hierarchical = ref<boolean>(false)

// 모크 온톨로지 데이터
const mockData = reactive<MockGraphData>({
  nodes: [
    // Problems (Top Level)
    { id: 'p1', label: 'System Downtime', group: 'Problem' },
    { id: 'p2', label: 'Service Degradation', group: 'Problem' },
    { id: 'p3', label: 'Data Inconsistency', group: 'Problem' },
    { id: 'p4', label: 'Security Breach', group: 'Problem' },
    
    // Errors (Mid Level)
    { id: 'e1', label: 'Database Connection Failed', group: 'Error' },
    { id: 'e2', label: 'Memory Overflow', group: 'Error' },
    { id: 'e3', label: 'API Timeout', group: 'Error' },
    { id: 'e4', label: 'Authentication Failed', group: 'Error' },
    { id: 'e5', label: 'Cache Miss', group: 'Error' },
    { id: 'e6', label: 'Transaction Rollback', group: 'Error' },
    { id: 'e7', label: 'SSL Handshake Failed', group: 'Error' },
    
    // Root Causes (Lower Level)
    { id: 'c1', label: 'Network Latency', group: 'Root Cause' },
    { id: 'c2', label: 'Resource Leak', group: 'Root Cause' },
    { id: 'c3', label: 'CPU Overload', group: 'Root Cause' },
    { id: 'c4', label: 'Disk I/O Bottleneck', group: 'Root Cause' },
    { id: 'c5', label: 'Insufficient Memory', group: 'Root Cause' },
    { id: 'c6', label: 'Expired Certificate', group: 'Root Cause' },
    { id: 'c7', label: 'Configuration Error', group: 'Root Cause' },
    { id: 'c8', label: 'Load Balancer Failure', group: 'Root Cause' },
    
    // Metrics (Monitoring)
    { id: 'm1', label: 'Response Time', group: 'Metric' },
    { id: 'm2', label: 'CPU Usage', group: 'Metric' },
    { id: 'm3', label: 'Memory Usage', group: 'Metric' },
    { id: 'm4', label: 'Error Rate', group: 'Metric' },
    { id: 'm5', label: 'Throughput', group: 'Metric' },
    { id: 'm6', label: 'Connection Count', group: 'Metric' },
    
    // Solutions (Bottom Level)
    { id: 's1', label: 'Connection Pool Optimization', group: 'Solution' },
    { id: 's2', label: 'Memory Leak Fix', group: 'Solution' },
    { id: 's3', label: 'Load Balancing', group: 'Solution' },
    { id: 's4', label: 'Certificate Renewal', group: 'Solution' },
    { id: 's5', label: 'Database Indexing', group: 'Solution' },
    { id: 's6', label: 'Cache Warmup', group: 'Solution' },
    { id: 's7', label: 'Resource Scaling', group: 'Solution' }
  ],
  edges: [
    // Problems -> Errors
    { id: 'pe1', from: 'p1', to: 'e1', label: 'manifests as' },
    { id: 'pe2', from: 'p1', to: 'e3', label: 'manifests as' },
    { id: 'pe3', from: 'p2', to: 'e2', label: 'manifests as' },
    { id: 'pe4', from: 'p2', to: 'e5', label: 'manifests as' },
    { id: 'pe5', from: 'p3', to: 'e6', label: 'manifests as' },
    { id: 'pe6', from: 'p4', to: 'e4', label: 'manifests as' },
    { id: 'pe7', from: 'p4', to: 'e7', label: 'manifests as' },
    
    // Errors -> Root Causes
    { id: 'ec1', from: 'e1', to: 'c1', label: 'caused by' },
    { id: 'ec2', from: 'e1', to: 'c7', label: 'caused by' },
    { id: 'ec3', from: 'e2', to: 'c2', label: 'caused by' },
    { id: 'ec4', from: 'e2', to: 'c5', label: 'caused by' },
    { id: 'ec5', from: 'e3', to: 'c3', label: 'caused by' },
    { id: 'ec6', from: 'e3', to: 'c8', label: 'caused by' },
    { id: 'ec7', from: 'e4', to: 'c6', label: 'caused by' },
    { id: 'ec8', from: 'e5', to: 'c4', label: 'caused by' },
    { id: 'ec9', from: 'e6', to: 'c4', label: 'caused by' },
    { id: 'ec10', from: 'e7', to: 'c6', label: 'caused by' },
    
    // Root Causes -> Solutions
    { id: 'cs1', from: 'c1', to: 's1', label: 'resolved by' },
    { id: 'cs2', from: 'c2', to: 's2', label: 'resolved by' },
    { id: 'cs3', from: 'c3', to: 's7', label: 'resolved by' },
    { id: 'cs4', from: 'c4', to: 's5', label: 'resolved by' },
    { id: 'cs5', from: 'c5', to: 's7', label: 'resolved by' },
    { id: 'cs6', from: 'c6', to: 's4', label: 'resolved by' },
    { id: 'cs7', from: 'c7', to: 's1', label: 'resolved by' },
    { id: 'cs8', from: 'c8', to: 's3', label: 'resolved by' },
    
    // Metrics -> Problems (Detection)
    { id: 'mp1', from: 'm1', to: 'p1', label: 'detects' },
    { id: 'mp2', from: 'm1', to: 'p2', label: 'detects' },
    { id: 'mp3', from: 'm2', to: 'p2', label: 'detects' },
    { id: 'mp4', from: 'm3', to: 'p2', label: 'detects' },
    { id: 'mp5', from: 'm4', to: 'p3', label: 'detects' },
    { id: 'mp6', from: 'm5', to: 'p2', label: 'detects' },
    { id: 'mp7', from: 'm6', to: 'p1', label: 'detects' },
    
    // Solutions -> Metrics (Improvement)
    { id: 'sm1', from: 's1', to: 'm1', label: 'improves' },
    { id: 'sm2', from: 's1', to: 'm6', label: 'improves' },
    { id: 'sm3', from: 's2', to: 'm3', label: 'improves' },
    { id: 'sm4', from: 's3', to: 'm5', label: 'improves' },
    { id: 'sm5', from: 's5', to: 'm1', label: 'improves' },
    { id: 'sm6', from: 's6', to: 'm4', label: 'improves' },
    { id: 'sm7', from: 's7', to: 'm2', label: 'improves' },
    { id: 'sm8', from: 's7', to: 'm3', label: 'improves' }
  ]
})
// vis.js 옵션 계산 속성
const visOptions = computed(() => ({
  physics: { 
    enabled: physics.value, 
    stabilization: { iterations: 120 } 
  },
  layout: hierarchical.value ? { 
    hierarchical: { 
      direction: 'LR', 
      sortMethod: 'directed', 
      levelSeparation: 150 
    } 
  } : {},
  interaction: { 
    hover: true, 
    tooltipDelay: 120 
  },
  nodes: {
    shape: 'box', 
    borderWidth: 1, 
    margin: 8,
    font: { 
      multi: 'md', 
      face: 'ui-sans-serif, system-ui', 
      size: 12 
    }
  },
  edges: { 
    arrows: 'to', 
    smooth: { type: 'dynamic' }, 
    font: { size: 10, align: 'top' } 
  }
}))

// 모크 그래프 렌더링
const renderMock = async (): Promise<void> => {
  await nextTick()
  
  const data = {
    nodes: new window.vis.DataSet(mockData.nodes),
    edges: new window.vis.DataSet(mockData.edges)
  }
  
  if (network.value) {
    network.value.destroy()
  }
  
  if (container.value) {
    network.value = new window.vis.Network(container.value, data, visOptions.value)
  }
}

// 그래프 피팅
const fit = (): void => {
  if (network.value) {
    network.value.fit({ animation: true })
  }
}

// 노드 하이라이트 및 확대
const highlightNode = (nodeLabel: string): void => {
  if (!network.value) return
  
  // 라벨로 노드 찾기
  const targetNode = mockData.nodes.find(node => 
    node.label.toLowerCase().includes(nodeLabel.toLowerCase())
  )
  
  if (targetNode) {
    // 노드 포커스 및 확대
    network.value.focus(targetNode.id, {
      scale: 2.0,
      animation: {
        duration: 1000,
        easingFunction: 'easeInOutQuad'
      }
    })
    
    // 노드 선택하여 하이라이트
    network.value.selectNodes([targetNode.id])
    
    // 3초 후 선택 해제
    setTimeout(() => {
      if (network.value) {
        network.value.unselectAll()
      }
    }, 3000)
  }
}

// 텍스트에서 문제 키워드 검색 및 하이라이트
const highlightFromText = (text: string): void => {
  const problemKeywords = [
    'System Downtime',
    'Service Degradation', 
    'Data Inconsistency',
    'Security Breach'
  ]
  
  const foundKeywords: string[] = []
  
  // Problem 키워드만 찾기
  for (const keyword of problemKeywords) {
    if (text.toLowerCase().includes(keyword.toLowerCase())) {
      foundKeywords.push(keyword)
    }
  }
  
  // 순서대로 하이라이트 (딜레이 추가)
  foundKeywords.forEach((keyword, index) => {
    setTimeout(() => {
      highlightNode(keyword)
    }, index * 1500) // 1.5초 간격으로 순차 하이라이트
  })
}

// Event Bus 초기화
const { on, off } = useEventBus()

// 이벤트 핸들러
const handleHighlightText = (e: CustomEvent) => {
  if (e.detail) {
    highlightFromText(e.detail)
  }
}

const handleHighlightNode = (e: CustomEvent) => {
  if (e.detail) {
    highlightNode(e.detail)
  }
}

// 라이프사이클 훅
onMounted(async () => {
  await renderMock()
  
  // 이벤트 리스너 등록
  on(EVENTS.HIGHLIGHT_TEXT, handleHighlightText)
  on(EVENTS.HIGHLIGHT_NODE, handleHighlightNode)
})

onUnmounted(() => {
  // 이벤트 리스너 정리
  off(EVENTS.HIGHLIGHT_TEXT, handleHighlightText)
  off(EVENTS.HIGHLIGHT_NODE, handleHighlightNode)
})

// 옵션 변경 감시
watch([physics, hierarchical], async () => {
  await renderMock()
})
</script>