// Only import the types we actually use
import type { Workflow, WorkflowExecutionStatus } from '../../types/workflow';

/**
 * Query parameters for fetching workflows
 */
export interface WorkflowQueryParams {
  limit?: number;
  offset?: number;
  search?: string;
  tags?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  is_active?: boolean;
}

/**
 * Response from get_workflows API
 */
export interface WorkflowsResponse {
  workflows: Workflow[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Service for interacting with the Frappe Workflow API
 */
export const workflowApi = {
  /**
   * Fetch all workflows with optional filters and pagination
   */
  async getWorkflows(params?: WorkflowQueryParams): Promise<WorkflowsResponse> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params?.limit) queryParams.append('limit', params.limit.toString());
      if (params?.offset) queryParams.append('offset', params.offset.toString());
      if (params?.search) queryParams.append('search', params.search);
      if (params?.tags) queryParams.append('tags', params.tags);
      if (params?.sort_by) queryParams.append('sort_by', params.sort_by);
      if (params?.sort_order) queryParams.append('sort_order', params.sort_order);
      if (params?.is_active !== undefined) queryParams.append('is_active', params.is_active ? '1' : '0');
      
      const url = `/api/method/automesh.automesh.api.workflow.get_workflows${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Error fetching workflows: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message || { workflows: [], total: 0, limit: 20, offset: 0 };
    } catch (error) {
      console.error('Failed to fetch workflows:', error);
      throw error;
    }
  },

  /**
   * Get a specific workflow by ID
   */
  async getWorkflow(id: string): Promise<Workflow> {
    try {
      const response = await fetch(`/api/method/automesh.automesh.api.workflow.get_workflow?workflow_id=${id}`);
      if (!response.ok) {
        throw new Error(`Error fetching workflow: ${response.status}`);
      }
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error(`Failed to fetch workflow ${id}:`, error);
      throw error;
    }
  },

  /**
   * Create a new workflow
   */
  async createWorkflow(workflow: Partial<Workflow>): Promise<Workflow> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.create_workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow: workflow,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error creating workflow: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error('Failed to create workflow:', error);
      throw error;
    }
  },

  /**
   * Update an existing workflow
   */
  async updateWorkflow(id: string, workflow: Partial<Workflow>): Promise<Workflow> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.update_workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: id,
          workflow: workflow,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error updating workflow: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error(`Failed to update workflow ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete a workflow
   */
  async deleteWorkflow(id: string): Promise<{ success: boolean }> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.delete_workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: id,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error deleting workflow: ${response.status}`);
      }
      
      await response.json(); // Process response but we don't need the data
      return { success: true };
    } catch (error) {
      console.error(`Failed to delete workflow ${id}:`, error);
      throw error;
    }
  },

  /**
   * Execute a workflow
   */
  async executeWorkflow(id: string): Promise<{ execution_id: string }> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.execute_workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: id,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error executing workflow: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error(`Failed to execute workflow ${id}:`, error);
      throw error;
    }
  },

  /**
   * Stop a workflow execution
   */
  async stopWorkflowExecution(executionId: string): Promise<{ success: boolean }> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.stop_workflow_execution', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          execution_id: executionId,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error stopping workflow execution: ${response.status}`);
      }
      
      return { success: true };
    } catch (error) {
      console.error(`Failed to stop workflow execution ${executionId}:`, error);
      throw error;
    }
  },

  /**
   * Get workflow execution status
   */
  async getWorkflowExecutionStatus(executionId: string): Promise<WorkflowExecutionStatus> {
    try {
      const response = await fetch(`/api/method/automesh.automesh.api.workflow.get_execution_status?execution_id=${executionId}`);
      
      if (!response.ok) {
        throw new Error(`Error fetching execution status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error(`Failed to fetch execution status for ${executionId}:`, error);
      throw error;
    }
  },

  /**
   * Get available node types
   */
  async getNodeTypes(): Promise<any[]> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.get_node_types');
      
      if (!response.ok) {
        throw new Error(`Error fetching node types: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message || [];
    } catch (error) {
      console.error('Failed to fetch node types:', error);
      throw error;
    }
  },

  /**
   * Get workflow templates
   */
  async getWorkflowTemplates(): Promise<any[]> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.get_workflow_templates');
      
      if (!response.ok) {
        throw new Error(`Error fetching workflow templates: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message || [];
    } catch (error) {
      console.error('Failed to fetch workflow templates:', error);
      throw error;
    }
  },

  /**
   * Create workflow from template
   */
  async createFromTemplate(templateId: string, name?: string): Promise<Workflow> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.create_from_template', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template_id: templateId,
          name: name,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error creating workflow from template: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error(`Failed to create workflow from template ${templateId}:`, error);
      throw error;
    }
  },

  /**
   * Duplicate a workflow
   */
  async duplicateWorkflow(id: string, newName?: string): Promise<Workflow> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.duplicate_workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: id,
          new_name: newName,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error duplicating workflow: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error(`Failed to duplicate workflow ${id}:`, error);
      throw error;
    }
  },

  /**
   * Toggle workflow active status
   */
  async toggleWorkflowStatus(id: string, isActive: boolean): Promise<{ success: boolean; is_active: boolean }> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.toggle_workflow_status', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: id,
          is_active: isActive,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error toggling workflow status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error(`Failed to toggle workflow status ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get workflow statistics
   */
  async getWorkflowStatistics(days: number = 7): Promise<any> {
    try {
      const response = await fetch(`/api/method/automesh.automesh.api.workflow.get_workflow_statistics?days=${days}`);
      
      if (!response.ok) {
        throw new Error(`Error fetching workflow statistics: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error('Failed to fetch workflow statistics:', error);
      throw error;
    }
  },

  /**
   * Get all tags used in workflows
   */
  async getAllTags(): Promise<string[]> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.get_all_tags');
      
      if (!response.ok) {
        throw new Error(`Error fetching tags: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message || [];
    } catch (error) {
      console.error('Failed to fetch tags:', error);
      throw error;
    }
  },

  /**
   * Bulk delete workflows
   */
  async bulkDeleteWorkflows(workflowIds: string[]): Promise<{ success: boolean; deleted: string[]; failed: any[]; deleted_count: number; failed_count: number }> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.bulk_delete_workflows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_ids: workflowIds,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error bulk deleting workflows: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error('Failed to bulk delete workflows:', error);
      throw error;
    }
  },

  /**
   * Bulk update workflow status
   */
  async bulkUpdateStatus(workflowIds: string[], isActive: boolean): Promise<{ success: boolean; updated: string[]; failed: any[]; updated_count: number; failed_count: number }> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.bulk_update_status', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_ids: workflowIds,
          is_active: isActive,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error bulk updating workflow status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error('Failed to bulk update workflow status:', error);
      throw error;
    }
  },

  /**
   * Get workflow execution history
   */
  async getWorkflowExecutions(workflowId: string, limit: number = 10, offset: number = 0, status?: string): Promise<{ executions: any[]; total: number; limit: number; offset: number }> {
    try {
      const params = new URLSearchParams({
        workflow_id: workflowId,
        limit: limit.toString(),
        offset: offset.toString(),
      });
      
      if (status) {
        params.append('status', status);
      }
      
      const response = await fetch(`/api/method/automesh.automesh.api.workflow.get_workflow_executions?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`Error fetching workflow executions: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error(`Failed to fetch workflow executions for ${workflowId}:`, error);
      throw error;
    }
  },

  /**
   * Get workflow templates
   */
  async getTemplates(category?: string): Promise<any[]> {
    try {
      const params = new URLSearchParams();
      if (category) {
        params.append('category', category);
      }
      
      const url = `/api/method/automesh.automesh.api.workflow.get_templates${params.toString() ? '?' + params.toString() : ''}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Error fetching templates: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message || [];
    } catch (error) {
      console.error('Failed to fetch templates:', error);
      throw error;
    }
  },

  /**
   * Create workflow from template
   */
  async createWorkflowFromTemplate(templateId: string, workflowName?: string): Promise<Workflow> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.create_workflow_from_template', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template_id: templateId,
          workflow_name: workflowName,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error creating workflow from template: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error(`Failed to create workflow from template ${templateId}:`, error);
      throw error;
    }
  },

  /**
   * Export workflow as JSON
   */
  async exportWorkflow(workflowId: string): Promise<any> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.export_workflow_json', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: workflowId,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error exporting workflow: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error(`Failed to export workflow ${workflowId}:`, error);
      throw error;
    }
  },

  /**
   * Import workflow from JSON
   */
  async importWorkflow(importData: any): Promise<Workflow> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.import_workflow_json', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          import_data: importData,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error importing workflow: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error('Failed to import workflow:', error);
      throw error;
    }
  },

  /**
   * Quick execute workflow with default inputs
   */
  async quickExecuteWorkflow(workflowId: string, inputData?: any): Promise<{ execution_id: string }> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.execute_workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: workflowId,
          input_data: inputData || {},
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error executing workflow: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error(`Failed to execute workflow ${workflowId}:`, error);
      throw error;
    }
  },

  /**
   * Share workflow with another user
   */
  async shareWorkflow(workflowId: string, sharedWith: string, permissionLevel: string, expiresAt?: string): Promise<{ success: boolean; share_id: string }> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.share_workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: workflowId,
          shared_with: sharedWith,
          permission_level: permissionLevel,
          expires_at: expiresAt,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error sharing workflow: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error(`Failed to share workflow ${workflowId}:`, error);
      throw error;
    }
  },

  /**
   * Get workflow shares
   */
  async getWorkflowShares(workflowId: string): Promise<any[]> {
    try {
      const response = await fetch(`/api/method/automesh.automesh.api.workflow.get_workflow_shares?workflow_id=${workflowId}`);
      
      if (!response.ok) {
        throw new Error(`Error fetching workflow shares: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message || [];
    } catch (error) {
      console.error(`Failed to fetch workflow shares for ${workflowId}:`, error);
      throw error;
    }
  },

  /**
   * Revoke workflow share
   */
  async revokeWorkflowShare(shareId: string): Promise<{ success: boolean }> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.revoke_workflow_share', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          share_id: shareId,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error revoking workflow share: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error(`Failed to revoke workflow share ${shareId}:`, error);
      throw error;
    }
  },

  /**
   * Update workflow share permission
   */
  async updateWorkflowShare(shareId: string, permissionLevel: string): Promise<{ success: boolean }> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.update_workflow_share', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          share_id: shareId,
          permission_level: permissionLevel,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error updating workflow share: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error(`Failed to update workflow share ${shareId}:`, error);
      throw error;
    }
  }
};
