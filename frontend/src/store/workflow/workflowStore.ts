import { create } from 'zustand';
import { 
  addEdge, 
  applyNodeChanges, 
  applyEdgeChanges
} from '@xyflow/react';
import type { 
  Node, 
  Edge, 
  NodeChange, 
  EdgeChange
} from '@xyflow/react';
import type { 
  Connection,
  Workflow, 
  WorkflowNode, 
  WorkflowEdge, 
  WorkflowState, 
  ExecutionStatus,
} from '../../types/workflow';
import { nodeTypes, initialNodes, initialEdges } from '../../components/workflow/nodes/NodeTypes';
import { workflowApi } from '../../services/workflow/workflowApi';
import { v4 as uuidv4 } from 'uuid';

// Define the workflow store state and actions
interface WorkflowStore extends WorkflowState {
  // Nodes and Edges Actions
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
  addNode: (node: Partial<WorkflowNode>) => void;
  updateNode: (id: string, data: Partial<WorkflowNode>) => void;
  removeNode: (id: string) => void;
  updateEdge: (id: string, data: Partial<WorkflowEdge>) => void;
  
  // Workflow Actions
  createNewWorkflow: (name: string, description?: string) => Promise<string>;
  loadWorkflow: (id: string) => Promise<void>;
  saveWorkflow: () => Promise<void>;
  deleteWorkflow: (id: string) => Promise<void>;
  exportWorkflow: (id: string) => Promise<string>;
  importWorkflow: (data: string) => void;
  
  // History Actions
  undo: () => void;
  redo: () => void;
  clearHistory: () => void;
  
  // Selection Actions
  selectNode: (id: string | null) => void;
  selectEdge: (id: string | null) => void;
  clearSelection: () => void;
  
  // Execution Actions
  startExecution: () => Promise<void>;
  stopExecution: () => Promise<void>;
  resetExecution: () => void;
  checkExecutionStatus: (executionId: string) => Promise<void>;
  
  // API-related actions
  fetchWorkflows: () => Promise<void>;
  fetchNodeTypes: () => Promise<void>;
}

// Create the workflow store
export const useWorkflowStore = create<WorkflowStore>((set, get) => ({
  // State
  nodes: initialNodes,
  edges: initialEdges,
  workflows: {},
  nodeTypes: nodeTypes,
  currentWorkflowId: null,
  selectedNode: null,
  selectedEdge: null,
  history: [],
  historyIndex: -1,
  executionStatus: 'idle',
  currentExecutionId: null,
  nodeExecutionStatuses: {},
  isLoading: false,
  error: null,
  
  // Nodes and Edges Actions
  onNodesChange: (changes: NodeChange[]) => {
    const { nodes, history, historyIndex } = get();
    const newNodes = applyNodeChanges(changes, nodes as Node[]) as WorkflowNode[];
    
    // Add to history if it's a significant change (not just a position update)
    const significantChanges = changes.some(change => 
      change.type === 'add' || change.type === 'remove');
      
    if (significantChanges) {
      const newHistory = [...history.slice(0, historyIndex + 1), {
        nodes: [...nodes],
        edges: [...get().edges]
      }];
      
      set({
        nodes: newNodes,
        history: newHistory,
        historyIndex: historyIndex + 1
      });
    } else {
      set({ nodes: newNodes });
    }
  },
  
  onEdgesChange: (changes: EdgeChange[]) => {
    const { edges, history, historyIndex } = get();
    const newEdges = applyEdgeChanges(changes, edges as Edge[]) as WorkflowEdge[];
    
    // Add to history if it's not just a selection change
    const significantChanges = changes.some(change => 
      change.type === 'add' || change.type === 'remove');
      
    if (significantChanges) {
      const newHistory = [...history.slice(0, historyIndex + 1), {
        nodes: [...get().nodes],
        edges: [...edges]
      }];
      
      set({
        edges: newEdges,
        history: newHistory,
        historyIndex: historyIndex + 1
      });
    } else {
      set({ edges: newEdges });
    }
  },
  
  onConnect: (connection: Connection) => {
    const { edges, history, historyIndex } = get();
    const newEdge: WorkflowEdge = {
      ...connection,
      id: `edge-${uuidv4()}`,
      type: 'custom', // Use our custom edge
      animated: false,
      data: { label: '' }
    };
    
    const newEdges = addEdge(newEdge, edges as Edge[]) as WorkflowEdge[];
    
    // Add to history
    const newHistory = [...history.slice(0, historyIndex + 1), {
      nodes: [...get().nodes],
      edges: [...edges]
    }];
    
    set({
      edges: newEdges,
      history: newHistory,
      historyIndex: historyIndex + 1
    });
  },
  
  addNode: (node: Partial<WorkflowNode>) => {
    const { nodes, history, historyIndex } = get();
    const newNode: WorkflowNode = {
      id: `node-${uuidv4()}`,
      type: 'custom',
      position: { x: 100, y: 100 },
      data: { 
        type: 'default',
        label: 'New Node',
        icon: '📄',
        color: '#3182CE',
        status: 'idle',
        params: {},
        inputSockets: [{ id: 'input-default', label: 'Input' }],
        outputSockets: [{ id: 'output-default', label: 'Output' }],
      },
      ...node
    };
    
    const newNodes = [...nodes, newNode];
    
    // Add to history
    const newHistory = [...history.slice(0, historyIndex + 1), {
      nodes: [...nodes],
      edges: [...get().edges]
    }];
    
    set({
      nodes: newNodes,
      history: newHistory,
      historyIndex: historyIndex + 1,
      selectedNode: newNode.id
    });
  },
  
  updateNode: (id: string, data: Partial<WorkflowNode>) => {
    const { nodes, history, historyIndex } = get();
    const newNodes = nodes.map(node => {
      if (node.id === id) {
        return { ...node, ...data, data: { ...node.data, ...data.data } };
      }
      return node;
    });
    
    // Add to history
    const newHistory = [...history.slice(0, historyIndex + 1), {
      nodes: [...nodes],
      edges: [...get().edges]
    }];
    
    set({
      nodes: newNodes,
      history: newHistory,
      historyIndex: historyIndex + 1
    });
  },
  
  removeNode: (id: string) => {
    const { nodes, edges, history, historyIndex } = get();
    
    // Remove the node
    const newNodes = nodes.filter(node => node.id !== id);
    
    // Remove any edges connected to the node
    const newEdges = edges.filter(
      edge => edge.source !== id && edge.target !== id
    );
    
    // Add to history
    const newHistory = [...history.slice(0, historyIndex + 1), {
      nodes: [...nodes],
      edges: [...edges]
    }];
    
    set({
      nodes: newNodes,
      edges: newEdges,
      history: newHistory,
      historyIndex: historyIndex + 1,
      selectedNode: null
    });
  },
  
  updateEdge: (id: string, data: Partial<WorkflowEdge>) => {
    const { edges, history, historyIndex } = get();
    const newEdges = edges.map(edge => {
      if (edge.id === id) {
        return { ...edge, ...data, data: { ...edge.data, ...data.data } };
      }
      return edge;
    });
    
    // Add to history
    const newHistory = [...history.slice(0, historyIndex + 1), {
      nodes: [...get().nodes],
      edges: [...edges]
    }];
    
    set({
      edges: newEdges,
      history: newHistory,
      historyIndex: historyIndex + 1
    });
  },
  
  // Workflow Actions
  createNewWorkflow: async (name: string, description?: string) => {
    try {
      set({ isLoading: true, error: null });
      
      const workflowData: Partial<Workflow> = {
        name,
        description,
        nodes: [],
        edges: [],
        version: '1.0.0',
        isActive: false,
        metadata: {
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          executionCount: 0
        }
      };
      
      const createdWorkflow = await workflowApi.createWorkflow(workflowData);
      
      // Update the workflows in the store
      const workflows = { ...get().workflows };
      workflows[createdWorkflow.id] = createdWorkflow;
      
      set({
        currentWorkflowId: createdWorkflow.id,
        nodes: [],
        edges: [],
        workflows,
        history: [],
        historyIndex: -1,
        selectedNode: null,
        selectedEdge: null,
        isLoading: false
      });
      
      return createdWorkflow.id;
    } catch (error) {
      console.error('Failed to create workflow:', error);
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Failed to create workflow' 
      });
      throw error;
    }
  },
  
  loadWorkflow: async (id: string) => {
    try {
      set({ isLoading: true, error: null });
      
      let workflow: Workflow;
      
      // Check if the workflow is already in our local cache
      if (get().workflows[id]) {
        workflow = get().workflows[id];
      } else {
        // Fetch from API
        workflow = await workflowApi.getWorkflow(id);
        
        // Update the workflows in the store
        const workflows = { ...get().workflows };
        workflows[id] = workflow;
        set({ workflows });
      }
      
      set({
        currentWorkflowId: id,
        nodes: workflow.nodes || [],
        edges: workflow.edges || [],
        history: [],
        historyIndex: -1,
        selectedNode: null,
        selectedEdge: null,
        executionStatus: 'idle',
        currentExecutionId: null,
        nodeExecutionStatuses: {},
        isLoading: false
      });
    } catch (error) {
      console.error(`Failed to load workflow ${id}:`, error);
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : `Failed to load workflow ${id}` 
      });
    }
  },
  
  saveWorkflow: async () => {
    const { currentWorkflowId, nodes, edges, workflows } = get();
    
    if (!currentWorkflowId) {
      console.error('No workflow selected to save');
      return;
    }
    
    try {
      set({ isLoading: true, error: null });
      
      const currentWorkflow = workflows[currentWorkflowId];
      
      // Create updated workflow object
      const updatedWorkflow: Partial<Workflow> = {
        ...currentWorkflow,
        nodes,
        edges,
        metadata: {
          ...currentWorkflow.metadata,
          updatedAt: new Date().toISOString()
        }
      };
      
      // Save to API
      const savedWorkflow = await workflowApi.updateWorkflow(currentWorkflowId, updatedWorkflow);
      
      // Update the workflows in the store
      const newWorkflows = { ...workflows };
      newWorkflows[currentWorkflowId] = savedWorkflow;
      
      set({
        workflows: newWorkflows,
        isLoading: false
      });
    } catch (error) {
      console.error(`Failed to save workflow ${currentWorkflowId}:`, error);
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : `Failed to save workflow ${currentWorkflowId}` 
      });
    }
  },
  
  deleteWorkflow: async (id: string) => {
    try {
      set({ isLoading: true, error: null });
      
      // Delete from API
      await workflowApi.deleteWorkflow(id);
      
      // Update the workflows in the store
      const newWorkflows = { ...get().workflows };
      delete newWorkflows[id];
      
      // If the deleted workflow was the current one, reset current state
      if (get().currentWorkflowId === id) {
        set({
          currentWorkflowId: null,
          nodes: [],
          edges: [],
          selectedNode: null,
          selectedEdge: null,
          history: [],
          historyIndex: -1,
          executionStatus: 'idle',
          currentExecutionId: null,
          nodeExecutionStatuses: {}
        });
      }
      
      set({
        workflows: newWorkflows,
        isLoading: false
      });
    } catch (error) {
      console.error(`Failed to delete workflow ${id}:`, error);
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : `Failed to delete workflow ${id}` 
      });
    }
  },
  
  exportWorkflow: async (id: string) => {
    const { workflows } = get();
    const workflowToExport = workflows[id];
    
    if (!workflowToExport) {
      throw new Error(`Workflow ${id} not found`);
    }
    
    return Promise.resolve(JSON.stringify(workflowToExport, null, 2));
  },
  
  importWorkflow: (data: string) => {
    try {
      const workflow: Workflow = JSON.parse(data);
      
      // Validate the imported data (basic validation)
      if (!workflow.name || !workflow.id) {
        throw new Error('Invalid workflow format');
      }
      
      // Add the workflow to our store
      const newWorkflows = { ...get().workflows };
      newWorkflows[workflow.id] = workflow;
      
      set({
        workflows: newWorkflows
      });
      
      return workflow.id;
    } catch (error) {
      console.error('Failed to import workflow:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to import workflow' 
      });
      throw error;
    }
  },
  
  // History Actions
  undo: () => {
    const { historyIndex, history } = get();
    
    if (historyIndex > 0) {
      const prevState = history[historyIndex - 1];
      
      set({
        nodes: prevState.nodes,
        edges: prevState.edges,
        historyIndex: historyIndex - 1,
        selectedNode: null,
        selectedEdge: null
      });
    }
  },
  
  redo: () => {
    const { historyIndex, history } = get();
    
    if (historyIndex < history.length - 1) {
      const nextState = history[historyIndex + 1];
      
      set({
        nodes: nextState.nodes,
        edges: nextState.edges,
        historyIndex: historyIndex + 1,
        selectedNode: null,
        selectedEdge: null
      });
    }
  },
  
  clearHistory: () => {
    set({
      history: [],
      historyIndex: -1
    });
  },
  
  // Selection Actions
  selectNode: (id: string | null) => {
    set({
      selectedNode: id,
      selectedEdge: null
    });
  },
  
  selectEdge: (id: string | null) => {
    set({
      selectedEdge: id,
      selectedNode: null
    });
  },
  
  clearSelection: () => {
    set({
      selectedNode: null,
      selectedEdge: null
    });
  },
  
  // Execution Actions
  startExecution: async () => {
    const { currentWorkflowId, nodes } = get();
    
    if (!currentWorkflowId) {
      console.error('No workflow selected to execute');
      return;
    }
    
    try {
      set({ 
        executionStatus: 'running',
        error: null,
        // Initialize all nodes to pending
        nodeExecutionStatuses: nodes.reduce((acc, node) => {
          acc[node.id] = { status: 'pending', message: null };
          return acc;
        }, {} as Record<string, { status: string; message: string | null }>)
      });
      
      // Start execution via API
      const { execution_id } = await workflowApi.executeWorkflow(currentWorkflowId);
      
      set({ currentExecutionId: execution_id });
      
      // Start polling for updates
      const intervalId = setInterval(async () => {
        await get().checkExecutionStatus(execution_id);
        
        // Stop polling if execution is no longer running
        if (get().executionStatus !== 'running') {
          clearInterval(intervalId);
        }
      }, 1000);
    } catch (error) {
      console.error(`Failed to start workflow execution:`, error);
      set({ 
        executionStatus: 'error',
        error: error instanceof Error ? error.message : 'Failed to start workflow execution' 
      });
    }
  },
  
  stopExecution: async () => {
    const { currentExecutionId } = get();
    
    if (!currentExecutionId) {
      console.error('No execution to stop');
      return;
    }
    
    try {
      // Stop execution via API
      await workflowApi.stopWorkflowExecution(currentExecutionId);
      
      set({ 
        executionStatus: 'stopped',
      });
    } catch (error) {
      console.error(`Failed to stop workflow execution:`, error);
      set({ 
        error: error instanceof Error ? error.message : 'Failed to stop workflow execution' 
      });
    }
  },
  
  resetExecution: () => {
    set({
      executionStatus: 'idle',
      currentExecutionId: null,
      nodeExecutionStatuses: {},
      error: null
    });
  },
  
  checkExecutionStatus: async (executionId: string) => {
    try {
      // Get execution status via API
      const executionResult = await workflowApi.getWorkflowExecutionStatus(executionId);
      
      // Map the API response to our store's expected format
      // The API may return different formats depending on implementation
      let status: ExecutionStatus = 'idle';
      let nodeStatuses = {};
      
      if (executionResult) {
        if (typeof executionResult === 'string') {
          // If API returns string status directly
          status = executionResult as ExecutionStatus;
        } else if (typeof executionResult === 'object') {
          // If API returns object with status and node data
          const result = executionResult as any;
          status = (result.status || 'idle') as ExecutionStatus;
          nodeStatuses = result.nodeExecutions || result.nodeStatuses || {};
        }
      }
      
      set({
        executionStatus: status,
        nodeExecutionStatuses: nodeStatuses
      });
    } catch (error) {
      console.error(`Failed to check execution status:`, error);
      // We don't set an error state here to avoid interrupting the UX
    }
  },
  
  // API-related actions
  fetchWorkflows: async () => {
    try {
      set({ isLoading: true, error: null });
      
      // Fetch workflows from API
      const workflowsList = await workflowApi.getWorkflows();
      
      // Convert to workflow map
      const workflowsMap = workflowsList.reduce((acc, workflow) => {
        acc[workflow.id] = workflow;
        return acc;
      }, {} as Record<string, Workflow>);
      
      set({
        workflows: workflowsMap,
        isLoading: false
      });
    } catch (error) {
      console.error('Failed to fetch workflows:', error);
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Failed to fetch workflows' 
      });
    }
  },
  
  fetchNodeTypes: async () => {
    try {
      set({ isLoading: true, error: null });
      
      // Fetch node types from API
      const apiNodeTypes = await workflowApi.getNodeTypes();
      
      // Merge with existing nodeTypes if needed
      // This would require mapping from API format to our internal format
      if (apiNodeTypes && Array.isArray(apiNodeTypes) && apiNodeTypes.length > 0) {
        // Here you could implement merging logic if needed
        // For now we're just acknowledging the response
      }
      
      set({
        isLoading: false
      });
    } catch (error) {
      console.error('Failed to fetch node types:', error);
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Failed to fetch node types' 
      });
    }
  }
}));
