<template>
  <div class="flex flex-col h-full">
    <!-- 메시지 영역 -->
    <div class="flex-1 overflow-y-auto space-y-3 p-3 rounded-2xl bg-white shadow-inner">
      <div 
        v-for="(message, index) in messages" 
        :key="index" 
        class="flex" 
        :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div 
          :class="[
            'max-w-[80%] px-4 py-2 rounded-2xl shadow',
            message.role === 'user' 
              ? 'bg-blue-600 text-white rounded-br-sm' 
              : 'bg-gray-100 text-gray-900 rounded-bl-sm'
          ]"
        >
          {{ message.text }}
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
        class="flex-1 resize-none rounded-2xl border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow"
      />
      <button 
        @click="send" 
        class="px-5 py-2 rounded-2xl bg-blue-600 text-white shadow hover:bg-blue-700 transition"
      >
        보내기
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ChatMessage } from '../types'

// 반응성 데이터
const messages = ref<ChatMessage[]>([
  { role: 'assistant', text: '안녕하세요! 그래프에서 궁금한 걸 물어보세요 😊' }
])

const input = ref('노드 간 연결 규칙을 요약해줘 (예시)')

// 메소드들
const send = (): void => {
  const text = input.value.trim()
  if (!text) return
  
  // 사용자 메시지 추가
  messages.value.push({ role: 'user', text })
  
  // 플레이스홀더 응답 (실제로는 API 호출로 대체)
  setTimeout(() => {
    messages.value.push({
      role: 'assistant',
      text: '응답 예시: 해당 질문은 백엔드 LLM API와 연동하면 실제 답변으로 대체됩니다.'
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