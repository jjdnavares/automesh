import { useState } from 'react';
import { Link } from '@tanstack/react-router';
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow 
} from '@/components/ui/table';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useWorkflowStore } from '../../store/workflow/workflowStore';

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
  
  // Use sampleWorkflows for now, will be replaced with actual data from the store
  const workflowList = Object.keys(workflows).length > 0 
    ? Object.values(workflows) 
    : sampleWorkflows;
  
  const handleCreateWorkflow = () => {
    if (newWorkflowName) {
      createNewWorkflow(newWorkflowName, newWorkflowDescription);
      setNewWorkflowName('');
      setNewWorkflowDescription('');
      setIsCreating(false);
      // Redirect to the new workflow will be handled by the router
    }
  };
  
  return (
    <div className="workflow-list-page">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-2xl font-bold">Workflows</h1>
          <p className="text-gray-500">Manage your automation workflows</p>
        </div>
        
        <Button
          onClick={() => setIsCreating(!isCreating)}
        >
          {isCreating ? 'Cancel' : 'Create Workflow'}
        </Button>
      </div>
      
      {isCreating && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Create New Workflow</CardTitle>
            <CardDescription>Enter the details for your new workflow</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid w-full items-center gap-1.5">
                <label htmlFor="workflow-name" className="text-sm font-medium">
                  Name
                </label>
                <input
                  id="workflow-name"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  value={newWorkflowName}
                  onChange={(e) => setNewWorkflowName(e.target.value)}
                  placeholder="Enter workflow name"
                />
              </div>
              
              <div className="grid w-full items-center gap-1.5">
                <label htmlFor="workflow-description" className="text-sm font-medium">
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
              
              <Button onClick={handleCreateWorkflow} disabled={!newWorkflowName}>
                Create
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
      
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Last Updated</TableHead>
                <TableHead>Last Executed</TableHead>
                <TableHead>Executions</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {workflowList.map((workflow) => (
                <TableRow key={workflow.id}>
                  <TableCell className="font-medium">
                    <Link to="/workflow/$workflowId" params={{ workflowId: workflow.id }}>
                      {workflow.name}
                    </Link>
                    <div className="text-xs text-gray-500">{workflow.description}</div>
                  </TableCell>
                  <TableCell>
                    <div className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                      workflow.isActive ? 'bg-green-50 text-green-700' : 'bg-gray-50 text-gray-700'
                    }`}>
                      {workflow.isActive ? 'Active' : 'Inactive'}
                    </div>
                  </TableCell>
                  <TableCell>
                    {new Date(workflow.metadata.updatedAt).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {workflow.metadata.lastExecutedAt 
                      ? new Date(workflow.metadata.lastExecutedAt).toLocaleDateString() 
                      : 'Never'}
                  </TableCell>
                  <TableCell>{workflow.metadata.executionCount}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button variant="ghost" size="sm">
                        <Link to="/workflow/$workflowId" params={{ workflowId: workflow.id }}>
                          Edit
                        </Link>
                      </Button>
                      <Button variant="ghost" size="sm">Clone</Button>
                      <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700">Delete</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              
              {workflowList.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <p className="text-gray-500">No workflows found</p>
                    <Button variant="outline" className="mt-2" onClick={() => setIsCreating(true)}>
                      Create your first workflow
                    </Button>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
