<template>
  <div class="min-h-screen bg-gray-100">
    <!-- 헤더 -->
    <header class="sticky top-0 z-10 bg-white/80 backdrop-blur border-b">
      <div class="max-w-7xl mx-auto px-4 py-3">
        <h1 class="text-xl font-semibold tracking-tight">
          Neo4j Graph + LLM Chat (Vue 3 + Tailwind)
        </h1>
      </div>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="max-w-7xl mx-auto p-4 grid lg:grid-cols-2 gap-4">
      <!-- 그래프 섹션 -->
      <section class="lg:col-span-1">
        <div class="p-4 bg-white rounded-2xl shadow h-full">
          <h2 class="text-lg font-semibold mb-3">그래프 탐색</h2>
          <GraphPanel height="560px" />
        </div>
      </section>

      <!-- 채팅 섹션 -->
      <section class="lg:col-span-1">
        <div class="p-4 bg-white rounded-2xl shadow h-full">
          <h2 class="text-lg font-semibold mb-3">LLM 채팅</h2>
          <div class="h-[560px]">
            <ChatPanel />
          </div>
        </div>
      </section>
    </main>

    <!-- 푸터 -->
    <footer class="max-w-7xl mx-auto px-4 py-6 text-sm text-gray-500">
      <p>
        🧩 교체 포인트: 실제 백엔드 연결 시 GraphPanel에서 
        <code class="bg-gray-100 px-1 rounded">mode='neovis'</code>와 Neo4j 접속 정보를 사용하세요. 
        채팅은 백엔드 API 호출로 대체.
      </p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import ChatPanel from './components/ChatPanel.vue'
import GraphPanel from './components/GraphPanel.vue'
</script>