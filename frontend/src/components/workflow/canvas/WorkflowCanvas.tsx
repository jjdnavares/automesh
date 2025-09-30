import { useCallback, useState } from 'react';
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
import { LucideLayoutPanelLeft, LucideX, LucidePlay } from 'lucide-react';
import type { Connection, WorkflowEdge } from '../../../types/workflow';

import Canvas from './Canvas';
import { nodeTypes as nodeTypeDefs } from '../nodes/NodeTypes';
import BaseNode from '../nodes/BaseNode';
import CustomEdge from '../edges/CustomEdge';
import NodeLibrary from '../nodes/NodeLibrary';
import PropertiesPanel from '../panels/PropertiesPanel';
import SelectNodePanel from '../panels/SelectNodePanel';

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
  // Track if node panel is visible
  const [isPanelVisible, setIsPanelVisible] = useState(showLibrary);
  // Track if a node is selected
  const [selectedNode, setSelectedNode] = useState<any>(null);
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
    // Set the selected node for properties panel
    setSelectedNode(node);
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
        {/* Workflow title */}
        <Panel position="top-left" className="workflow-header-panel m-4">
          <div className="flex items-center gap-2">
            <h3 className="text-xl font-bold">
              {workflowId ? `Workflow: ${workflowId}` : 'New Workflow'}
            </h3>
          </div>
        </Panel>
        
        {/* Action buttons */}
        <Panel position="top-right" className="workflow-actions-panel m-4">
          <div className="flex items-center gap-2">
            <button className="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-sm font-medium">
              Run Workflow
            </button>
            <button className="px-3 py-1 bg-white border border-gray-300 text-gray-700 rounded hover:bg-gray-50 text-sm font-medium">
              Save
            </button>
          </div>
        </Panel>
        
        {/* Toggle node panel button */}
        <Panel position="top-right" className="toggle-panel-btn mr-2" style={{ top: '80px' }}>
          <button 
            className="px-3 py-1.5 bg-white border border-gray-200 text-gray-800 rounded-md hover:bg-gray-50 text-sm font-medium flex items-center gap-1.5 shadow-sm"
            onClick={() => setIsPanelVisible(!isPanelVisible)}
            title={isPanelVisible ? "Close nodes panel" : "Open nodes panel"}
          >
            {isPanelVisible ? (
              <>
                <LucideX size={16} className="text-gray-600" />
                <span className="whitespace-nowrap">Close panel</span>
              </>
            ) : (
              <>
                <LucideLayoutPanelLeft size={16} className="text-gray-600" />
                <span className="whitespace-nowrap">Open nodes panel</span>
              </>
            )}
          </button>
        </Panel>
        
        {/* Node library in right side panel */}
        {isPanelVisible && (
          <Panel position="top-right" className="node-library-panel mr-4" style={{ top: '130px' }}>
            <NodeLibrary />
          </Panel>
        )}

        {/* Select node panel or Properties panel below node library */}
        {isPanelVisible && showProperties && (
          <Panel 
            position="top-right" 
            className="select-node-panel mr-4" 
            style={{ top: 'calc(130px + 400px + 16px)' }}
          >
            {selectedNode ? (
              <PropertiesPanel nodeData={selectedNode} onClose={() => setSelectedNode(null)} />
            ) : (
              <SelectNodePanel />
            )}
          </Panel>
        )}

        {/* Execution button (bottom right) */}
        <Panel position="bottom-right" className="mr-4 mb-4">
          <button
            className="p-3 bg-orange-500 text-white rounded-md hover:bg-orange-600 transition-colors"
            title="Execute workflow"
          >
            <LucidePlay size={20} fill="white" />
          </button>
        </Panel>
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
