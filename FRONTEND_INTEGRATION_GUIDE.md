# Frontend Integration Guide - Phase 1 API

**AutoMesh Workflow Management**  
**Date:** 2025-10-01

---

## 🎯 Overview

This guide shows how to integrate the Phase 1 backend API with your React/TypeScript frontend.

---

## 📁 File Structure

```
frontend/src/
├── services/
│   └── workflow/
│       ├── workflowApi.ts          # API client (UPDATE THIS)
│       └── types.ts                # TypeScript types
├── store/
│   └── workflow/
│       └── workflowStore.ts        # State management (UPDATE THIS)
└── pages/
    └── workflow/
        └── WorkflowListPage.tsx    # UI component (UPDATE THIS)
```

---

## 1. Update API Client

**File:** `frontend/src/services/workflow/workflowApi.ts`

```typescript
import { FrappeCall } from '@/lib/frappe';

export interface WorkflowFilters {
  limit?: number;
  offset?: number;
  search?: string;
  tags?: string;
  is_active?: boolean;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface WorkflowStatistics {
  total_workflows: number;
  active_workflows: number;
  total_executions: number;
  completed: number;
  failed: number;
  failure_rate: string;
  time_saved: string;
  avg_runtime: string;
}

export const workflowApi = {
  /**
   * Get all workflows with optional filters
   */
  async getWorkflows(filters?: WorkflowFilters) {
    const response = await FrappeCall({
      method: 'automesh.automesh.api.workflow.get_workflows',
      args: filters || {},
    });
    return response.message;
  },

  /**
   * Get a single workflow by ID
   */
  async getWorkflow(workflowId: string) {
    const response = await FrappeCall({
      method: 'automesh.automesh.api.workflow.get_workflow',
      args: { workflow_id: workflowId },
    });
    return response.message;
  },

  /**
   * Create a new workflow
   */
  async createWorkflow(workflowData: any) {
    const response = await FrappeCall({
      method: 'automesh.automesh.api.workflow.create_workflow',
      args: workflowData,
    });
    return response.message;
  },

  /**
   * Update an existing workflow
   */
  async updateWorkflow(workflowId: string, workflowData: any) {
    const response = await FrappeCall({
      method: 'automesh.automesh.api.workflow.update_workflow',
      args: {
        workflow_id: workflowId,
        workflow: workflowData,
      },
    });
    return response.message;
  },

  /**
   * Delete a workflow
   */
  async deleteWorkflow(workflowId: string) {
    const response = await FrappeCall({
      method: 'automesh.automesh.api.workflow.delete_workflow',
      args: { workflow_id: workflowId },
    });
    return response.message;
  },

  /**
   * Duplicate a workflow
   */
  async duplicateWorkflow(workflowId: string, newName?: string) {
    const response = await FrappeCall({
      method: 'automesh.automesh.api.workflow.duplicate_workflow',
      args: {
        workflow_id: workflowId,
        new_name: newName,
      },
    });
    return response.message;
  },

  /**
   * Toggle workflow active status
   */
  async toggleWorkflowStatus(workflowId: string, isActive: boolean) {
    const response = await FrappeCall({
      method: 'automesh.automesh.api.workflow.toggle_workflow_status',
      args: {
        workflow_id: workflowId,
        is_active: isActive,
      },
    });
    return response.message;
  },

  /**
   * Get workflow statistics
   */
  async getStatistics(days: number = 7): Promise<WorkflowStatistics> {
    const response = await FrappeCall({
      method: 'automesh.automesh.api.workflow.get_workflow_statistics',
      args: { days },
    });
    return response.message;
  },

  /**
   * Get all available tags
   */
  async getAllTags(): Promise<string[]> {
    const response = await FrappeCall({
      method: 'automesh.automesh.api.workflow.get_all_tags',
      args: {},
    });
    return response.message;
  },
};
```

---

## 2. Update Store (State Management)

**File:** `frontend/src/store/workflow/workflowStore.ts`

```typescript
import { create } from 'zustand';
import { workflowApi, WorkflowFilters, WorkflowStatistics } from '@/services/workflow/workflowApi';
import { Workflow } from '@/services/workflow/types';

interface WorkflowStore {
  // State
  workflows: Workflow[];
  currentWorkflow: Workflow | null;
  statistics: WorkflowStatistics | null;
  tags: string[];
  loading: boolean;
  error: string | null;
  total: number;
  filters: WorkflowFilters;

  // Actions
  fetchWorkflows: (filters?: WorkflowFilters) => Promise<void>;
  fetchWorkflow: (id: string) => Promise<void>;
  createWorkflow: (data: any) => Promise<Workflow>;
  updateWorkflow: (id: string, data: any) => Promise<Workflow>;
  deleteWorkflow: (id: string) => Promise<void>;
  duplicateWorkflow: (id: string, newName?: string) => Promise<Workflow>;
  toggleWorkflowStatus: (id: string, isActive: boolean) => Promise<void>;
  fetchStatistics: (days?: number) => Promise<void>;
  fetchTags: () => Promise<void>;
  setFilters: (filters: WorkflowFilters) => void;
  clearError: () => void;
}

export const useWorkflowStore = create<WorkflowStore>((set, get) => ({
  // Initial state
  workflows: [],
  currentWorkflow: null,
  statistics: null,
  tags: [],
  loading: false,
  error: null,
  total: 0,
  filters: {},

  // Fetch workflows with filters
  fetchWorkflows: async (filters?: WorkflowFilters) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowApi.getWorkflows(filters);
      set({
        workflows: response.workflows,
        total: response.total,
        filters: filters || {},
        loading: false,
      });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  // Fetch single workflow
  fetchWorkflow: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const workflow = await workflowApi.getWorkflow(id);
      set({ currentWorkflow: workflow, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  // Create workflow
  createWorkflow: async (data: any) => {
    set({ loading: true, error: null });
    try {
      const workflow = await workflowApi.createWorkflow(data);
      set((state) => ({
        workflows: [workflow, ...state.workflows],
        total: state.total + 1,
        loading: false,
      }));
      return workflow;
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // Update workflow
  updateWorkflow: async (id: string, data: any) => {
    set({ loading: true, error: null });
    try {
      const workflow = await workflowApi.updateWorkflow(id, data);
      set((state) => ({
        workflows: state.workflows.map((w) => (w.id === id ? workflow : w)),
        currentWorkflow: state.currentWorkflow?.id === id ? workflow : state.currentWorkflow,
        loading: false,
      }));
      return workflow;
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // Delete workflow
  deleteWorkflow: async (id: string) => {
    set({ loading: true, error: null });
    try {
      await workflowApi.deleteWorkflow(id);
      set((state) => ({
        workflows: state.workflows.filter((w) => w.id !== id),
        total: state.total - 1,
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // Duplicate workflow
  duplicateWorkflow: async (id: string, newName?: string) => {
    set({ loading: true, error: null });
    try {
      const workflow = await workflowApi.duplicateWorkflow(id, newName);
      set((state) => ({
        workflows: [workflow, ...state.workflows],
        total: state.total + 1,
        loading: false,
      }));
      return workflow;
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // Toggle workflow status
  toggleWorkflowStatus: async (id: string, isActive: boolean) => {
    set({ loading: true, error: null });
    try {
      await workflowApi.toggleWorkflowStatus(id, isActive);
      set((state) => ({
        workflows: state.workflows.map((w) =>
          w.id === id
            ? { ...w, metadata: { ...w.metadata, isActive } }
            : w
        ),
        loading: false,
      }));
    } catch (error: any) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  // Fetch statistics
  fetchStatistics: async (days: number = 7) => {
    try {
      const statistics = await workflowApi.getStatistics(days);
      set({ statistics });
    } catch (error: any) {
      console.error('Failed to fetch statistics:', error);
    }
  },

  // Fetch tags
  fetchTags: async () => {
    try {
      const tags = await workflowApi.getAllTags();
      set({ tags });
    } catch (error: any) {
      console.error('Failed to fetch tags:', error);
    }
  },

  // Set filters
  setFilters: (filters: WorkflowFilters) => {
    set({ filters });
    get().fetchWorkflows(filters);
  },

  // Clear error
  clearError: () => set({ error: null }),
}));
```

---

## 3. Update UI Component

**File:** `frontend/src/pages/workflow/WorkflowListPage.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { useWorkflowStore } from '@/store/workflow/workflowStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { toast } from '@/components/ui/use-toast';

export const WorkflowListPage: React.FC = () => {
  const {
    workflows,
    statistics,
    tags,
    loading,
    error,
    total,
    fetchWorkflows,
    fetchStatistics,
    fetchTags,
    deleteWorkflow,
    duplicateWorkflow,
    toggleWorkflowStatus,
  } = useWorkflowStore();

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [activeFilter, setActiveFilter] = useState<boolean | undefined>(undefined);

  // Load data on mount
  useEffect(() => {
    fetchWorkflows();
    fetchStatistics();
    fetchTags();
  }, []);

  // Handle search
  const handleSearch = (search: string) => {
    setSearchTerm(search);
    fetchWorkflows({ search, tags: selectedTags.join(','), is_active: activeFilter });
  };

  // Handle tag filter
  const handleTagFilter = (tag: string) => {
    const newTags = selectedTags.includes(tag)
      ? selectedTags.filter((t) => t !== tag)
      : [...selectedTags, tag];
    setSelectedTags(newTags);
    fetchWorkflows({ search: searchTerm, tags: newTags.join(','), is_active: activeFilter });
  };

  // Handle active filter
  const handleActiveFilter = (isActive: boolean | undefined) => {
    setActiveFilter(isActive);
    fetchWorkflows({ search: searchTerm, tags: selectedTags.join(','), is_active: isActive });
  };

  // Handle delete
  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this workflow?')) {
      try {
        await deleteWorkflow(id);
        toast({ title: 'Success', description: 'Workflow deleted successfully' });
      } catch (error) {
        toast({ title: 'Error', description: 'Failed to delete workflow', variant: 'destructive' });
      }
    }
  };

  // Handle duplicate
  const handleDuplicate = async (id: string) => {
    try {
      await duplicateWorkflow(id);
      toast({ title: 'Success', description: 'Workflow duplicated successfully' });
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to duplicate workflow', variant: 'destructive' });
    }
  };

  // Handle toggle status
  const handleToggleStatus = async (id: string, currentStatus: boolean) => {
    try {
      await toggleWorkflowStatus(id, !currentStatus);
      toast({ title: 'Success', description: 'Workflow status updated' });
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to update status', variant: 'destructive' });
    }
  };

  if (loading && workflows.length === 0) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="p-6">
      {/* Statistics Dashboard */}
      {statistics && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="p-4 bg-white rounded-lg shadow">
            <h3 className="text-sm text-gray-500">Total Workflows</h3>
            <p className="text-2xl font-bold">{statistics.total_workflows}</p>
          </div>
          <div className="p-4 bg-white rounded-lg shadow">
            <h3 className="text-sm text-gray-500">Active Workflows</h3>
            <p className="text-2xl font-bold">{statistics.active_workflows}</p>
          </div>
          <div className="p-4 bg-white rounded-lg shadow">
            <h3 className="text-sm text-gray-500">Total Executions</h3>
            <p className="text-2xl font-bold">{statistics.total_executions}</p>
          </div>
          <div className="p-4 bg-white rounded-lg shadow">
            <h3 className="text-sm text-gray-500">Time Saved</h3>
            <p className="text-2xl font-bold">{statistics.time_saved}</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 space-y-4">
        <Input
          placeholder="Search workflows..."
          value={searchTerm}
          onChange={(e) => handleSearch(e.target.value)}
        />

        <div className="flex gap-2">
          <Button
            variant={activeFilter === undefined ? 'default' : 'outline'}
            onClick={() => handleActiveFilter(undefined)}
          >
            All
          </Button>
          <Button
            variant={activeFilter === true ? 'default' : 'outline'}
            onClick={() => handleActiveFilter(true)}
          >
            Active
          </Button>
          <Button
            variant={activeFilter === false ? 'default' : 'outline'}
            onClick={() => handleActiveFilter(false)}
          >
            Inactive
          </Button>
        </div>

        <div className="flex flex-wrap gap-2">
          {tags.map((tag) => (
            <Badge
              key={tag}
              variant={selectedTags.includes(tag) ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => handleTagFilter(tag)}
            >
              {tag}
            </Badge>
          ))}
        </div>
      </div>

      {/* Workflow List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {workflows.map((workflow) => (
          <div key={workflow.id} className="p-4 bg-white rounded-lg shadow">
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-lg font-semibold">{workflow.name}</h3>
              <Badge variant={workflow.metadata.isActive ? 'default' : 'secondary'}>
                {workflow.metadata.isActive ? 'Active' : 'Inactive'}
              </Badge>
            </div>

            <p className="text-sm text-gray-600 mb-4">{workflow.description}</p>

            <div className="flex flex-wrap gap-1 mb-4">
              {workflow.tags?.split(',').map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  {tag.trim()}
                </Badge>
              ))}
            </div>

            <div className="text-xs text-gray-500 mb-4">
              <div>Executions: {workflow.metadata.executionCount}</div>
              <div>Version: {workflow.version}</div>
            </div>

            <div className="flex gap-2">
              <Button size="sm" onClick={() => handleToggleStatus(workflow.id, workflow.metadata.isActive)}>
                {workflow.metadata.isActive ? 'Deactivate' : 'Activate'}
              </Button>
              <Button size="sm" variant="outline" onClick={() => handleDuplicate(workflow.id)}>
                Duplicate
              </Button>
              <Button size="sm" variant="destructive" onClick={() => handleDelete(workflow.id)}>
                Delete
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination Info */}
      <div className="mt-6 text-center text-sm text-gray-500">
        Showing {workflows.length} of {total} workflows
      </div>
    </div>
  );
};
```

---

## 🎨 UI Components Needed

Make sure you have these shadcn/ui components installed:

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add toast
```

---

## 🔄 Data Flow

```
User Action → Component → Store → API Client → Backend → Database
                ↓                                  ↓
            UI Update ← State Update ← Response ←
```

---

## 🧪 Testing Frontend Integration

1. **Start the development server:**
```bash
cd frontend
npm run dev
```

2. **Test each feature:**
   - [ ] Load workflows on page mount
   - [ ] Search functionality
   - [ ] Tag filtering
   - [ ] Active/Inactive filtering
   - [ ] Delete workflow (with confirmation)
   - [ ] Duplicate workflow
   - [ ] Toggle workflow status
   - [ ] View statistics

---

## 📝 TypeScript Types

**File:** `frontend/src/services/workflow/types.ts`

```typescript
export interface Workflow {
  id: string;
  name: string;
  description: string;
  tags: string;
  version: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  metadata: WorkflowMetadata;
}

export interface WorkflowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: {
    label: string;
    type: string;
    [key: string]: any;
  };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export interface WorkflowMetadata {
  createdAt: string;
  updatedAt: string;
  lastExecutedAt?: string;
  executionCount: number;
  isActive: boolean;
  createdBy: string;
}
```

---

## 🚀 Next Steps

1. **Implement the API client** - Copy the code from section 1
2. **Update the store** - Copy the code from section 2
3. **Update the UI component** - Copy the code from section 3
4. **Test the integration** - Follow the testing checklist
5. **Add error handling** - Implement toast notifications
6. **Add loading states** - Show spinners during API calls
7. **Add pagination** - Implement load more or page navigation

---

## 🐛 Common Issues

### Issue: CORS errors
**Solution:** Make sure your Frappe site allows CORS from your frontend URL

### Issue: Authentication errors
**Solution:** Ensure you're logged in to Frappe and have proper session cookies

### Issue: API not found
**Solution:** Verify the API endpoint path and method name

### Issue: Type errors
**Solution:** Make sure all TypeScript types match the API response structure

---

## 📚 Additional Resources

- Frappe API Documentation: https://frappeframework.com/docs/user/en/api
- React Query (alternative to Zustand): https://tanstack.com/query
- SWR (alternative state management): https://swr.vercel.app/

---

## ✅ Checklist

- [ ] API client implemented
- [ ] Store updated with new actions
- [ ] UI component updated
- [ ] TypeScript types defined
- [ ] Error handling added
- [ ] Loading states implemented
- [ ] Toast notifications working
- [ ] All features tested
- [ ] Pagination implemented (if needed)
- [ ] Responsive design verified

---

**Ready to integrate! All backend APIs are tested and working.** 🎉
