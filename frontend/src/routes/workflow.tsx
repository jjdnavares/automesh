import { createFileRoute } from '@tanstack/react-router';
import WorkflowCanvasWrapper from '../components/workflow/WorkflowCanvas';

export const Route = createFileRoute('/workflow')({ 
  component: () => (
    <div className="p-6 h-screen">
      <h1 className="text-2xl font-bold mb-6">Workflow Editor</h1>
      <div className="h-[calc(100vh-120px)]">
        <WorkflowCanvasWrapper />
      </div>
    </div>
  )
});
