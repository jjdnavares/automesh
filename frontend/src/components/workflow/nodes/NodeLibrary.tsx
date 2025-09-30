import { useState, useEffect, useRef, useCallback } from 'react';
import { nodeTypes, nodeCategories, getNodeTypesByCategory } from './NodeTypes';
import { cn } from '../../../lib/utils';
import { 
  LucideX, 
  LucideChevronLeft, 
  LucideChevronRight, 
  LucideSearch, 
  LucidePlus, 
  LucideStar, 
  LucideFlame, 
  LucideWrench, 
  LucideSettings,
  LucideInfo
} from 'lucide-react';

interface NodeAction {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  category: string;
}

interface ViewStack {
  id: string;
  title: string;
  subtitle?: string;
  icon?: string;
  categoryId: string;
  search?: string;
  transitionDirection: 'in' | 'out';
  isSubcategory?: boolean;
  nodeType?: any;
}

// Define action categories
const actionCategories = {
  triggers: 'Triggers',
  actions: 'Actions',
  transformations: 'Transformations',
  settings: 'Settings',
};

// Action category icons
const categoryIcons = {
  triggers: <LucideStar size={16} className="text-yellow-500" />,
  actions: <LucideFlame size={16} className="text-orange-500" />,
  transformations: <LucideWrench size={16} className="text-blue-500" />,
  settings: <LucideSettings size={16} className="text-gray-500" />,
};

export default function NodeLibrary() {
  const [activeCategory, setActiveCategory] = useState('automation');
  const [searchQuery, setSearchQuery] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [viewStacks, setViewStacks] = useState<ViewStack[]>([{ 
    id: 'main', 
    title: 'Nodes',
    categoryId: 'automation',
    transitionDirection: 'in' 
  }]);
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);
  
  // Focus search input when clicking the search icon
  const focusSearch = () => {
    searchInputRef.current?.focus();
    setIsSearchFocused(true);
  };

  // Get current view stack
  const activeViewStack = viewStacks[viewStacks.length - 1];
  
  // Push a new view stack (for subcategories)
  const pushViewStack = (newStack: Partial<ViewStack> & { categoryId: string }) => {
    setViewStacks(prevStacks => [...prevStacks, {
      id: `stack-${Date.now()}`,
      title: newStack.title || 'Subcategory',
      subtitle: newStack.subtitle,
      icon: newStack.icon,
      transitionDirection: 'in',
      isSubcategory: true,
      ...newStack
    }]);
  };
  
  // Pop the current view stack
  const popViewStack = () => {
    if (viewStacks.length > 1) {
      setViewStacks(prevStacks => prevStacks.slice(0, -1));
    }
  };

  // Update active category when changing tabs
  useEffect(() => {
    if (!activeViewStack.isSubcategory) {
      setActiveCategory(activeViewStack.categoryId);
    }
  }, [activeViewStack]);

  // Filter node types based on search query
  const getFilteredNodeTypes = useCallback(() => {
    if (searchQuery) {
      return Object.values(nodeTypes).filter(
        (node) => 
          node.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
          node.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    } else {
      return getNodeTypesByCategory(activeCategory);
    }
  }, [searchQuery, activeCategory]);

  const filteredNodeTypes = getFilteredNodeTypes();

  // Handle drag start
  const onDragStart = (event: React.DragEvent<HTMLDivElement>, nodeType: string) => {
    event.dataTransfer.setData('application/automeshNodeType', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  // Handle search
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  // Clear search
  const clearSearch = () => {
    setSearchQuery('');
    searchInputRef.current?.focus();
  };

  // Current node for actions view and expanded categories
  const [currentNodeForActions, setCurrentNodeForActions] = useState<any>(null);
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({
    triggers: true,
    actions: true,
    transformations: false,
    settings: false,
  });

  // Mock actions data - in a real implementation, these would come from the node definition
  const getMockActionsForNode = (): Record<string, NodeAction[]> => ({
    triggers: [
      { id: 'onCreated', name: 'On Created', description: 'Trigger when item is created', icon: <LucideStar size={14} />, category: 'triggers' },
      { id: 'onUpdated', name: 'On Updated', description: 'Trigger when item is updated', icon: <LucideStar size={14} />, category: 'triggers' },
    ],
    actions: [
      { id: 'create', name: 'Create', description: 'Create a new item', icon: <LucideFlame size={14} />, category: 'actions' },
      { id: 'update', name: 'Update', description: 'Update an existing item', icon: <LucideFlame size={14} />, category: 'actions' },
      { id: 'delete', name: 'Delete', description: 'Delete an item', icon: <LucideFlame size={14} />, category: 'actions' },
    ],
    transformations: [
      { id: 'transform', name: 'Transform', description: 'Transform data structure', icon: <LucideWrench size={14} />, category: 'transformations' },
      { id: 'filter', name: 'Filter', description: 'Filter data based on conditions', icon: <LucideWrench size={14} />, category: 'transformations' },
    ],
    settings: [
      { id: 'config', name: 'Config', description: 'Configure node settings', icon: <LucideSettings size={14} />, category: 'settings' },
    ]
  });

  // Toggle category expansion
  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };
  
  // View node actions
  const viewNodeActions = (nodeType: any) => {
    setCurrentNodeForActions(nodeType);
    pushViewStack({
      categoryId: activeCategory,
      title: nodeType.label,
      icon: nodeType.icon,
      subtitle: 'Actions',
      nodeType
    });
  };

  // Handle action selection
  const handleActionSelect = (action: any) => {
    console.log('Selected action:', action, 'for node:', currentNodeForActions);
    // Here you would handle adding the node with the specific action
    // Similar to how n8n does it
    popViewStack();
  };

  return (
    <div className={cn(
      "node-library bg-white border border-gray-200 shadow-md overflow-hidden transition-all duration-300",
      isExpanded ? "w-[350px] h-[600px]" : "w-[280px] h-[500px]",
      "rounded-lg flex flex-col"
    )}>
      {/* Stack transition container */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        {viewStacks.map((stack, index) => (
          <div 
            key={stack.id}
            className={cn(
              "absolute inset-0 flex flex-col w-full transition-transform duration-300 ease-in-out",
              index !== viewStacks.length - 1 ? "-translate-x-full" : "translate-x-0"
            )}
          >
            {/* Header with title and back button */}
            <div className="px-3 py-2 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
              <div className="flex items-center">
                {stack.isSubcategory && (
                  <button 
                    onClick={popViewStack} 
                    className="mr-2 text-gray-500 hover:text-gray-700 p-1 rounded hover:bg-gray-200 transition-colors"
                  >
                    <LucideChevronLeft size={18} />
                  </button>
                )}
                {stack.icon && <span className="mr-2">{stack.icon}</span>}
                <div>
                  <h3 className="font-medium text-gray-900">{stack.title}</h3>
                  {stack.subtitle && <p className="text-xs text-gray-500">{stack.subtitle}</p>}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button 
                  onClick={focusSearch} 
                  className="text-gray-500 hover:text-gray-700 p-1 rounded hover:bg-gray-200 transition-colors"
                >
                  <LucideSearch size={18} />
                </button>
                <button 
                  onClick={() => setIsExpanded(!isExpanded)} 
                  className="text-gray-500 hover:text-gray-700 p-1 rounded hover:bg-gray-200 transition-colors"
                >
                  {isExpanded ? <LucideChevronRight size={18} /> : <LucideChevronLeft size={18} />}
                </button>
              </div>
            </div>

            {/* Search input */}
            <div className={cn(
              "px-3 py-2 border-b border-gray-200 transition-all duration-300",
              isSearchFocused || searchQuery ? "opacity-100" : "opacity-100"
            )}>
              <div className="relative">
                <input
                  ref={searchInputRef}
                  type="text"
                  placeholder="Search nodes..."
                  className="w-full text-sm px-3 py-1.5 pr-8 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  value={searchQuery}
                  onChange={handleSearch}
                  onFocus={() => setIsSearchFocused(true)}
                  onBlur={() => setIsSearchFocused(false)}
                />
                {searchQuery && (
                  <button 
                    onClick={clearSearch}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    <LucideX size={14} />
                  </button>
                )}
              </div>
            </div>

            {/* Category tabs - horizontal scrolling */}
            {!searchQuery && !stack.isSubcategory && (
              <div className="flex border-b border-gray-200 overflow-x-auto sticky top-0 bg-white z-10">
                {Object.values(nodeCategories).map((category) => (
                  <button
                    key={category.id}
                    className={cn(
                      'px-3 py-2 text-sm whitespace-nowrap flex items-center',
                      activeCategory === category.id
                        ? 'text-indigo-600 border-b-2 border-indigo-600 font-medium'
                        : 'text-gray-500 hover:text-gray-700'
                    )}
                    onClick={() => {
                      setViewStacks([{
                        id: 'main',
                        title: 'Nodes',
                        categoryId: category.id,
                        transitionDirection: 'in'
                      }]);
                    }}
                  >
                    <span className="mr-1">{category.icon}</span>
                    <span className={cn(!isExpanded && 'hidden')}>{category.label}</span>
                  </button>
                ))}
              </div>
            )}

            {/* Show either the node list or the actions panel based on whether it's a subcategory view */}
            {stack.isSubcategory && stack.nodeType ? (
              <div className="flex-1 flex flex-col">
                <div className="overflow-y-auto flex-1">
                  {/* Node Actions View */}
                  <div className="space-y-1">
                    {Object.entries(getMockActionsForNode()).map(([category, actions]) => (
                      <div key={category} className="border-b border-gray-100 last:border-0">
                        {/* Category header */}
                        <button 
                          className={cn(
                            'w-full px-3 py-2 flex items-center justify-between text-left',
                            expandedCategories[category] ? 'bg-gray-50' : 'bg-white'
                          )}
                          onClick={() => toggleCategory(category)}
                        >
                          <div className="flex items-center text-sm font-medium">
                            {categoryIcons[category as keyof typeof categoryIcons]}
                            <span className="ml-1.5">{actionCategories[category as keyof typeof actionCategories]}</span>
                          </div>
                          <div className="text-gray-400">
                            {expandedCategories[category] ? '−' : '+'}
                          </div>
                        </button>
                        
                        {/* Category items */}
                        {expandedCategories[category] && (
                          <div className="py-1 pl-6 pr-2 bg-gray-50">
                            {actions.map(action => (
                              <button
                                key={action.id}
                                className="w-full px-2 py-1.5 text-left rounded-sm hover:bg-gray-100 flex items-center group"
                                onClick={() => handleActionSelect(action)}
                                title={action.description}
                              >
                                <span className="mr-2 text-gray-600 w-5 flex justify-center">{action.icon}</span>
                                <div className="text-sm font-medium">{action.name}</div>
                                <LucideInfo 
                                  size={14} 
                                  className="text-gray-400 opacity-0 group-hover:opacity-100 ml-auto" 
                                />
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              /* Node items - grid layout when expanded */
              <div className="overflow-y-auto flex-1 p-2">
                {filteredNodeTypes.length === 0 ? (
                  <div className="text-center text-gray-500 py-4">
                    No nodes found
                  </div>
                ) : (
                  <div className={cn(
                    isExpanded ? "grid grid-cols-2 gap-2" : "space-y-2"
                  )}>
                    {filteredNodeTypes.map((nodeType) => (
                      <div
                        key={nodeType.type}
                        className="node-item bg-white border border-gray-200 rounded-md p-2 cursor-grab hover:shadow-md transition-all hover:border-indigo-300 hover:translate-y-[-1px] relative group"
                        draggable
                        onDragStart={(event) => onDragStart(event, nodeType.type)}
                        title={nodeType.description}
                      >
                        <div className="flex items-center">
                          <div 
                            className="h-8 w-8 flex items-center justify-center mr-2 rounded-md text-white flex-shrink-0"
                            style={{ backgroundColor: nodeType.color }}
                          >
                            {nodeType.icon}
                          </div>
                          <div className="flex-1 overflow-hidden">
                            <div className="font-medium text-sm truncate">{nodeType.label}</div>
                            {isExpanded && (
                              <div className="text-xs text-gray-500 line-clamp-1">{nodeType.description}</div>
                            )}
                          </div>
                          <button 
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              viewNodeActions(nodeType);
                            }}
                            className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 text-gray-400 hover:text-gray-600 p-1 rounded transition-opacity"
                            title="View node actions"
                          >
                            <LucidePlus size={14} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-2 border-t border-gray-200 bg-gray-50 text-center">
        <span className="text-xs text-gray-500">{filteredNodeTypes.length} nodes available</span>
      </div>
    </div>
  );
}
