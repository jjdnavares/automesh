import { useCallback, useState } from 'react';
import type { ReactNode } from 'react';
import { 
  ReactFlow, 
  Background, 
  Controls, 
  MiniMap, 
  ConnectionLineType,
  PanOnScrollMode,
  BackgroundVariant
} from '@xyflow/react';
import type { 
  NodeMouseHandler, 
  EdgeMouseHandler,
  OnSelectionChangeFunc,
  Connection
} from '@xyflow/react';
import type { WorkflowNode, WorkflowEdge } from '../../../types/workflow';
import '@xyflow/react/dist/style.css';

// Define types needed for drag handlers
type NodeDragHandler = (event: React.MouseEvent, node: WorkflowNode) => void;
type SelectionDragHandler = (event: React.MouseEvent, nodes: WorkflowNode[]) => void;

interface CanvasProps {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  nodeTypes: Record<string, React.ComponentType<any>>;
  edgeTypes?: Record<string, React.ComponentType<any>>;
  onNodesChange: (changes: any) => void;
  onEdgesChange: (changes: any) => void;
  onConnect: (connection: WorkflowEdge | Connection) => void;
  onNodeClick?: NodeMouseHandler;
  onNodeDragStop?: NodeDragHandler;
  onSelectionDragStop?: SelectionDragHandler;
  onSelectionChange?: OnSelectionChangeFunc;
  onEdgeClick?: EdgeMouseHandler;
  children?: ReactNode;
  className?: string;
  snapToGrid?: boolean;
  snapGrid?: [number, number];
  defaultViewport?: { x: number; y: number; zoom: number };
  fitView?: boolean;
  fitViewOptions?: { padding?: number; includeHiddenNodes?: boolean };
  minZoom?: number;
  maxZoom?: number;
  defaultMarkerColor?: string;
  connectionLineStyle?: Record<string, any>;
  connectionLineType?: ConnectionLineType;
  connectionMode?: string;
  autoPanOnConnect?: boolean;
  elevateEdgesOnSelect?: boolean;
  deleteKeyCode?: string | null;
  selectionKeyCode?: string | null;
  multiSelectionKeyCode?: string | null;
  panActivationKeyCode?: string | null;
  panOnScroll?: boolean;
  panOnScrollMode?: PanOnScrollMode;
  zoomActivationKeyCode?: string | null;
  zoomOnScroll?: boolean;
  zoomOnPinch?: boolean;
  onlyRenderVisibleElements?: boolean;
  defaultEdgeOptions?: Record<string, any>;
  showMinimap?: boolean;
  showControls?: boolean;
  showBackground?: boolean;
  backgroundVariant?: BackgroundVariant;
  backgroundGap?: number;
  backgroundOpacity?: number;
  backgroundColor?: string;
  isReadOnly?: boolean;
  style?: React.CSSProperties;
}

export default function Canvas({
  nodes,
  edges,
  nodeTypes,
  edgeTypes,
  onNodesChange,
  onEdgesChange,
  onConnect,
  onNodeClick,
  onNodeDragStop,
  onSelectionDragStop,
  onSelectionChange,
  onEdgeClick,
  children,
  className = 'automesh-canvas',
  snapToGrid = true,
  snapGrid = [16, 16],
  defaultViewport = { x: 0, y: 0, zoom: 1 },
  fitView = true,
  fitViewOptions = { padding: 0.2 },
  minZoom = 0.1,
  maxZoom = 4,
  defaultMarkerColor = '#6366F1',
  connectionLineStyle = { stroke: '#6366F1', strokeWidth: 2 },
  connectionLineType = ConnectionLineType.Bezier,
  connectionMode = 'loose',
  autoPanOnConnect = true,
  elevateEdgesOnSelect = true,
  deleteKeyCode = 'Delete',
  selectionKeyCode = 'Shift',
  multiSelectionKeyCode = 'Meta',
  panActivationKeyCode = 'Space',
  panOnScroll = false,
  panOnScrollMode = PanOnScrollMode.Free,
  zoomActivationKeyCode = 'Meta',
  zoomOnScroll = true,
  zoomOnPinch = true,
  onlyRenderVisibleElements = false,
  defaultEdgeOptions = { animated: true, type: 'bezier' },
  showMinimap = true,
  showControls = true,
  showBackground = true,
  backgroundVariant = BackgroundVariant.Dots,
  backgroundGap = 16,
  backgroundOpacity = 0.6,
  backgroundColor = '#f8fafc',
  isReadOnly = false,
  style,
}: CanvasProps) {
  const [selectedNodes, setSelectedNodes] = useState<string[]>([]);
  const [selectedEdges, setSelectedEdges] = useState<string[]>([]);

  // Selection handling
  const onSelectionChangeHandler: OnSelectionChangeFunc = useCallback(
    ({ nodes, edges }) => {
      setSelectedNodes(nodes.map((node) => node.id));
      setSelectedEdges(edges.map((edge) => edge.id));
      
      // Forward the selection change if provided
      onSelectionChange?.({ nodes, edges });
    },
    [onSelectionChange]
  );

  const handlePaneClick = useCallback(() => {
    // Clear selection when clicking on the canvas background
    if (selectedNodes.length > 0 || selectedEdges.length > 0) {
      setSelectedNodes([]);
      setSelectedEdges([]);
    }
  }, [selectedNodes, selectedEdges]);

  return (
    <div className={`workflow-canvas ${className}`} style={{ width: '100%', height: '100%', ...style }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onNodeDragStop={onNodeDragStop}
        onSelectionDragStop={onSelectionDragStop}
        onSelectionChange={onSelectionChangeHandler}
        onEdgeClick={onEdgeClick}
        onPaneClick={handlePaneClick}
        snapToGrid={snapToGrid}
        snapGrid={snapGrid}
        defaultViewport={defaultViewport}
        fitView={fitView}
        fitViewOptions={fitViewOptions}
        minZoom={minZoom}
        maxZoom={maxZoom}
        defaultMarkerColor={defaultMarkerColor}
        connectionLineStyle={connectionLineStyle}
        connectionLineType={connectionLineType}
        connectionMode={connectionMode as any}
        autoPanOnConnect={autoPanOnConnect}
        elevateEdgesOnSelect={elevateEdgesOnSelect}
        deleteKeyCode={isReadOnly ? null : deleteKeyCode}
        selectionKeyCode={selectionKeyCode}
        multiSelectionKeyCode={multiSelectionKeyCode}
        panActivationKeyCode={panActivationKeyCode}
        panOnScroll={panOnScroll}
        panOnScrollMode={panOnScrollMode}
        zoomActivationKeyCode={zoomActivationKeyCode}
        zoomOnScroll={zoomOnScroll}
        zoomOnPinch={zoomOnPinch}
        onlyRenderVisibleElements={onlyRenderVisibleElements}
        defaultEdgeOptions={defaultEdgeOptions}
        nodesDraggable={!isReadOnly}
        nodesConnectable={!isReadOnly}
        elementsSelectable={!isReadOnly}
        className="automesh-reactflow"
      >
        {showBackground && (
          <Background
            variant={backgroundVariant}
            gap={backgroundGap}
            color={defaultMarkerColor}
            size={1}
            style={{ opacity: backgroundOpacity }}
          />
        )}

        {showControls && (
          <Controls position="bottom-right" showInteractive={false} />
        )}

        {showMinimap && (
          <MiniMap
            nodeStrokeColor={defaultMarkerColor}
            nodeColor={backgroundColor}
            nodeBorderRadius={2}
            maskColor="rgba(240, 240, 240, 0.6)"
            position="bottom-left"
          />
        )}

        {children}
      </ReactFlow>
    </div>
  );
}
