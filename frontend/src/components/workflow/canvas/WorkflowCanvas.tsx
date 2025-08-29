import { useCallback } from 'react';
import { 
  ReactFlowProvider,
  ConnectionMode,
  ConnectionLineType,
  Panel,
  useNodesState,
  useEdgesState,
  addEdge,
  BackgroundVariant
} from '@xyflow/react';
import type { Connection, WorkflowEdge } from '../../../types/workflow';

import Canvas from './Canvas';
import { nodeTypes as nodeTypeDefs } from '../nodes/NodeTypes';
import BaseNode from '../nodes/BaseNode';
import CustomEdge from '../edges/CustomEdge';
import NodeLibrary from '../nodes/NodeLibrary';
import PropertiesPanel from '../panels/PropertiesPanel';

// Import state management when implemented
// import { useWorkflowStore } from '../../../store/workflow/workflowStore';

import '../workflow.css';

// Define custom node and edge types
const nodeTypes = { 
  base: BaseNode,
};

const edgeTypes = {
  custom: CustomEdge,
};

interface WorkflowCanvasProps {
  workflowId?: string;
  isReadOnly?: boolean;
  showLibrary?: boolean;
  showProperties?: boolean;
  initialNodes?: any[];
  initialEdges?: WorkflowEdge[];
}

function WorkflowCanvasInner({
  workflowId,
  isReadOnly = false,
  showLibrary = true,
  showProperties = true,
  initialNodes = [],
  initialEdges = [],
}: WorkflowCanvasProps) {
  // When we implement the store, we'll use it here
  // const { nodes: storeNodes, edges: storeEdges, onNodesChange, onEdgesChange } = useWorkflowStore();
  
  // For now, use local state
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes.length > 0 ? initialNodes : []);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges.length > 0 ? initialEdges : []);
  
  const onConnect = useCallback(
    (params: Connection | WorkflowEdge) => {
      // Ensure we have an ID for the edge and all required properties
      const edgeWithId = {
        ...params,
        id: `edge-${Date.now()}`,
        animated: true,
        type: 'custom',
        data: {},
        // Ensure required properties are present
        source: params.source || '',
        target: params.target || ''
      };
      
      // Cast to any to bypass type checking since we've manually ensured the required properties
      return setEdges((eds) => addEdge(edgeWithId as any, eds));
    },
    [setEdges]
  );
  
  const onNodeClick = useCallback((_: any, node: any) => {
    // Will be used to show properties panel
    console.log('Node clicked:', node);
  }, []);
  
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);
  
  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const reactFlowBounds = event.currentTarget.getBoundingClientRect();
      const type = event.dataTransfer.getData('application/automeshNodeType');
      
      // Check if we have data
      if (!type) return;
      
      // Get the node data
      const nodeData = nodeTypeDefs[type as keyof typeof nodeTypeDefs];
      if (!nodeData) return;
      
      const position = {
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      };
      
      // Create new node
      const newNode = {
        id: `${type}_${Date.now()}`,
        type: 'base',
        position,
        data: { ...nodeData, type },
      };
      
      setNodes((nds) => nds.concat(newNode));
    },
    [setNodes]
  );
  
  return (
    <div className="workflow-container" onDragOver={onDragOver} onDrop={onDrop}>
      <Canvas
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        isReadOnly={isReadOnly}
        connectionLineType={ConnectionLineType.Bezier}
        connectionMode={ConnectionMode.Loose}
        defaultMarkerColor="#6366F1"
        backgroundVariant={BackgroundVariant.Dots}
      >
        <Panel position="top-left" className="workflow-header-panel">
          <h3 className="text-xl font-bold">
            {workflowId ? `Workflow: ${workflowId}` : 'New Workflow'}
          </h3>
        </Panel>
        
        {showLibrary && (
          <Panel position="top-right" className="node-library-panel">
            <NodeLibrary />
          </Panel>
        )}
        
        {showProperties && (
          <Panel position="bottom-right" className="properties-panel">
            <PropertiesPanel />
          </Panel>
        )}
      </Canvas>
    </div>
  );
}

// Wrap with provider to avoid context errors
export default function WorkflowCanvas(props: WorkflowCanvasProps) {
  return (
    <ReactFlowProvider>
      <WorkflowCanvasInner {...props} />
    </ReactFlowProvider>
  );
}
