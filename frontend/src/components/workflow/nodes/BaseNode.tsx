import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import type { WorkflowNode } from '../../../types/workflow';
import { cn } from '../../../lib/utils';
import NodeToolbar from './NodeToolbar';
import type { NodeStatus } from '../types';
import { getNodeStatusStyles, getNodeStatusIndicatorClass } from '../types';

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
    status = 'idle' as NodeStatus,
    type = 'default',
    configurable = false,
  } = data;

  // Calculate node dimensions (similar to n8n's calculateNodeSize)
  const nodeWidth = configurable ? 200 : 150;
  const nodeHeight = 60;

  // Get status styling from helper function
  const statusStyle = getNodeStatusStyles(status);

  // Handle node type specific styling
  const isConfigurable = configurable;
  const isTriggerNode = type === 'trigger';

  // Event handlers for toolbar actions
  const handleDelete = () => {
    console.log('Delete node:', id);
    // Implementation would go here
  };
  
  const handleRun = () => {
    console.log('Run node:', id);
    // Implementation would go here
  };
  
  const handleToggle = () => {
    console.log('Toggle node:', id);
    // Implementation would go here
  };
  
  const handleSettings = () => {
    console.log('Open settings for node:', id);
    // Implementation would go here
  };
  
  const handleMore = (nodeId: string, event: React.MouseEvent) => {
    console.log('More options for node:', nodeId, event);
    // Implementation would go here
  };

  return (
    <div
      className={cn(
        'workflow-node relative flex items-center justify-center group',
        'border-2 transition-all duration-200',
        selected ? 'shadow-[0_0_0_4px_rgba(99,102,241,0.3)]' : '',
        statusStyle,
        status === 'running' ? 'animate-pulse-subtle' : ''
      )}
      style={{ 
        backgroundColor: 'white',
        borderColor: selected ? '#6366F1' : '#e2e8f0',
        borderRadius: isTriggerNode ? '24px 8px 8px 24px' : '8px',
        width: `${nodeWidth}px`,
        height: `${nodeHeight}px`
      }}
      data-test-id="canvas-node"
      data-node-name={label}
      data-node-type={type}
    >
      {/* Node Toolbar */}
      <NodeToolbar
        nodeId={id}
        onDelete={handleDelete}
        onRun={handleRun}
        onToggle={handleToggle}
        onSettings={handleSettings}
        onMore={handleMore}
        isDisabled={status === 'disabled'}
        status={status !== 'disabled' ? status : 'idle'}
        showStatus={false} /* We're already showing status in the node */
      />
      
      {/* Status indicator */}
      {status !== 'idle' && status !== 'disabled' && (
        <div 
          className={cn(
            'absolute right-1 top-1 h-2 w-2 rounded-full',
            getNodeStatusIndicatorClass(status)
          )}
        />
      )}

      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        isConnectable={isConnectable}
        className="w-3 h-3 !bg-gray-400 border-2 border-white hover:!bg-blue-500 hover:scale-125 transition-all duration-200"
        style={{ zIndex: 3 }}
      />

      {/* Node icon */}
      <div 
        className="flex-shrink-0 flex items-center justify-center text-gray-800" 
        style={{ 
          fontSize: configurable ? '20px' : '24px',
          width: configurable ? '30px' : '40px',
          height: configurable ? '30px' : '40px'
        }}
      >
        {icon}
      </div>

      {/* Node content */}
      {isConfigurable ? (
        <div className="ml-2 mr-2 flex-grow overflow-hidden">
          <div className="font-medium text-gray-800 truncate">{label}</div>
          {description && (
            <div className="text-xs text-gray-500 truncate">{description}</div>
          )}
        </div>
      ) : (
        <div className="absolute top-full mt-1 flex flex-col items-center w-full pointer-events-none">
          <div className="font-medium text-gray-800 text-center text-sm">{label}</div>
          {description && (
            <div className="text-xs text-gray-500 text-center line-clamp-2 max-w-[180px]">{description}</div>
          )}
        </div>
      )}

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        isConnectable={isConnectable}
        className="w-3 h-3 !bg-gray-400 border-2 border-white hover:!bg-blue-500 hover:scale-125 transition-all duration-200"
        style={{ zIndex: 3 }}
      />
      
      {/* Disabled indicator - strikethrough line */}
      {status === 'disabled' && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
          <div className="h-[1px] w-full bg-gray-400 transform rotate-12 opacity-70"></div>
        </div>
      )}

      {/* Node ID (small and discreet) */}
      <div className="absolute bottom-0 right-1 text-[8px] text-gray-400 opacity-60">
        {id.substring(0, 8)}
      </div>
    </div>
  );
};

export default memo(BaseNode);
