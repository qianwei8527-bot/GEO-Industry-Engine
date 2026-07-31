const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8080/api/v1';

interface RequestOptions { method?: string; body?: unknown; token?: string; }
async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, token } = options;
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = 'Bearer ' + token;
  const res = await fetch(API_BASE + path, {
    method, headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) { const e = await res.json().catch(() => ({ detail: 'Request failed' })); throw new Error(e.detail || 'Request failed'); }
  return res.json();
}

export const api = {
  auth: {
    register: (d: { email: string; password: string; name: string }) => apiRequest('/auth/register', { method: 'POST', body: d }),
    login: (d: { email: string; password: string }) => apiRequest('/auth/login', { method: 'POST', body: d }),
  },
  users: { me: (t: string) => apiRequest('/users/me', { token: t }) },
  entities: {
    list: (type?: string) => apiRequest('/entities/?' + (type ? 'entity_type=' + type : '')),
    get: (id: string) => apiRequest('/entities/' + id),
  },
  companies: {
    list: (industry?: string) => apiRequest('/companies/?' + (industry ? 'industry_id=' + industry : '')),
    get: (id: string) => apiRequest('/companies/' + id),
  },
  industries: {
    list: () => apiRequest('/industries/'),
    get: (id: string) => apiRequest('/industries/' + id),
  },
  context: {
    company: (id: string) => apiRequest('/context/company/' + id),
    industry: (id: string) => apiRequest('/context/industry/' + id),
    capability: (id: string) => apiRequest('/context/capability/' + id),
    query: (q: string, limit = 10) => apiRequest('/context/query', { method: 'POST', body: { query: q, limit } }),
  },
  decision: {
    company: (id: string) => apiRequest('/decision/company/' + id),
    industry: (id: string) => apiRequest('/decision/industry/' + id),
    analyze: (q: string) => apiRequest('/decision/analyze', { method: 'POST', body: { query: q } }),
  },
  evidence: {
    list: (targetId?: string) => apiRequest('/evidence/?' + (targetId ? 'target_id=' + targetId : '')),
    create: (d: any) => apiRequest('/evidence/', { method: 'POST', body: d }),
  },
  relationships: { list: () => apiRequest('/relationships/') },
  admin: {
    listConfigs: () => apiRequest<Record<string,string[]>>('/admin/configs/'),
    getConfig: (name: string) => apiRequest('/admin/configs/' + name),
    saveConfig: (name: string, value: any) => apiRequest('/admin/configs/' + name, { method: 'PUT', body: { name, value } }),
    dbStats: () => apiRequest<{counts:Record<string,number>;total:number;timestamp:string}>('/admin/db-stats'),
    health: () => apiRequest<{status:string;db:string;version:string}>('/admin/health'),
    stats: () => apiRequest<{total_configs:number;categories:number;version:string}>('/admin/stats'),
    listIndustries: () => apiRequest<any[]>('/admin/industries'),
    listCompanies: () => apiRequest<any[]>('/admin/companies'),
  },
  certification: {
    list: () => apiRequest<any[]>('/certifications/'),
    get: (id: string) => apiRequest<{id:string;status:string;level:string}>('/certifications/' + id),
    status: (entityId: string) => apiRequest<any[]>('/certification/status/' + entityId),
    apply: (d: any) => apiRequest('/certifications/apply', { method: 'POST', body: d }),
    review: (certId: string, action: string, comment?: string) => apiRequest('/certification/review/' + certId, { method: 'PUT', body: { action, comment } }),
    listPending: () => apiRequest<any[]>('/certification/review/pending'),
  },
  marketplace: {
    listProviders: () => apiRequest('/marketplace/providers/'),
    listDemands: () => apiRequest('/marketplace/demands/'),
    getProvider: (id: string) => apiRequest('/marketplace/providers/' + id),
    getDemand: (id: string) => apiRequest('/marketplace/demands/' + id),
  },
  agent: {
    analyze: (q: string, params?: Record<string,any>) => apiRequest('/agent/analyze', { method: 'POST', body: { query: q, params: params || {} } }),
    report: (companyId: string) => apiRequest('/agent/report/' + companyId),
    diagnose: (companyId: string) => apiRequest('/agent/diagnose/' + companyId),
    match: (params: { demand_id?: string; industry_id?: string; company_id?: string }) => apiRequest('/agent/match', { method: 'POST', body: params }),
    compare: (companyId: string, competitorIds: string[]) => apiRequest('/agent/compare', { method: 'POST', body: { company_id: companyId, competitor_ids: competitorIds } }),
  },
  assets: {
    overview: () => apiRequest('/assets/overview'),
    capabilities: () => apiRequest('/assets/capabilities'),
    industries: () => apiRequest('/assets/industries'),
    opportunities: () => apiRequest('/assets/opportunities'),
  },
  universe: {
    rules: (category?: string) => apiRequest('/universe/rules' + (category ? '?category=' + category : '')),
    cite: (ruleId: string, explanation: string) => apiRequest('/universe/cite', { method: 'POST', body: { rule_id: ruleId, explanation } }),
    panel: (nodeType: string, nodeId: string) => apiRequest('/universe/panel/' + nodeType + '/' + nodeId),
  },
  graph: {
    overview: () => apiRequest('/graph/overview'),
    ecosystem: (industryId?: string) => apiRequest(industryId ? '/graph/ecosystem/' + industryId : '/graph/ecosystem'),
    business: (industryId: string) => apiRequest('/graph/business/' + industryId),
    growth: (industryId: string) => apiRequest('/graph/growth/' + industryId),
    distribution: (industryId: string) => apiRequest('/graph/distribution/' + industryId),
    future: (industryId: string) => apiRequest('/graph/future/' + industryId),
    nodeDetail: (type: string, id: string) => apiRequest('/graph/nodes/' + type + '/' + id),
  },
  identity: {
    profiles: (params?: Record<string,string>) => {
      const qs = params ? '?' + new URLSearchParams(params).toString() : '';
      return apiRequest('/universe/identity/profiles' + qs);
    },
    profile: (entityId: string) => apiRequest('/universe/identity/profile/' + entityId),
    createProfile: (data: Record<string,any>) => apiRequest('/universe/identity/profile', { method: 'POST', body: data }),
    snapshots: (entityId: string) => apiRequest('/universe/identity/snapshots/' + entityId),
    latestSnapshot: (entityId: string) => apiRequest('/universe/identity/snapshots/' + entityId + '/latest'),
    createSnapshot: (data: Record<string,any>) => apiRequest('/universe/identity/snapshot', { method: 'POST', body: data }),
  }
};
