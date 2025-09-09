<template>
  <div class="space-y-3">
    <!-- 컨트롤 패널 -->
    <div class="flex flex-wrap items-center gap-2">
      <!-- 모드 선택 -->
      <div class="inline-flex bg-white rounded-2xl shadow overflow-hidden">
        <button 
          @click="switchMode('mock')" 
          :class="[
            'px-3 py-2', 
            mode === 'mock' ? 'bg-gray-900 text-white' : 'text-gray-700'
          ]"
        >
          Mock
        </button>
        <button 
          @click="switchMode('neovis')" 
          :class="[
            'px-3 py-2', 
            mode === 'neovis' ? 'bg-gray-900 text-white' : 'text-gray-700'
          ]"
        >
          Neo4j (NeoVis)
        </button>
      </div>
      
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

    <!-- Neo4j 연결 설정 (neovis 모드일 때만 표시) -->
    <div v-if="mode === 'neovis'" class="grid md:grid-cols-5 gap-2 bg-white p-3 rounded-2xl shadow">
      <input 
        v-model="neo4j.url" 
        placeholder="bolt://host:7687" 
        class="md:col-span-2 rounded-xl border p-2" 
      />
      <input 
        v-model="neo4j.user" 
        placeholder="neo4j" 
        class="rounded-xl border p-2" 
      />
      <input 
        v-model="neo4j.password" 
        placeholder="password" 
        type="password" 
        class="rounded-xl border p-2" 
      />
      <input 
        v-model="neo4j.database" 
        placeholder="neo4j" 
        class="rounded-xl border p-2" 
      />
      <input 
        v-model="neo4j.initialCypher" 
        placeholder="MATCH (n)-[r]->(m) RETURN n,r,m LIMIT 50" 
        class="md:col-span-4 rounded-xl border p-2" 
      />
      <button 
        @click="switchMode('neovis')" 
        class="md:col-span-1 px-3 py-2 rounded-xl bg-blue-600 text-white shadow hover:bg-blue-700"
      >
        Connect
      </button>
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
  GraphMode, 
  GraphStatus, 
  Neo4jConfig, 
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
const viz = ref<any>(null) // NeoVis 인스턴스

// UI 상태
const mode = ref<GraphMode>('mock')
const physics = ref<boolean>(true)
const hierarchical = ref<boolean>(false)
const status = ref<GraphStatus>('ready')

// Neo4j 연결 설정
const neo4j = reactive<Neo4jConfig>({
  url: 'bolt://localhost:7687',
  user: 'neo4j',
  password: 'password',
  database: 'neo4j',
  initialCypher: 'MATCH (n)-[r]->(m) RETURN n,r,m LIMIT 50'
})

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

// NeoVis 유틸리티 함수
const resolveNeoVis = (): any => {
  const g = window as any
  return g.NeoVis?.NeoVis || g.NeoVis?.default || g.NeoVis || null
}

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

// NeoVis 그래프 렌더링
const renderNeoVis = async (): Promise<void> => {
  const NeoVisClass = resolveNeoVis()
  if (!NeoVisClass) {
    console.warn('NeoVis library not detected. Check CDN script tag.')
    status.value = 'error'
    return
  }
  
  status.value = 'connecting'
  await nextTick()

  // 기존 네트워크 정리
  if (network.value) {
    network.value.destroy()
    network.value = null
  }
  
  if (viz.value) {
    try {
      viz.value.clearNetwork()
    } catch (_) {
      // 에러 무시
    }
    viz.value = null
  }

  const config = {
    containerId: container.value?.id || 'graph-container',
    neo4j: {
      serverUrl: neo4j.url,
      serverUser: neo4j.user,
      serverPassword: neo4j.password,
      database: neo4j.database
    },
    labels: {
      Person: { caption: 'name' },
      Company: { caption: 'name' },
      Technology: { caption: 'name' },
      Concept: { caption: 'name' },
    },
    relationships: {
      WORKS_AT: { caption: true },
      USES: { caption: true },
      MODELS: { caption: true },
      VISUALIZES: { caption: true },
    },
    visConfig: visOptions.value,
    initialCypher: neo4j.initialCypher
  }

  try {
    viz.value = new NeoVisClass(config)
    viz.value.render()
    status.value = 'ready'
  } catch (err) {
    console.error(err)
    status.value = 'error'
  }
}

// 모드 전환
const switchMode = async (newMode: GraphMode): Promise<void> => {
  mode.value = newMode
  if (newMode === 'mock') {
    await renderMock()
  } else {
    await renderNeoVis()
  }
}

// 그래프 피팅
const fit = (): void => {
  if (mode.value === 'mock' && network.value) {
    network.value.fit({ animation: true })
  }
  // NeoVis는 내부적으로 vis 네트워크를 사용
  if (mode.value === 'neovis' && viz.value && viz.value._network) {
    viz.value._network.fit({ animation: true })
  }
}

// 라이프사이클 훅
onMounted(async () => {
  await renderMock()
})

// 옵션 변경 감시
watch([physics, hierarchical], async () => {
  if (mode.value === 'mock') {
    await renderMock()
  } else {
    await renderNeoVis()
  }
})
</script>