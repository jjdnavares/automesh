import type { Edge } from '@xyflow/react';

// Define node categories for organization in the library
export const nodeCategories = {
  automation: {
    id: 'automation',
    label: 'Automation',
    description: 'Automation workflow nodes',
    icon: '⚙️',
  },
  content: {
    id: 'content',
    label: 'Content',
    description: 'Content creation and management',
    icon: '📝',
  },
  communication: {
    id: 'communication',
    label: 'Communication',
    description: 'Communication and notification tools',
    icon: '📢',
  },
  integration: {
    id: 'integration',
    label: 'Integration',
    description: 'External systems integration',
    icon: '🔄',
  },
};

// Define node types with their properties
export const nodeTypes = {
  // Content nodes
  seoWriter: {
    type: 'seoWriter',
    label: 'SEO Writer',
    description: 'Generate SEO-optimized content',
    icon: '📝',
    color: '#10B981', // Green
    category: 'content',
    inputs: [],
    outputs: ['content'],
  },
  contentFormatter: {
    type: 'contentFormatter',
    label: 'Content Formatter',
    description: 'Format and structure content',
    icon: '📄',
    color: '#8B5CF6', // Purple
    category: 'content',
    inputs: ['content'],
    outputs: ['formattedContent'],
  },
  
  // Communication nodes
  webPageContent: {
    type: 'webPageContent',
    label: 'Web Page Content',
    description: 'Post content to web pages',
    icon: '🌐',
    color: '#3B82F6', // Blue
    category: 'communication',
    inputs: ['content', 'formattedContent'],
    outputs: ['notification'],
  },
  emailBlast: {
    type: 'emailBlast',
    label: 'Email Blast',
    description: 'Send emails to subscribers',
    icon: '📧',
    color: '#F59E0B', // Amber
    category: 'communication',
    inputs: ['content', 'formattedContent'],
    outputs: ['notification'],
  },
  notification: {
    type: 'notification',
    label: 'Notification',
    description: 'Send system notifications',
    icon: '🔔',
    color: '#EF4444', // Red
    category: 'communication',
    inputs: ['trigger'],
    outputs: [],
  },
  
  // Integration nodes
  apiRequest: {
    type: 'apiRequest',
    label: 'API Request',
    description: 'Make external API requests',
    icon: '🔌',
    color: '#6366F1', // Indigo
    category: 'integration',
    inputs: ['trigger', 'data'],
    outputs: ['response'],
  },
  dataTransform: {
    type: 'dataTransform',
    label: 'Data Transform',
    description: 'Transform data between formats',
    icon: '🔄',
    color: '#EC4899', // Pink
    category: 'integration',
    inputs: ['data'],
    outputs: ['transformedData'],
  },
  
  // Automation nodes
  trigger: {
    type: 'trigger',
    label: 'Trigger',
    description: 'Start workflow execution',
    icon: '▶️',
    color: '#0EA5E9', // Sky
    category: 'automation',
    inputs: [],
    outputs: ['trigger'],
  },
  condition: {
    type: 'condition',
    label: 'Condition',
    description: 'Branch based on conditions',
    icon: '🔀',
    color: '#F97316', // Orange
    category: 'automation',
    inputs: ['any'],
    outputs: ['true', 'false'],
  },
  delay: {
    type: 'delay',
    label: 'Delay',
    description: 'Add delay between steps',
    icon: '⏲️',
    color: '#64748B', // Slate
    category: 'automation',
    inputs: ['trigger'],
    outputs: ['trigger'],
  },
};

// Helper function to get all node types by category
export const getNodeTypesByCategory = (categoryId: string) => {
  return Object.values(nodeTypes).filter(
    (nodeType) => nodeType.category === categoryId
  );
};

// Define sample initial nodes
export const initialNodes = [
  {
    id: '1',
    type: 'base',
    position: { x: 50, y: 150 },
    data: { ...nodeTypes.seoWriter, label: 'Generate Product Description' }
  },
  {
    id: '2',
    type: 'base',
    position: { x: 400, y: 150 },
    data: { ...nodeTypes.webPageContent, label: 'Post to Product Page' }
  },
  {
    id: '3',
    type: 'base',
    position: { x: 750, y: 150 },
    data: { ...nodeTypes.emailBlast, label: 'Send to Premium Subscribers' }
  }
];

// Define sample initial edges
export const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true, type: 'custom' },
  { id: 'e2-3', source: '2', target: '3', animated: true, type: 'custom' }
];
