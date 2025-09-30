import { useState } from 'react';
import { useReactFlow } from '@xyflow/react';
import { cn } from '../../../lib/utils';

// Define a type for node data that matches what we're using in the component
interface NodeData {
  label?: string;
  type?: string;
  icon?: string;
  description?: string;
  parameters?: Record<string, any>;
  [key: string]: any;
}

// Define a node type to use in this component
interface FlowNode {
  id: string;
  selected?: boolean;
  data: NodeData;
  position?: { x: number; y: number };
  [key: string]: any;
}

interface PropertiesPanelProps {
  nodeData?: any;
  onClose?: () => void;
}

export default function PropertiesPanel({ nodeData, onClose }: PropertiesPanelProps) {
  const { getNodes, setNodes } = useReactFlow();
  const [isExpanded, setIsExpanded] = useState(true);
  
  // Get all selected nodes
  const selectedNodes = nodeData ? [nodeData] : getNodes().filter((node) => node.selected) as FlowNode[];
  const hasSelectedNode = selectedNodes.length > 0;
  
  // Get the first selected node (for now we'll just show properties for one node)
  const selectedNode = hasSelectedNode ? selectedNodes[0] : undefined;
  
  // Update node label
  const updateNodeLabel = (nodeId: string, newLabel: string) => {
    setNodes((nodes) =>
      nodes.map((node: any) => {
        if (node.id === nodeId) {
          // Create a safe copy of node data
          const nodeData = node.data ? { ...node.data } : {};
          
          return {
            ...node,
            data: {
              ...nodeData,
              label: newLabel,
            },
          };
        }
        return node;
      })
    );
  };
  
  // Update node data
  const updateNodeData = (nodeId: string, key: string, value: any) => {
    setNodes((nodes) =>
      nodes.map((node: any) => {
        if (node.id === nodeId) {
          // Make a copy of the node and safely access parameters
          const nodeData = node.data ? { ...node.data } : {};
          const parameters = nodeData.parameters ? { ...nodeData.parameters } : {};
          
          return {
            ...node,
            data: {
              ...nodeData,
              parameters: {
                ...parameters,
                [key]: value,
              },
            },
          };
        }
        return node;
      })
    );
  };
  
  // Toggle panel
  const togglePanel = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div 
      className={cn(
        "properties-panel bg-white rounded-lg border border-gray-200 shadow-md overflow-hidden transition-all",
        isExpanded ? "w-[280px]" : "w-[40px]"
      )}
    >
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-200 bg-gray-50">
        <h3 className={cn("font-medium text-gray-900 flex items-center", !isExpanded && "hidden")}>
          {hasSelectedNode && (
            <span className="mr-2 w-5 h-5 flex items-center justify-center text-white rounded-md"
                  style={{ backgroundColor: selectedNode?.data.color || '#6366F1' }}>
              {selectedNode?.data.icon || '⚙️'}
            </span>
          )}
          {hasSelectedNode ? (selectedNode?.data.label || 'Node Properties') : 'Select a node'}
        </h3>
        <div className="flex gap-1">
          {onClose && (
            <button 
              onClick={onClose}
              className="p-1 rounded-md hover:bg-gray-100 text-gray-500"
              aria-label="Close panel"
            >
              ✕
            </button>
          )}
          <button 
            onClick={togglePanel}
            className="p-1 rounded-md hover:bg-gray-100 text-gray-500"
            aria-label={isExpanded ? 'Collapse panel' : 'Expand panel'}
          >
            {isExpanded ? '◀' : '▶'}
          </button>
        </div>
      </div>
      
      {isExpanded && (
        <div className="overflow-y-auto max-h-[500px] p-3">
          {!hasSelectedNode ? (
            <div className="text-center text-gray-500 py-4">
              Select a node to edit its properties
            </div>
          ) : selectedNode ? (
            <div>
              <div className="mb-4">
                <div className="flex items-center mb-2">
                  <span className="text-lg mr-2">{selectedNode.data.icon || ''}</span>
                  <span className="font-medium">{selectedNode.data.type || ''}</span>
                </div>
                
                <div className="mb-3">
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Node Name
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-gray-50 hover:bg-white focus:bg-white transition-colors"
                    value={selectedNode.data.label || ''}
                    onChange={(e) => updateNodeLabel(selectedNode.id, e.target.value)}
                    placeholder="Enter node name"
                  />
                </div>
              </div>
              
              {/* Display node-specific parameters based on type */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2 border-b border-gray-200 pb-1">
                  Parameters
                </h4>
                
                {/* This will be expanded based on node type */}
                <div className="space-y-3">
                  {/* Just showing sample parameters based on node type */}
                  {selectedNode.data.type === 'seoWriter' && (
                    <>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                          Keywords
                        </label>
                        <input
                          type="text"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-gray-50 hover:bg-white focus:bg-white transition-colors"
                          placeholder="Enter keywords"
                          value={selectedNode.data.parameters?.keywords || ''}
                          onChange={(e) => 
                            updateNodeData(selectedNode.id, 'keywords', e.target.value)
                          }
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                          Content Length
                        </label>
                        <select
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-gray-50 hover:bg-white focus:bg-white transition-colors appearance-none"
                          value={selectedNode.data.parameters?.contentLength || 'medium'}
                          onChange={(e) =>
                            updateNodeData(selectedNode.id, 'contentLength', e.target.value)
                          }
                        >
                          <option value="short">Short</option>
                          <option value="medium">Medium</option>
                          <option value="long">Long</option>
                        </select>
                      </div>
                    </>
                  )}
                  
                  {selectedNode.data.type === 'emailBlast' && (
                    <>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                          Recipient List
                        </label>
                        <select
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-gray-50 hover:bg-white focus:bg-white transition-colors appearance-none"
                          value={selectedNode.data.parameters?.recipientList || 'all'}
                          onChange={(e) =>
                            updateNodeData(selectedNode.id, 'recipientList', e.target.value)
                          }
                        >
                          <option value="all">All Subscribers</option>
                          <option value="premium">Premium Subscribers</option>
                          <option value="free">Free Subscribers</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                          Email Subject
                        </label>
                        <input
                          type="text"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-gray-50 hover:bg-white focus:bg-white transition-colors"
                          placeholder="Email subject line"
                          value={selectedNode.data.parameters?.subject || ''}
                          onChange={(e) =>
                            updateNodeData(selectedNode.id, 'subject', e.target.value)
                          }
                        />
                      </div>
                    </>
                  )}
                  
                  {/* Default parameters for any node type */}
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Description
                    </label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-gray-50 hover:bg-white focus:bg-white transition-colors"
                      rows={2}
                      placeholder="Enter node description"
                      value={selectedNode.data.description || ''}
                      onChange={(e) => {
                        setNodes((nodes) =>
                          nodes.map((node) => {
                            if (node.id === selectedNode.id) {
                              return {
                                ...node,
                                data: {
                                  ...node.data,
                                  description: e.target.value,
                                },
                              };
                            }
                            return node;
                          })
                        );
                      }}
                    />
                  </div>
                </div>
              </div>
              
              <div className="mt-4 pt-3 border-t border-gray-200">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-[10px] text-gray-400 truncate overflow-hidden flex-grow">ID: {selectedNode.id}</span>
                  <div className="flex space-x-2">
                    <button
                      className="px-2 py-1 bg-gray-50 hover:bg-gray-100 border border-gray-300 rounded text-xs transition-colors"
                      onClick={() => {
                        setNodes((nodes) =>
                          nodes.map((node) => {
                            if (node.id === selectedNode.id) {
                              return {
                                ...node,
                                selected: false,
                              };
                            }
                            return node;
                          })
                        );
                      }}
                    >
                      Deselect
                    </button>
                    <button
                      className="px-2 py-1 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 rounded text-xs transition-colors"
                      onClick={() => {
                        setNodes((nodes) =>
                          nodes.filter((node) => node.id !== selectedNode.id)
                        );
                      }}
                    >
                      Delete
                    </button>
                  </div>
                </div>
                
                <div className="mt-3 pt-2 border-t border-gray-100 flex justify-end">
                  <button
                    className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md text-xs font-medium transition-colors"
                    onClick={() => {/* Apply changes function would go here */}}
                  >
                    Apply
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-4">
              Error loading node properties
            </div>
          )}
        </div>
      )}
    </div>
  );
}
