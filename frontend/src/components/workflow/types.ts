/**
 * Node status types used across workflow components
 */
export type NodeStatus = 'idle' | 'running' | 'success' | 'error' | 'waiting' | 'disabled';

/**
 * Node type definitions
 */
export type NodeType = 'default' | 'trigger' | 'action' | 'config' | 'utility';

/**
 * Common node styling helpers
 */
export const getNodeStatusStyles = (status: NodeStatus): string => {
  switch (status) {
    case 'running':
      return 'border-yellow-400 bg-yellow-50';
    case 'success':
      return 'border-green-500';
    case 'error':
      return 'border-red-500';
    case 'waiting':
      return 'border-blue-400';
    case 'disabled':
      return 'border-gray-300 opacity-60';
    default:
      return '';
  }
};

/**
 * Get indicator styling for a node status
 */
export const getNodeStatusIndicatorClass = (status: NodeStatus): string => {
  switch (status) {
    case 'running':
      return 'bg-yellow-400 animate-pulse';
    case 'success':
      return 'bg-green-500';
    case 'error':
      return 'bg-red-500';
    case 'waiting':
      return 'bg-blue-400';
    default:
      return '';
  }
};
