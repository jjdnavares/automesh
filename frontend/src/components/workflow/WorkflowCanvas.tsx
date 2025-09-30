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
    <div className="workflow-container workflow-page">
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
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="#e2e8f0" />
        <Controls 
          showInteractive={!readOnly} 
          className="react-flow__controls-button bg-white border border-gray-200 shadow-sm"
          style={{
            borderRadius: '8px',
            padding: '4px',
            backgroundColor: 'white',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}
        />
        <MiniMap 
          nodeStrokeColor="#aaa" 
          nodeColor={(node) => {
            return (node.data?.color || '#eee') + '80';
          }}
          className="bg-white rounded-lg border border-gray-100 shadow-sm"
          style={{ padding: '8px' }}
        />
        <Panel position="top-left" className="workflow-info-panel">
          <h3 className="text-xl font-bold">{title}</h3>
          {description && <p className="text-sm text-gray-600">{description}</p>}
          <div className="text-xs text-gray-500 mt-1">
            {workflowStats.nodeCount} nodes · {workflowStats.edgeCount} connections
          </div>
        </Panel>
        
        <Panel position="top-right">
          <div className="flex gap-2 bg-white rounded-lg border border-gray-100 shadow-sm p-2">
            <button className="px-3 py-1.5 text-xs font-medium bg-indigo-50 text-indigo-700 rounded-md hover:bg-indigo-100">
              Run
            </button>
            <button className="px-3 py-1.5 text-xs font-medium border border-gray-200 rounded-md hover:bg-gray-50">
              Save
            </button>
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
