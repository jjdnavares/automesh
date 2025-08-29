import { memo } from 'react';
import { getSmoothStepPath, BaseEdge } from '@xyflow/react';
import type { Position } from '@xyflow/react';
import type { WorkflowEdge } from '../../../types/workflow';

// Define the props needed for the edge component based on WorkflowEdge
type CustomEdgeProps = {
  id: string;
  sourceX: number;
  sourceY: number;
  targetX: number;
  targetY: number;
  sourcePosition: Position;
  targetPosition: Position;
  style?: Record<string, any>;
  data?: WorkflowEdge['data'];
  markerEnd?: string;
};

function CustomEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  data,
  markerEnd,
}: CustomEdgeProps) {
  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const edgeStyles = {
    stroke: '#6366F1',
    strokeWidth: 2,
    ...style,
  };

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={edgeStyles}
        markerEnd={markerEnd}
      />
      {data?.label && (
        <foreignObject
          width={80}
          height={30}
          x={labelX - 40}
          y={labelY - 15}
          className="edge-label-container"
          requiredExtensions="http://www.w3.org/1999/xhtml"
        >
          <div className="bg-white/80 text-xs p-1 rounded shadow text-center">
            {data.label}
          </div>
        </foreignObject>
      )}
    </>
  );
}

export default memo(CustomEdge);
