import { Handle, Position } from '@xyflow/react';
import { cn } from '../../lib/utils';
import type { NodeStatus } from './types';
import { getNodeStatusStyles, getNodeStatusIndicatorClass } from './types';

export interface CustomNodeData extends Record<string, unknown> {
  label: string;
  type: string;
  icon: string;
  color: string;
  status?: NodeStatus;
  description?: string;
  selected?: boolean;
}

export default function CustomNode({ data, isConnectable }: { data: CustomNodeData; isConnectable?: boolean }) {
  // Default status to idle if not provided
  const status = data.status || 'idle';
  const description = data.description || `Click to configure this ${data.type.toLowerCase()} node`;
  const selected = !!data.selected;
  
  // Node styling based on n8n design
  const nodeWidth = 180;
  const nodeHeight = 60;
  
  // Get status styles
  const statusStyle = getNodeStatusStyles(status);
  
  return (
    <div 
      className={cn(
        'custom-node flex items-center',
        selected ? 'shadow-[0_0_0_4px_rgba(99,102,241,0.3)]' : '',
        statusStyle
      )}
      style={{ 
        width: `${nodeWidth}px`,
        height: `${nodeHeight}px`,
        borderRadius: '8px',
        borderWidth: '2px',
        borderColor: selected ? '#6366F1' : '#e2e8f0',
        borderLeftWidth: '6px',
        borderLeftColor: data.color,
        backgroundColor: 'white',
        boxShadow: selected ? '0 4px 10px rgba(0, 0, 0, 0.12)' : '0 4px 6px rgba(0, 0, 0, 0.08)',
      }}
      data-status={status}
    >
      {/* Status indicator */}
      {/* Status indicator */}
      {status !== 'idle' && status !== 'disabled' && (
        <div 
          className={cn(
            'absolute right-1 top-1 h-2 w-2 rounded-full',
            getNodeStatusIndicatorClass(status)
          )}
        />
      )}
      
      {/* Disabled indicator - strikethrough line */}
      {status === 'disabled' && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="h-[1px] w-full bg-gray-400 transform rotate-12 opacity-70"></div>
        </div>
      )}
      
      <div className="flex p-3 items-center w-full">
        {/* Icon */}
        <div 
          className="custom-node-icon flex-shrink-0 flex items-center justify-center text-white rounded-md" 
          style={{ 
            backgroundColor: data.color,
            width: '32px',
            height: '32px',
            fontSize: '16px',
          }}
        >
          {data.icon}
        </div>
        
        {/* Content */}
        <div className="ml-2 flex flex-col flex-1 overflow-hidden">
          <div className="text-xs text-gray-500 uppercase tracking-wide font-medium">{data.type}</div>
          <div className="font-medium text-gray-800 truncate">{data.label}</div>
        </div>
      </div>
      
      {/* Description tooltip (could be shown on hover) */}
      <div className="custom-node-tooltip absolute -bottom-10 left-0 w-full opacity-0 transition-opacity group-hover:opacity-100 pointer-events-none">
        <div className="text-xs bg-gray-900 text-white p-1 rounded">
          {description}
        </div>
      </div>
      
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        id="in"
        isConnectable={isConnectable}
        className="w-3 h-3 !bg-gray-400 border-2 border-white hover:!bg-blue-500 hover:scale-125 transition-all duration-200"
        style={{ zIndex: 3 }}
      />
      
      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        id="out"
        isConnectable={isConnectable}
        className="w-3 h-3 !bg-gray-400 border-2 border-white hover:!bg-blue-500 hover:scale-125 transition-all duration-200"
        style={{ zIndex: 3 }}
      />
    </div>
  );
}
