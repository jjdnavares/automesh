import { useState } from 'react';
import { nodeTypes, nodeCategories, getNodeTypesByCategory } from './NodeTypes';
import { cn } from '../../../lib/utils';

export default function NodeLibrary() {
  const [activeCategory, setActiveCategory] = useState('automation');
  const [searchQuery, setSearchQuery] = useState('');

  // Filter node types based on search query
  const filteredNodeTypes = searchQuery
    ? Object.values(nodeTypes).filter(
        (node) => 
          node.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
          node.description.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : getNodeTypesByCategory(activeCategory);

  // Handle drag start
  const onDragStart = (event: React.DragEvent<HTMLDivElement>, nodeType: string) => {
    event.dataTransfer.setData('application/automeshNodeType', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div className="node-library bg-white rounded-lg border border-gray-200 shadow-md overflow-hidden w-[250px]">
      <div className="px-3 py-2 border-b border-gray-200">
        <h3 className="font-medium text-gray-900">Node Library</h3>
        <div className="mt-2">
          <input
            type="text"
            placeholder="Search nodes..."
            className="w-full text-sm px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {!searchQuery && (
        <div className="flex border-b border-gray-200 overflow-x-auto">
          {Object.values(nodeCategories).map((category) => (
            <button
              key={category.id}
              className={cn(
                'px-3 py-2 text-sm whitespace-nowrap',
                activeCategory === category.id
                  ? 'text-indigo-600 border-b-2 border-indigo-600 font-medium'
                  : 'text-gray-500 hover:text-gray-700'
              )}
              onClick={() => setActiveCategory(category.id)}
            >
              <span className="mr-1">{category.icon}</span>
              {category.label}
            </button>
          ))}
        </div>
      )}

      <div className="overflow-y-auto max-h-[400px] p-2">
        {filteredNodeTypes.length === 0 ? (
          <div className="text-center text-gray-500 py-4">
            No nodes found
          </div>
        ) : (
          filteredNodeTypes.map((nodeType) => (
            <div
              key={nodeType.type}
              className="node-item bg-white border border-gray-200 rounded-md mb-2 p-2 cursor-grab hover:shadow-md transition-shadow"
              draggable
              onDragStart={(event) => onDragStart(event, nodeType.type)}
            >
              <div className="flex items-center">
                <div className="h-8 w-8 flex items-center justify-center mr-2 rounded text-lg" style={{ color: nodeType.color }}>
                  {nodeType.icon}
                </div>
                <div>
                  <div className="font-medium text-sm">{nodeType.label}</div>
                  <div className="text-xs text-gray-500 line-clamp-1">{nodeType.description}</div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
