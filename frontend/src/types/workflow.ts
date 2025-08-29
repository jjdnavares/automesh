import type { Node, Edge, NodeChange, EdgeChange } from '@xyflow/react';

// Define Connection interface based on the expected usage
export interface Connection {
  source: string;
  sourceHandle?: string | null;
  target: string;
  targetHandle?: string | null;
}

// Node data structure
export interface WorkflowNodeData {
  type: string;
  label: string;
  description?: string;
  icon: string;
  color: string;
  category?: string;
  inputs?: string[];
  outputs?: string[];
  parameters?: Record<string, any>;
  status?: 'idle' | 'running' | 'success' | 'error';
  metadata?: {
    createdAt: string;
    updatedAt: string;
    executionCount: number;
  };
}

// Extending React Flow's Node type
export interface WorkflowNode extends Node {
  data: WorkflowNodeData & Record<string, unknown>;
}

// Extending React Flow's Edge type
export interface WorkflowEdge extends Edge {
  data?: {
    label?: string;
    transformations?: any[];
    conditions?: any[];
  };
}

// Workflow model
export interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  version: string;
  tags?: string[];
  isActive: boolean;
  metadata: {
    createdAt: string;
    updatedAt: string;
    lastExecutedAt?: string;
    executionCount: number;
  };
}

// History entry for undo/redo
export interface HistoryEntry {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  timestamp?: number;
}

// Node category for grouping in library
export interface NodeCategory {
  id: string;
  label: string;
  description: string;
  icon: string;
}

// Node type definition
export interface NodeType {
  type: string;
  label: string;
  description: string;
  icon: string;
  color: string;
  category: string;
  inputs: string[];
  outputs: string[];
}

// Function types for workflow operations
export type OnNodesChange = (changes: NodeChange[]) => void;
export type OnEdgesChange = (changes: EdgeChange[]) => void;
export type OnConnect = (connection: Edge) => void;
export type OnNodeAdd = (node: WorkflowNode) => void;
export type OnEdgeAdd = (edge: WorkflowEdge) => void;
export type OnNodeRemove = (nodeId: string) => void;
export type OnEdgeRemove = (edgeId: string) => void;
export type OnUndo = () => void;
export type OnRedo = () => void;

// Execution status for workflow
export type WorkflowExecutionStatus = 
  | 'idle' 
  | 'running' 
  | 'completed' 
  | 'failed' 
  | 'paused' 
  | 'stopped';

// Simplified execution status used by the store
export type ExecutionStatus = 'idle' | 'running' | 'completed' | 'error' | 'stopped';

// Execution data for workflow
export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: WorkflowExecutionStatus;
  startTime: string;
  endTime?: string;
  nodeExecutions: {
    nodeId: string;
    status: 'idle' | 'running' | 'success' | 'error';
    startTime: string;
    endTime?: string;
    outputs?: any;
    error?: string;
  }[];
}

// Workflow state interface for the store
export interface WorkflowState {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  workflows: Record<string, Workflow>;
  nodeTypes: Record<string, any>;
  currentWorkflowId: string | null;
  selectedNode: string | null;
  selectedEdge: string | null;
  history: HistoryEntry[];
  historyIndex: number;
  executionStatus: ExecutionStatus;
  currentExecutionId: string | null;
  nodeExecutionStatuses: Record<string, { status: string; message: string | null }>;
  isLoading: boolean;
  error: string | null;
}

// Re-export all types to ensure they're properly recognized by the bundler
const workflowTypes = {
  WorkflowNodeData: {} as WorkflowNodeData,
  WorkflowNode: {} as WorkflowNode,
  WorkflowEdge: {} as WorkflowEdge,
  Workflow: {} as Workflow,
  WorkflowExecutionStatus: 'idle' as WorkflowExecutionStatus,
  WorkflowExecution: {} as WorkflowExecution,
  ExecutionStatus: 'idle' as ExecutionStatus,
  WorkflowState: {} as WorkflowState,
};

export default workflowTypes;
