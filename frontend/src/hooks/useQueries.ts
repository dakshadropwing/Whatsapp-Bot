import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

// ── Analytics ─────────────────────────────────────────────
export const useAnalyticsStats = () => {
  return useQuery({
    queryKey: ["analytics", "stats"],
    queryFn: async () => {
      const { data } = await api.get("/analytics/stats");
      return data;
    },
  });
};

export const useAnalyticsOverview = (period = "7d") => {
  return useQuery({
    queryKey: ["analytics", "overview", period],
    queryFn: async () => {
      const { data } = await api.get(`/analytics/overview?period=${period}`);
      return data;
    },
  });
};

// ── Conversations ─────────────────────────────────────────
export const useConversations = (params?: { status?: string; search?: string }) => {
  return useQuery({
    queryKey: ["conversations", params],
    queryFn: async () => {
      const { data } = await api.get("/conversations", { params });
      return data.items || data;
    },
    refetchInterval: 5000, // Poll every 5 seconds for real-time feel
  });
};

export const useMessages = (conversationId: string | null) => {
  return useQuery({
    queryKey: ["messages", conversationId],
    queryFn: async () => {
      if (!conversationId) return [];
      const { data } = await api.get(`/conversations/${conversationId}/messages`);
      return data.items || data;
    },
    enabled: !!conversationId,
    refetchInterval: 3000,
  });
};

// ── Tickets ───────────────────────────────────────────────
export const useTickets = (params?: { status?: string }, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: ["tickets", params],
    queryFn: async () => {
      const { data } = await api.get("/tickets", { params });
      return data.items || data;
    },
    enabled: options?.enabled,
  });
};

// ── Agents ────────────────────────────────────────────────
export const useAgents = () => {
  return useQuery({
    queryKey: ["agents"],
    queryFn: async () => {
      const { data } = await api.get("/agents");
      return data.items || data;
    },
  });
};

// ── Workflows ─────────────────────────────────────────────
export const useWorkflows = () => {
  return useQuery({
    queryKey: ["workflows"],
    queryFn: async () => {
      const { data } = await api.get("/workflows");
      return data.items || data;
    },
  });
};

// ── Clients ───────────────────────────────────────────────
export const useClients = (params?: { search?: string }) => {
  return useQuery({
    queryKey: ["clients", params],
    queryFn: async () => {
      const { data } = await api.get("/clients", { params });
      return data.items || data;
    },
  });
};

// ── Users ─────────────────────────────────────────────────
export const useUsers = () => {
  return useQuery({
    queryKey: ["users"],
    queryFn: async () => {
      const { data } = await api.get("/users");
      return data.items || data;
    },
  });
};

// ── Prompts ───────────────────────────────────────────────
export const usePrompts = () => {
  return useQuery({
    queryKey: ["prompts"],
    queryFn: async () => {
      const { data } = await api.get("/prompts");
      return data.items || data;
    },
  });
};

// ── Settings ──────────────────────────────────────────────
export const useSettings = () => {
  return useQuery({
    queryKey: ["settings"],
    queryFn: async () => {
      const { data } = await api.get("/settings");
      return data;
    },
  });
};

// ── Employees ─────────────────────────────────────────────
export const useEmployees = (params?: { search?: string; page?: number; per_page?: number }) => {
  return useQuery({
    queryKey: ["employees", params],
    queryFn: async () => {
      const { data } = await api.get("/employees", { params });
      return data.employees || data.data || data;
    },
  });
};

// ── Endpoints ─────────────────────────────────────────────
export const useEndpoints = (params?: { page?: number; per_page?: number }) => {
  return useQuery({
    queryKey: ["endpoints", params],
    queryFn: async () => {
      const { data } = await api.get("/endpoints", { params });
      return data.endpoints || data.data || data;
    },
  });
};

// ── Audit Logs ────────────────────────────────────────────
export const useAuditLogs = (params?: { page?: number; per_page?: number; action?: string; resource_type?: string }) => {
  return useQuery({
    queryKey: ["audit", params],
    queryFn: async () => {
      const { data } = await api.get("/audit", { params });
      return data.logs || data.data || data;
    },
  });
};

// ── WhatsApp ──────────────────────────────────────────────
export const useWhatsAppAccounts = () => {
  return useQuery({
    queryKey: ["whatsapp", "accounts"],
    queryFn: async () => {
      const { data } = await api.get("/whatsapp/accounts");
      return data.accounts || data.data || data;
    },
  });
};
