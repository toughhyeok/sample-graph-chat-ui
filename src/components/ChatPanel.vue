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
        placeholder="Ask about root causes and causal relationships... (Ctrl/⌘+Enter to send)"
        class="flex-1 resize-none rounded-lg border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow"
      />
      <button 
        @click="send" 
        :disabled="isLoading"
        :class="[
          'px-5 py-2 rounded-lg shadow transition',
          isLoading 
            ? 'bg-gray-400 text-gray-600 cursor-not-allowed' 
            : 'bg-blue-600 text-white hover:bg-blue-700'
        ]"
      >
        {{ isLoading ? 'Sending...' : 'Send' }}
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

// 로딩 상태
const isLoading = ref<boolean>(false)

// 메소드들
const send = async (): Promise<void> => {
  const text = input.value.trim()
  if (!text || isLoading.value) return
  
  // 사용자 메시지 추가
  const userMessage: ChatMessage = { role: 'user', text, timestamp: dayjs() }
  messages.value.push(userMessage)
  input.value = ''
  isLoading.value = true
  
  try {
    // FastAPI 서버로 직접 요청
    const claudeMessages = messages.value
      .filter((msg: ChatMessage) => msg.text.trim())
      .map((msg: ChatMessage) => ({
        role: msg.role,
        content: msg.text
      }))

    const response = await fetch('/api/claude/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: claudeMessages
      })
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`API error: ${response.status} - ${errorText}`)
    }

    const data = await response.json()
    
    if (data.content && data.content.length > 0) {
      // Assistant 응답 추가
      messages.value.push({
        role: 'assistant',
        text: data.content[0].text,
        timestamp: dayjs()
      })
    } else {
      throw new Error('No content in response')
    }
    
  } catch (error) {
    console.error('Failed to get response:', error)
    
    // 에러 발생 시 대체 메시지
    messages.value.push({
      role: 'assistant',
      text: `I apologize, but I'm currently unable to process your request. Please check your API configuration and try again. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      timestamp: dayjs()
    })
  } finally {
    isLoading.value = false
  }
}

const handleKey = (event: KeyboardEvent): void => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter' && !isLoading.value) {
    event.preventDefault()
    send()
  }
}
</script>