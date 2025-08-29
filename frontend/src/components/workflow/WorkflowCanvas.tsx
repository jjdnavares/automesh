import { useCallback, useState, useEffect } from 'react';
import { ReactFlow, ReactFlowProvider, Background, Controls, Panel, useNodesState, useEdgesState, addEdge, MiniMap, BackgroundVariant } from '@xyflow/react';
import type { Connection, WorkflowNode, WorkflowEdge } from '../../types/workflow';
import { v4 as uuidv4 } from 'uuid';
import '@xyflow/react/dist/style.css';
import './workflow.css';

import CustomNode from './CustomNode';
import { initialNodes, initialEdges } from './nodeTypes';

// Define custom node types
const nodeTypes = { custom: CustomNode };

interface WorkflowProps {
  id?: string;
  title?: string;
  description?: string;
  initialNodes?: WorkflowNode[];
  initialEdges?: WorkflowEdge[];
  readOnly?: boolean;
}

function WorkflowCanvas({
  title = 'Document Approval Workflow',
  description = 'A workflow demonstrating the document creation and approval process',
  initialNodes: propNodes = initialNodes,
  initialEdges: propEdges = initialEdges,
  readOnly = false
}: WorkflowProps) {
  const [nodes, _, onNodesChange] = useNodesState(propNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(propEdges);
  const [workflowStats, setWorkflowStats] = useState({
    nodeCount: propNodes.length,
    edgeCount: propEdges.length
  });

  // Update stats when nodes or edges change
  useEffect(() => {
    setWorkflowStats({
      nodeCount: nodes.length,
      edgeCount: edges.length
    });
  }, [nodes.length, edges.length]);

  const onConnect = useCallback((params: Connection) => {
    if (readOnly) return; // Prevent connections in read-only mode
    
    // Generate unique ID for new edges
    const edgeWithId = {
      ...params,
      id: `edge-${uuidv4()}`,
      animated: true,
      type: 'smoothstep',
      data: {}
    };
    setEdges((eds) => addEdge(edgeWithId as any, eds));
  }, [setEdges, readOnly]);

  return (
    <div className="workflow-container" style={{ width: '100%', height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        nodesDraggable={!readOnly}
        nodesConnectable={!readOnly}
        elementsSelectable={!readOnly}
        fitView
      >
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        <Controls showInteractive={!readOnly} />
        <MiniMap 
          nodeStrokeColor="#aaa" 
          nodeColor={(node) => {
            return (node.data?.color || '#eee') + '80';
          }} 
        />
        <Panel position="top-left" className="workflow-info-panel">
          <h3 className="text-xl font-bold">{title}</h3>
          {description && <p className="text-sm text-gray-600">{description}</p>}
          <div className="text-xs text-gray-500 mt-1">
            {workflowStats.nodeCount} nodes · {workflowStats.edgeCount} connections
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}

// Wrap with provider to avoid context errors
export default function WorkflowCanvasWrapper(props: WorkflowProps) {
  return (
    <ReactFlowProvider>
      <WorkflowCanvas {...props} />
    </ReactFlowProvider>
  );
}
