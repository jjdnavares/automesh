import { createFileRoute } from '@tanstack/react-router';
import WorkflowCanvasWrapper from '../components/workflow/WorkflowCanvas';
import { PageLayout } from '../components/layout/PageLayout';

export const Route = createFileRoute('/workflow')({ 
  component: () => (
    <PageLayout 
      title="Workflow Editor" 
      subtitle="Build, design and automate your workflows with an intuitive interface"
    >
      <div className="flex flex-col gap-4 mb-8">
        <div className="flex flex-wrap gap-3">
          <button className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors text-sm font-medium">New Workflow</button>
          <button className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors text-sm font-medium">Import</button>
          <button className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors text-sm font-medium">Templates</button>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
        <WorkflowCanvasWrapper />
      </div>
    </PageLayout>
  )
});
