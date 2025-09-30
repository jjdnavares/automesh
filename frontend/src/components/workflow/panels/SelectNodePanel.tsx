import { LucideChevronLeft } from 'lucide-react';
import { cn } from '../../../lib/utils';

interface SelectNodePanelProps {
  onClose?: () => void;
  className?: string;
}

export default function SelectNodePanel({ onClose, className }: SelectNodePanelProps) {
  return (
    <div className={cn(
      "select-node-panel bg-white border border-gray-200 shadow-sm rounded-lg overflow-hidden flex flex-col",
      className
    )}>
      {/* Header */}
      <div className="px-3 py-2 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
        <h3 className="font-medium text-gray-900">Select a node</h3>
        {onClose && (
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 p-1 rounded hover:bg-gray-200 transition-colors"
            aria-label="Close panel"
          >
            <LucideChevronLeft size={18} />
          </button>
        )}
      </div>
      
      {/* Content */}
      <div className="p-8 flex-1 flex items-center justify-center text-center">
        <p className="text-gray-500 text-lg">
          Select a node to edit its properties
        </p>
      </div>
    </div>
  );
}
