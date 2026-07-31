// Event Store client ? append-only event log access.
// Supports listing events, appending new events, and time-travel replay.

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080/api/v1";

export interface UniverseEvent {
  event_id: string;
  event_type: string;
  node_id?: string;
  node_type?: string;
  payload: Record<string, unknown>;
  timestamp: string;
  actor: string;
}

export interface EventStoreStats {
  total_events: number;
  event_types: string[];
  affected_nodes: number;
  date_range: { first: string | null; last: string | null };
}

export async function listEvents(params?: {
  limit?: number;
  offset?: number;
  nodeId?: string;
  eventType?: string;
}): Promise<{ count: number; events: UniverseEvent[] }> {
  const qs = new URLSearchParams();
  if (params?.limit) qs.set("limit", String(params.limit));
  if (params?.offset) qs.set("offset", String(params.offset));
  if (params?.nodeId) qs.set("node_id", params.nodeId);
  if (params?.eventType) qs.set("event_type", params.eventType);
  const res = await fetch(API_BASE + "/universe/events?" + qs.toString());
  return res.json();
}

export async function appendEvent(data: {
  event_type: string;
  node_id?: string;
  node_type?: string;
  payload?: Record<string, unknown>;
  actor?: string;
}): Promise<{ status: string; event_id: string; timestamp: string }> {
  const res = await fetch(API_BASE + "/universe/events", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function replayEvents(at?: string): Promise<Record<string, unknown>> {
  const qs = at ? "?at=" + encodeURIComponent(at) : "";
  const res = await fetch(API_BASE + "/universe/events/replay" + qs);
  return res.json();
}

export async function eventStoreStats(): Promise<EventStoreStats> {
  const res = await fetch(API_BASE + "/universe/events/stats");
  return res.json();
}
