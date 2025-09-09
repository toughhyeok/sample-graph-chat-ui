<template>
  <div class="flex flex-col h-full">
    <!-- 메시지 영역 -->
    <div class="flex-1 overflow-y-auto space-y-3 p-3 rounded-lg bg-white shadow-inner">
      <div 
        v-for="(message, index) in messages" 
        :key="index" 
        class="flex flex-col" 
        :class="message.role === 'user' ? 'items-end' : 'items-start'"
      >
        <div 
          :class="[
            'max-w-[80%] px-4 py-2 rounded-lg shadow',
            message.role === 'user' 
              ? 'bg-blue-600 text-white rounded-br-sm' 
              : 'bg-gray-100 text-gray-900 rounded-bl-sm'
          ]"
        >
          {{ message.text }}
        </div>
        <div class="text-xs text-gray-400 mt-1">
          {{ formatTime(message.timestamp) }}
        </div>
      </div>
    </div>
    
    <!-- 입력 영역 -->
    <div class="mt-3 flex gap-2">
      <textarea 
        v-model="input" 
        @keydown="handleKey"
        rows="2" 
        placeholder="메시지를 입력하고 Ctrl/⌘+Enter로 전송"
        class="flex-1 resize-none rounded-lg border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow"
      />
      <button 
        @click="send" 
        class="px-5 py-2 rounded-lg bg-blue-600 text-white shadow hover:bg-blue-700 transition"
      >
        보내기
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import dayjs from 'dayjs'
import type { ChatMessage } from '../types'

// 반응성 데이터
const messages = ref<ChatMessage[]>([
  { role: 'assistant', text: 'Welcome to RAPTOR! I can help you analyze causal relationships and identify root causes from the ontology. What would you like to investigate?', timestamp: dayjs() }
])

const input = ref('What is the root cause of the system failure?')

// 시간 포맷팅 함수
const formatTime = (timestamp: any): string => {
  return timestamp.format('HH:mm')
}

// 메소드들
const send = (): void => {
  const text = input.value.trim()
  if (!text) return
  
  // 사용자 메시지 추가
  messages.value.push({ role: 'user', text, timestamp: dayjs() })
  
  // 플레이스홀더 응답 (실제로는 API 호출로 대체)
  setTimeout(() => {
    messages.value.push({
      role: 'assistant',
      text: 'Based on the ontology analysis, I can identify potential causal chains and root causes. This response will be powered by the backend LLM API when integrated.',
      timestamp: dayjs()
    })
  }, 300)
  
  input.value = ''
}

const handleKey = (event: KeyboardEvent): void => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    send()
  }
}
</script>