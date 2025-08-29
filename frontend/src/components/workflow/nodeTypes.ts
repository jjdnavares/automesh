import type { WorkflowEdge, WorkflowNode } from '../../types/workflow';

// Generic workflow node types that can be used for various workflows
export const nodeTypes = {
  start: {
    type: 'start',
    label: 'Start',
    icon: '▶️',
    color: '#4CAF50'
  },
  process: {
    type: 'process',
    label: 'Process',
    icon: '⚙️',
    color: '#2196F3'
  },
  decision: {
    type: 'decision',
    label: 'Decision',
    icon: '❓',
    color: '#FF9800'
  },
  end: {
    type: 'end',
    label: 'End',
    icon: '🏁',
    color: '#F44336'
  },
  approval: {
    type: 'approval',
    label: 'Approval',
    icon: '✅',
    color: '#9C27B0'
  },
  document: {
    type: 'document',
    label: 'Document',
    icon: '📄',
    color: '#607D8B'
  },
  data: {
    type: 'data',
    label: 'Data',
    icon: '💾',
    color: '#00BCD4'
  }
};

// Example workflow for document approval process
// Use proper node types for workflow nodes - making sure they match WorkflowNode type
export const initialNodes: WorkflowNode[] = [
  {
    id: '1',
    type: 'custom',
    position: { x: 50, y: 150 },
    data: {
      ...nodeTypes.start,
      label: 'Start Process',
      status: 'idle' as const
    }
  },
  {
    id: '2',
    type: 'custom',
    position: { x: 300, y: 150 },
    data: {
      ...nodeTypes.document,
      label: 'Create Document',
      status: 'idle' as const
    }
  },
  {
    id: '3',
    type: 'custom',
    position: { x: 600, y: 150 },
    data: {
      ...nodeTypes.approval,
      label: 'Review Document',
      status: 'idle' as const
    }
  },
  {
    id: '4',
    type: 'custom',
    position: { x: 900, y: 50 },
    data: {
      ...nodeTypes.process,
      label: 'Revise Document',
      status: 'idle' as const
    }
  },
  {
    id: '5',
    type: 'custom',
    position: { x: 900, y: 250 },
    data: {
      ...nodeTypes.end,
      label: 'Publish Document',
      status: 'idle' as const
    }
  },
  {
    id: '6',
    type: 'custom',
    position: { x: 600, y: 50 },
    data: {
      ...nodeTypes.decision,
      label: 'Needs Revision?',
      status: 'idle' as const
    }
  }
];

export const initialEdges: WorkflowEdge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true, type: 'smoothstep', data: {} },
  { id: 'e2-3', source: '2', target: '3', animated: true, type: 'smoothstep', data: {} },
  { id: 'e3-6', source: '3', target: '6', animated: true, type: 'smoothstep', data: {} },
  { id: 'e6-4', source: '6', target: '4', animated: true, type: 'smoothstep', data: { label: 'Yes' } },
  { id: 'e6-5', source: '6', target: '5', animated: true, type: 'smoothstep', data: { label: 'No' } },
  { id: 'e4-3', source: '4', target: '3', animated: true, type: 'smoothstep', data: {} }
];
