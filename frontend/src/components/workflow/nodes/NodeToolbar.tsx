import { Play, Trash2, PauseCircle, Settings, MoreHorizontal } from 'lucide-react';
import { cn } from '../../../lib/utils';
import type { NodeStatus } from '../types';

interface NodeToolbarProps {
  nodeId: string;
  readOnly?: boolean;
  onDelete?: (id: string) => void;
  onRun?: (id: string) => void;
  onToggle?: (id: string) => void;
  onSettings?: (id: string) => void;
  onMore?: (id: string, event: React.MouseEvent) => void;
  isDisabled?: boolean;
  showStatus?: boolean;
  status?: NodeStatus;
}

export default function NodeToolbar({
  nodeId,
  readOnly = false,
  onDelete,
  onRun,
  onToggle,
  onSettings,
  onMore,
  isDisabled = false,
  status = 'idle',
  showStatus = false
}: NodeToolbarProps) {
  if (readOnly) return null;
  
  return (
    <div 
      className={cn(
        'absolute -top-9 left-0 z-10 flex items-center gap-1 p-1 rounded-md bg-white/95 backdrop-blur-sm border border-gray-200 shadow-sm',
        'opacity-0 group-hover:opacity-100 transition-opacity duration-200',
        'node-toolbar'
      )}
    >
      <button 
        className="p-1 rounded-sm hover:bg-gray-100 text-gray-600 transition-colors"
        onClick={() => onRun?.(nodeId)}
        title="Run node"
      >
        <Play size={14} />
      </button>
      
      <button 
        className={cn(
          "p-1 rounded-sm hover:bg-gray-100 transition-colors",
          isDisabled ? "text-blue-500" : "text-gray-600"
        )}
        onClick={() => onToggle?.(nodeId)}
        title={isDisabled ? "Enable node" : "Disable node"}
      >
        <PauseCircle size={14} />
      </button>
      
      <button 
        className="p-1 rounded-sm hover:bg-gray-100 text-gray-600 transition-colors"
        onClick={() => onSettings?.(nodeId)}
        title="Node settings"
      >
        <Settings size={14} />
      </button>
      
      <button 
        className="p-1 rounded-sm hover:bg-gray-100 text-gray-600 transition-colors"
        onClick={() => onDelete?.(nodeId)}
        title="Delete node"
      >
        <Trash2 size={14} />
      </button>
      
      <button 
        className="p-1 rounded-sm hover:bg-gray-100 text-gray-600 transition-colors"
        onClick={(e) => onMore?.(nodeId, e)}
        title="More options"
      >
        <MoreHorizontal size={14} />
      </button>
      
      {showStatus && status !== 'idle' && (
        <div className="ml-1 flex items-center">
          <div 
            className={cn(
              "h-2 w-2 rounded-full",
              status === 'running' ? "bg-yellow-400 animate-pulse" : "",
              status === 'success' ? "bg-green-500" : "",
              status === 'error' ? "bg-red-500" : "",
              status === 'waiting' ? "bg-blue-400" : ""
            )}
          />
        </div>
      )}
    </div>
  );
}
