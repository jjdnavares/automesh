import { useState, useEffect } from 'react';
import { Link } from '@tanstack/react-router';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  CardDescription
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useWorkflowStore } from '../../store/workflow/workflowStore';
import { Badge } from '@/components/ui/badge';
import { Search, Filter, ChevronDown, SortAsc, SortDesc, Clock, Plus, Copy, Trash2, Edit } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

// Sample workflow data (will be replaced with actual data from store)
const sampleWorkflows = [
  {
    id: 'workflow_1',
    name: 'Content Generation Pipeline',
    description: 'Automated content creation and distribution',
    version: '1.0.0',
    isActive: true,
    metadata: {
      createdAt: '2025-08-25T10:00:00Z',
      updatedAt: '2025-08-27T15:30:00Z',
      lastExecutedAt: '2025-08-28T08:45:00Z',
      executionCount: 12
    }
  },
  {
    id: 'workflow_2',
    name: 'Customer Onboarding',
    description: 'New customer welcome sequence',
    version: '1.0.0',
    isActive: false,
    metadata: {
      createdAt: '2025-08-20T14:20:00Z',
      updatedAt: '2025-08-26T09:15:00Z',
      lastExecutedAt: '2025-08-26T09:20:00Z',
      executionCount: 5
    }
  },
  {
    id: 'workflow_3',
    name: 'Data Transformation',
    description: 'Transform data between systems',
    version: '1.0.0',
    isActive: true,
    metadata: {
      createdAt: '2025-08-18T11:30:00Z',
      updatedAt: '2025-08-25T16:45:00Z',
      lastExecutedAt: '2025-08-27T14:10:00Z',
      executionCount: 23
    }
  }
];

export default function WorkflowListPage() {
  const { workflows, createNewWorkflow } = useWorkflowStore();
  const [isCreating, setIsCreating] = useState(false);
  const [newWorkflowName, setNewWorkflowName] = useState('');
  const [newWorkflowDescription, setNewWorkflowDescription] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('updatedAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  
  // Statistics
  const [stats, setStats] = useState({
    totalWorkflows: 0,
    activeWorkflows: 0,
    totalExecutions: 0,
    failureRate: '0%',
    timeSaved: '0h',
    runTime: '0s'
  });
  
  // Use sampleWorkflows for now, will be replaced with actual data from the store
  const workflowList = Object.keys(workflows).length > 0 
    ? Object.values(workflows) 
    : sampleWorkflows;

  useEffect(() => {
    // Calculate statistics
    const totalWorkflows = workflowList.length;
    const activeWorkflows = workflowList.filter(workflow => workflow.isActive).length;
    const totalExecutions = workflowList.reduce((sum, workflow) => sum + workflow.metadata.executionCount, 0);
    
    setStats({
      totalWorkflows,
      activeWorkflows,
      totalExecutions,
      failureRate: '0%', // Placeholder
      timeSaved: totalExecutions > 0 ? `${Math.floor(totalExecutions * 0.25)}h` : '0h', // Rough estimate
      runTime: '0s' // Placeholder
    });
  }, [workflowList]);

  const handleCreateWorkflow = () => {
    if (newWorkflowName) {
      createNewWorkflow(newWorkflowName, newWorkflowDescription);
      setNewWorkflowName('');
      setNewWorkflowDescription('');
      setIsCreating(false);
      // Redirect to the new workflow will be handled by the router
    }
  };

  // Filter and sort workflows
  const filteredWorkflows = workflowList.filter(workflow => {
    const matchesSearch = workflow.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         workflow.description?.toLowerCase().includes(searchQuery.toLowerCase());
    
    if (statusFilter === 'all') return matchesSearch;
    if (statusFilter === 'active') return matchesSearch && workflow.isActive;
    if (statusFilter === 'inactive') return matchesSearch && !workflow.isActive;
    
    return matchesSearch;
  }).sort((a, b) => {
    let comparison = 0;
    
    if (sortBy === 'name') {
      comparison = a.name.localeCompare(b.name);
    } else if (sortBy === 'updatedAt') {
      comparison = new Date(a.metadata.updatedAt).getTime() - new Date(b.metadata.updatedAt).getTime();
    } else if (sortBy === 'executionCount') {
      comparison = a.metadata.executionCount - b.metadata.executionCount;
    }
    
    return sortOrder === 'desc' ? -comparison : comparison;
  });
  
  return (
    <div className="workflow-list-page p-6 max-w-7xl mx-auto">
      <div className="flex flex-col gap-6">
        {/* Overview section */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle>Overview</CardTitle>
            <CardDescription>All workflows, credentials and executions you have access to</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-1">
                <div className="flex flex-col">
                  <div className="text-sm text-gray-500 mb-1">Prod. executions</div>
                  <div className="text-2xl font-semibold">{stats.activeWorkflows}</div>
                  <div className="text-xs text-gray-400">Last 7 days</div>
                </div>
              </div>
              <div className="col-span-1">
                <div className="flex flex-col">
                  <div className="text-sm text-gray-500 mb-1">Failure rate</div>
                  <div className="text-2xl font-semibold">{stats.failureRate}</div>
                  <div className="text-xs text-gray-400">Last 7 days</div>
                </div>
              </div>
              <div className="col-span-1">
                <div className="flex flex-col">
                  <div className="text-sm text-gray-500 mb-1">Time saved</div>
                  <div className="text-2xl font-semibold">{stats.timeSaved}</div>
                  <div className="text-xs text-gray-400">Last 7 days</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Filters and search */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 flex-1">
            <div className="relative w-[300px]">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-500" />
              <Input
                placeholder="Search workflows..."
                className="pl-8"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-center">
                <Filter className="mr-2 h-4 w-4 text-gray-500" />
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[140px]">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All statuses</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="inactive">Inactive</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center">
                <Clock className="mr-2 h-4 w-4 text-gray-500" />
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="updatedAt">Last updated</SelectItem>
                    <SelectItem value="name">Name</SelectItem>
                    <SelectItem value="executionCount">Execution count</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              >
                {sortOrder === 'asc' ? (
                  <SortAsc className="h-4 w-4" />
                ) : (
                  <SortDesc className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
          <Button onClick={() => setIsCreating(!isCreating)}>
            <Plus className="mr-2 h-4 w-4" />
            {isCreating ? 'Cancel' : 'Create Workflow'}
          </Button>
        </div>
        
        {/* Create workflow form */}
        {isCreating && (
          <Card className="mb-6 p-6">
            <CardHeader className="p-0 mb-4">
              <CardTitle>Create New Workflow</CardTitle>
              <CardDescription>Enter the details for your new workflow</CardDescription>
            </CardHeader>
            <div className="space-y-4">
              <div>
                <label htmlFor="workflow-name" className="text-sm font-medium block mb-2">
                  Name
                </label>
                <Input
                  id="workflow-name"
                  value={newWorkflowName}
                  onChange={(e) => setNewWorkflowName(e.target.value)}
                  placeholder="Enter workflow name"
                />
              </div>
              
              <div>
                <label htmlFor="workflow-description" className="text-sm font-medium block mb-2">
                  Description
                </label>
                <textarea
                  id="workflow-description"
                  className="flex h-20 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  value={newWorkflowDescription}
                  onChange={(e) => setNewWorkflowDescription(e.target.value)}
                  placeholder="Enter workflow description"
                />
              </div>
              
              <div className="flex justify-end">
                <Button onClick={handleCreateWorkflow} disabled={!newWorkflowName}>
                  Create Workflow
                </Button>
              </div>
            </div>
          </Card>
        )}
        
        {/* Workflow list */}
        <div className="grid grid-cols-1 gap-4">
          {filteredWorkflows.length === 0 ? (
            <Card className="text-center py-12">
              <div className="mb-4">
                <p className="text-gray-500 mb-2">No workflows found</p>
                <p className="text-gray-400 text-sm">Create your first workflow to get started</p>
              </div>
              <Button 
                variant="outline" 
                onClick={() => setIsCreating(true)}
                className="mx-auto"
              >
                <Plus className="mr-2 h-4 w-4" />
                Create workflow
              </Button>
            </Card>
          ) : (
            filteredWorkflows.map((workflow) => (
              <Card key={workflow.id} className="hover:border-primary/50 transition-colors">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <Link 
                        to="/workflow/$workflowId" 
                        params={{ workflowId: workflow.id }}
                        className="text-lg font-semibold text-gray-900 hover:text-primary transition-colors block"
                      >
                        {workflow.name}
                      </Link>
                      <p className="text-sm text-gray-600 mt-1">{workflow.description}</p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Badge variant={workflow.isActive ? "success" : "secondary"}>
                        {workflow.isActive ? 'Active' : 'Inactive'}
                      </Badge>
                      <div className="flex space-x-1">
                        <Button variant="ghost" size="icon" asChild>
                          <Link to="/workflow/$workflowId" params={{ workflowId: workflow.id }}>
                            <Edit className="h-4 w-4 text-gray-500" />
                          </Link>
                        </Button>
                        <Button variant="ghost" size="icon">
                          <Copy className="h-4 w-4 text-gray-500" />
                        </Button>
                        <Button variant="ghost" size="icon">
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex mt-6 text-sm text-gray-500 space-x-6">
                    <div>
                      Last updated: {new Date(workflow.metadata.updatedAt).toLocaleDateString()}
                    </div>
                    <div>
                      Last executed: {workflow.metadata.lastExecutedAt 
                        ? new Date(workflow.metadata.lastExecutedAt).toLocaleDateString() 
                        : 'Never'}
                    </div>
                    <div>
                      Executions: {workflow.metadata.executionCount}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
