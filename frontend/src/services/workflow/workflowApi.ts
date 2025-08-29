// Only import the types we actually use
import type { Workflow, WorkflowExecutionStatus } from '../../types/workflow';

/**
 * Service for interacting with the Frappe Workflow API
 */
export const workflowApi = {
  /**
   * Fetch all workflows
   */
  async getWorkflows(): Promise<Workflow[]> {
    try {
      const response = await fetch('/api/method/automesh.automesh.api.workflow.get_workflows');
      if (!response.ok) {
        throw new Error(`Error fetching workflows: ${response.status}`);
      }
      const data = await response.json();
      return data.message || [];
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
  }
};
