import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import type { WorkflowNode } from '../../../types/workflow';
import { cn } from '../../../lib/utils';

// Use properties from WorkflowNode but only what we need for this component
type BaseNodeProps = Pick<WorkflowNode, 'id' | 'selected'> & {
  data: WorkflowNode['data'];
  isConnectable?: boolean;
};

const BaseNode = ({
  id,
  data,
  selected,
  isConnectable
}: BaseNodeProps) => {
  // Extract node data with defaults
  const {
    label = 'Node',
    description = '',
    icon = '📄',
    color = '#6366F1',
    status = 'idle'
  } = data;

  // Status styling
  const statusStyles = {
    idle: 'bg-gray-200',
    running: 'bg-yellow-400 animate-pulse',
    success: 'bg-green-500',
    error: 'bg-red-500'
  };

  return (
    <div
      className={cn(
        'workflow-node relative rounded-lg shadow-md p-3 min-w-[160px]',
        'border-2 transition-all duration-200',
        selected ? 'border-blue-500 shadow-lg' : 'border-gray-200',
      )}
      style={{ 
        backgroundColor: 'white',
        borderLeftColor: color,
        borderLeftWidth: '6px'
      }}
    >
      {/* Status indicator */}
      <div 
        className={cn(
          'absolute -right-1 -top-1 h-3 w-3 rounded-full',
          statusStyles[status as keyof typeof statusStyles] || 'bg-gray-200'
        )}
      />

      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        isConnectable={isConnectable}
        className="w-3 h-3 !bg-gray-400 border-2 border-white"
      />

      {/* Node header */}
      <div className="flex items-center mb-2">
        <div className="text-xl mr-2">{icon}</div>
        <div className="font-medium text-gray-900 truncate flex-1">{label}</div>
      </div>

      {/* Optional description */}
      {description && (
        <div className="text-xs text-gray-500 mb-2 line-clamp-2">{description}</div>
      )}

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        isConnectable={isConnectable}
        className="w-3 h-3 !bg-gray-400 border-2 border-white"
      />

      {/* Node ID display for debugging */}
      <div className="absolute bottom-0 right-0 text-[9px] text-gray-400 px-1">
        {id}
      </div>
    </div>
  );
};

export default memo(BaseNode);
