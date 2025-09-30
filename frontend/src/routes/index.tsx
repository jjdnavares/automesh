import { createFileRoute } from '@tanstack/react-router'
import { Link } from '@tanstack/react-router'
import { ArrowRight, Workflow, Zap, Shield, Rocket } from 'lucide-react'
import { initialNodes, initialEdges } from '../components/workflow/nodeTypes'
import { ReactFlow, ReactFlowProvider, Background } from '@xyflow/react'
import CustomNode from '../components/workflow/CustomNode'
import '@xyflow/react/dist/style.css'
import { PageLayout } from '../components/layout/PageLayout'

export const Route = createFileRoute('/')({  
  component: Index,
})

// Define custom node types
const nodeTypes = { custom: CustomNode }

// Export the component so it can be used in routes.tsx
export function Index() {
  return (
    <PageLayout fullWidth className="space-y-16">
      {/* Hero Section */}
      <section className="relative px-6 py-16 md:py-24 mx-auto max-w-7xl flex flex-col md:flex-row items-center gap-12">
        <div className="flex-1 space-y-8">
          <div className="inline-flex items-center px-4 py-2 bg-indigo-50 text-indigo-700 rounded-full text-sm font-medium mb-4">
            <span>Workflow Automation</span>
            <span className="ml-2 px-2 py-1 bg-indigo-100 rounded-full text-xs">New</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-gray-900 leading-tight">
            Intelligent <span className="text-indigo-600">Workflow</span> Automation for Teams
          </h1>
          
          <p className="text-xl text-gray-600 max-w-2xl">
            Streamline your business processes with smart, AI-powered workflow automation. 
            Build, deploy, and scale workflows with minimal effort.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <Link to="/workflow" className="
              inline-flex items-center px-6 py-3 bg-indigo-600 text-white 
              rounded-lg hover:bg-indigo-700 transition-colors text-lg font-medium">
              Get Started <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
            <Link to="/about" className="
              inline-flex items-center px-6 py-3 border border-gray-300 
              rounded-lg hover:bg-gray-50 transition-colors text-lg font-medium text-gray-700">
              Learn More
            </Link>
          </div>
        </div>
        
        {/* Workflow Preview */}
        <div className="flex-1 h-[400px] md:h-[500px] w-full border-2 border-gray-200 rounded-xl shadow-lg overflow-hidden bg-white">
          <ReactFlowProvider>
            <div className="h-full w-full">
              <ReactFlow
                nodes={initialNodes}
                edges={initialEdges}
                nodeTypes={nodeTypes}
                fitView
                minZoom={0.5}
                maxZoom={1.5}
                nodesDraggable={false}
                nodesConnectable={false}
                elementsSelectable={false}
                proOptions={{ hideAttribution: true }}
              >
                <Background gap={12} size={1} color="#e2e8f0" />
              </ReactFlow>
            </div>
          </ReactFlowProvider>
        </div>
      </section>
      
      {/* Features Section */}
      <section className="px-6 py-24 mx-auto max-w-7xl">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Powerful Workflow Solutions</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Build, automate, and optimize your business processes with our intuitive tools
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
          {[
            {
              icon: <Workflow className="h-8 w-8 text-indigo-600" />,
              title: 'Visual Workflow Builder',
              description: 'Drag and drop interface to design complex workflows without coding',
            },
            {
              icon: <Zap className="h-8 w-8 text-indigo-600" />,
              title: 'AI-Powered Automation',
              description: 'Leverage AI to automate repetitive tasks and make smart decisions',
            },
            {
              icon: <Shield className="h-8 w-8 text-indigo-600" />,
              title: 'Enterprise Security',
              description: 'Robust security controls to protect your sensitive workflow data',
            },
          ].map((feature, i) => (
            <div key={i} className="bg-white p-8 rounded-xl border-2 border-gray-100 shadow-md hover:shadow-lg transition-shadow">
              <div className="bg-indigo-50 p-4 rounded-lg inline-flex items-center justify-center mb-5">{feature.icon}</div>
              <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
              <p className="text-gray-600 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>
      
      {/* Getting Started Section */}
      <section className="px-6 py-24 bg-gray-50">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Get Started in Minutes</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Follow these simple steps to begin automating your workflows
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10 mb-16">
            {[
              {
                step: 1,
                title: 'Create a workflow',
                description: 'Start with one of our templates or build from scratch',
              },
              {
                step: 2,
                title: 'Configure nodes',
                description: 'Connect and configure nodes to automate your process',
              },
              {
                step: 3,
                title: 'Deploy & Monitor',
                description: 'Deploy your workflow and monitor its performance',
              },
            ].map((step, i) => (
              <div key={i} className="bg-white p-8 rounded-xl shadow-md">
                <div className="flex items-center gap-5 mb-4">
                  <div className="flex-shrink-0 h-14 w-14 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xl">
                    {step.step}
                  </div>
                  <h3 className="text-2xl font-bold">{step.title}</h3>
                </div>
                <p className="text-gray-600 text-lg ml-[4.5rem]">{step.description}</p>
              </div>
            ))}
          </div>
          
          <div className="flex justify-center">
            <Link to="/workflow" className="
              inline-flex items-center px-8 py-4 bg-indigo-600 text-white 
              rounded-lg hover:bg-indigo-700 transition-colors text-lg font-medium shadow-lg hover:shadow-xl">
              Start Building <Rocket className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>
      
      {/* Call to Action */}
      <section className="px-6 py-24 mx-auto max-w-6xl">
        <div className="bg-gradient-to-r from-indigo-600 to-indigo-800 rounded-2xl p-12 md:p-16 text-center text-white shadow-xl">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to transform your workflow?</h2>
          <p className="text-xl mb-10 opacity-95 max-w-2xl mx-auto leading-relaxed">
            Join thousands of teams who have already automated their business processes with AutoMesh
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/workflow" className="
              inline-flex items-center justify-center px-8 py-4 bg-white text-indigo-600 
              rounded-lg hover:bg-gray-100 transition-colors text-lg font-medium shadow-md hover:shadow-lg">
              Get Started for Free
            </Link>
            <Link to="/about" className="
              inline-flex items-center justify-center px-8 py-4 border-2 border-white text-white 
              rounded-lg hover:bg-indigo-700 transition-colors text-lg font-medium">
              Learn More
            </Link>
          </div>
        </div>
      </section>
    </PageLayout>
  )
}