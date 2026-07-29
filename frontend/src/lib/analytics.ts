// GEO-Industry-Engine 前端埋点SDK
// 轻量化、可配置、不绑厂商

const ANALYTICS_ENDPOINT = process.env.NEXT_PUBLIC_API_URL + '/api/v1/analytics/events'
const BATCH_SIZE = 10
const FLUSH_INTERVAL_MS = 30000

let eventQueue: Array<Record<string,any>> = []
let sessionId: string = crypto.randomUUID()
let userId: string|null = null
let flushTimer: ReturnType<typeof setInterval>|null = null

function getSource(): string { return 'web' }

async function flush(): Promise<void> {
  if (eventQueue.length === 0) return
  const batch = [...eventQueue]
  eventQueue = []
  try {
    await fetch(ANALYTICS_ENDPOINT + '/batch', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ events: batch }),
    })
  } catch (e) { console.debug('Analytics flush failed:', e) }
}

function scheduleFlush() {
  if (flushTimer) return
  flushTimer = setInterval(flush, FLUSH_INTERVAL_MS)
}

const analytics = {
  identify(id: string) { userId = id },
  track(eventType: string, props: Record<string,any> = {}) {
    eventQueue.push({
      event_type: eventType,
      user_id: userId,
      session_id: sessionId,
      source: getSource(),
      client_ts: new Date().toISOString(),
      properties: props,
    })
    if (eventQueue.length >= BATCH_SIZE) flush()
  },
  trackEntityView(entityType: string, entityId: string, extra: Record<string,any> = {}) {
    this.track('entity_viewed', { entity_type: entityType, entity_id: entityId, ...extra })
  },
  trackSearch(query: string, resultCount: number, filters: Record<string,any> = {}) {
    this.track('search_performed', { query, result_count: resultCount, filters })
  },
  trackCertificationApply(entityId: string, targetLevel: string) {
    this.track('certification_applied', { entity_id: entityId, target_level: targetLevel })
  },
  flush,
}

if (typeof window !== 'undefined') {
  scheduleFlush()
  window.addEventListener('beforeunload', flush)
}

export default analytics