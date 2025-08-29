import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { 
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle 
} from '@/components/ui/card';
import WorkflowCanvas from '../../components/workflow/canvas/WorkflowCanvas';
import { useWorkflowStore } from '../../store/workflow/workflowStore';

export default function WorkflowPage() {
  const { 
    currentWorkflowId,
    nodes,
    edges,
    executionStatus,
    startExecution,
    stopExecution,
    resetExecution,
    saveWorkflow
  } = useWorkflowStore();
  
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  const handleStartExecution = () => {
    startExecution();
  };
  
  const handleStopExecution = () => {
    stopExecution();
  };
  
  const handleResetExecution = () => {
    resetExecution();
  };
  
  const handleSaveWorkflow = () => {
    saveWorkflow();
  };
  
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };
  
  return (
    <div className={`workflow-page ${isFullscreen ? 'fullscreen' : ''}`}>
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-2xl font-bold">
            {currentWorkflowId ? `Edit Workflow` : 'Create New Workflow'}
          </h1>
          <p className="text-gray-500">
            {currentWorkflowId ? `ID: ${currentWorkflowId}` : 'Build your automation workflow'}
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={toggleFullscreen}
          >
            {isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          </Button>
          
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleSaveWorkflow}
          >
            Save
          </Button>
          
          {executionStatus === 'idle' ? (
            <Button 
              variant="default" 
              size="sm"
              onClick={handleStartExecution}
            >
              Run Workflow
            </Button>
          ) : executionStatus === 'running' ? (
            <Button 
              variant="destructive" 
              size="sm"
              onClick={handleStopExecution}
            >
              Stop
            </Button>
          ) : (
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleResetExecution}
            >
              Reset
            </Button>
          )}
        </div>
      </div>
      
      <div className="workflow-container" style={{ height: isFullscreen ? 'calc(100vh - 100px)' : '700px' }}>
        <WorkflowCanvas 
          workflowId={currentWorkflowId || undefined}
          initialNodes={nodes}
          initialEdges={edges}
        />
      </div>
      
      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Workflow Information</CardTitle>
          <CardDescription>Details and statistics about this workflow</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h3 className="font-medium">Nodes</h3>
              <p className="text-2xl">{nodes.length}</p>
            </div>
            <div>
              <h3 className="font-medium">Connections</h3>
              <p className="text-2xl">{edges.length}</p>
            </div>
            <div>
              <h3 className="font-medium">Status</h3>
              <p className="text-2xl capitalize">{executionStatus}</p>
            </div>
          </div>
        </CardContent>
        <CardFooter className="bg-gray-50 flex justify-between">
          <p className="text-sm text-gray-500">Last updated: {new Date().toLocaleString()}</p>
          <Button variant="ghost" size="sm">View History</Button>
        </CardFooter>
      </Card>
    </div>
  );
}
