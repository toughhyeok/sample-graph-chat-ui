<template>
  <div class="space-y-3">
    <!-- 컨트롤 패널 -->
    <div class="flex flex-wrap items-center gap-2">
      <!-- 물리 효과 체크박스 -->
      <label class="inline-flex items-center gap-2 bg-white px-3 py-2 rounded-2xl shadow">
        <input type="checkbox" v-model="physics" class="rounded">
        <span class="text-sm">Physics</span>
      </label>
      
      <!-- 계층 구조 체크박스 -->
      <label class="inline-flex items-center gap-2 bg-white px-3 py-2 rounded-2xl shadow">
        <input type="checkbox" v-model="hierarchical" class="rounded">
        <span class="text-sm">Hierarchical</span>
      </label>
      
      <!-- Fit 버튼 -->
      <button @click="fit" class="px-3 py-2 rounded-2xl bg-white shadow hover:bg-gray-50">
        Fit
      </button>
      
      <!-- 상태 표시 -->
      <span class="text-sm text-gray-500">Status: {{ status }}</span>
    </div>

    <!-- 그래프 컨테이너 -->
    <div :style="{ height: height }" class="bg-white rounded-2xl shadow relative">
      <div id="graph-container" ref="container" class="absolute inset-0 rounded-2xl"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import type { 
  GraphStatus, 
  MockGraphData 
} from '../types'

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
const status = ref<GraphStatus>('ready')

// 모크 온톨로지 데이터
const mockData = reactive<MockGraphData>({
  nodes: [
    { id: 'p1', label: 'Person\nAlice', group: 'Person' },
    { id: 'p2', label: 'Person\nBob', group: 'Person' },
    { id: 'c1', label: 'Company\nAcme Corp', group: 'Company' },
    { id: 't1', label: 'Tech\nNeo4j', group: 'Technology' },
    { id: 't2', label: 'Tech\nVue.js', group: 'Technology' },
    { id: 'o1', label: 'Ontology\nGraph', group: 'Concept' },
  ],
  edges: [
    { id: 'e1', from: 'p1', to: 'c1', label: 'WORKS_AT' },
    { id: 'e2', from: 'p2', to: 'c1', label: 'WORKS_AT' },
    { id: 'e3', from: 'c1', to: 't1', label: 'USES' },
    { id: 'e4', from: 'c1', to: 't2', label: 'USES' },
    { id: 'e5', from: 't1', to: 'o1', label: 'MODELS' },
    { id: 'e6', from: 't2', to: 'o1', label: 'VISUALIZES' },
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
  status.value = 'rendering'
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
    network.value.once('stabilized', () => {
      status.value = 'ready'
    })
  }
}

// 그래프 피팅
const fit = (): void => {
  if (network.value) {
    network.value.fit({ animation: true })
  }
}

// 라이프사이클 훅
onMounted(async () => {
  await renderMock()
})

// 옵션 변경 감시
watch([physics, hierarchical], async () => {
  await renderMock()
})
</script>