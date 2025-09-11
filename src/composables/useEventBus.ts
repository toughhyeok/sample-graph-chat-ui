import { ref } from 'vue'

// 전역 이벤트 버스
const eventTarget = ref(new EventTarget())

export const useEventBus = () => {
  const emit = (event: string, data?: any) => {
    eventTarget.value.dispatchEvent(
      new CustomEvent(event, { detail: data })
    )
  }

  const on = (event: string, callback: (e: CustomEvent) => void) => {
    eventTarget.value.addEventListener(event, callback as EventListener)
  }

  const off = (event: string, callback: (e: CustomEvent) => void) => {
    eventTarget.value.removeEventListener(event, callback as EventListener)
  }

  return {
    emit,
    on,
    off
  }
}

// 이벤트 타입 정의
export const EVENTS = {
  HIGHLIGHT_TEXT: 'highlight-text',
  HIGHLIGHT_NODE: 'highlight-node'
} as const