import { createFileRoute } from '@tanstack/react-router'
import { PageLayout } from '../components/layout/PageLayout'

export const Route = createFileRoute('/about')({
  component: About,
})

function About() {
  return (
    <PageLayout
      title="About AutoMesh"
      subtitle="Learn more about our intelligent workflow automation platform"
    >
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-8 mb-12 overflow-hidden">
        <h2 className="text-2xl font-semibold mb-4">Our Mission</h2>
        <p className="text-gray-700 mb-6">
          AutoMesh was built with the vision of making complex workflow automation accessible to everyone. 
          We believe that teams should spend time on creative and strategic tasks, not repetitive processes.
        </p>
        
        <h2 className="text-2xl font-semibold mb-4">Key Features</h2>
        <ul className="list-disc pl-6 space-y-2 text-gray-700 mb-6">
          <li>Visual drag-and-drop workflow builder</li>
          <li>AI-powered automation capabilities</li>
          <li>Enterprise-grade security</li>
          <li>Seamless integration with your existing tools</li>
          <li>Advanced analytics and reporting</li>
        </ul>
        
        <h2 className="text-2xl font-semibold mb-4">Get Started Today</h2>
        <p className="text-gray-700">
          Ready to transform how your team works? Start building your first workflow today and 
          see the difference AutoMesh can make for your organization.
        </p>
      </div>
    </PageLayout>
  )
}