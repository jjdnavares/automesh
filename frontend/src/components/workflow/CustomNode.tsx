import { Handle, Position } from '@xyflow/react';

export interface CustomNodeData extends Record<string, unknown> {
  label: string;
  type: string;
  icon: string;
  color: string;
}

export default function CustomNode({ data, isConnectable }: { data: CustomNodeData; isConnectable?: boolean }) {
  return (
    <div className="custom-node" style={{ borderTop: `3px solid ${data.color}` }}>
      <div className="custom-node-header" style={{ backgroundColor: data.color + '20' }}>
        <div className="custom-node-icon" style={{ backgroundColor: data.color }}>
          {data.icon}
        </div>
        <div className="custom-node-type">{data.type}</div>
      </div>
      <div className="custom-node-content">
        <div className="custom-node-label">{data.label}</div>
      </div>
      <Handle
        type="target"
        position={Position.Left}
        id="in"
        isConnectable={isConnectable}
        className="custom-handle"
      />
      <Handle
        type="source"
        position={Position.Right}
        id="out"
        isConnectable={isConnectable}
        className="custom-handle"
      />
    </div>
  );
}
