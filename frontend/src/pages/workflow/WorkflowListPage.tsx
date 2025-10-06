import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from '@tanstack/react-router';
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
import { Search, Filter, SortAsc, SortDesc, Clock, Plus, Copy, Trash2, Edit, Loader2, Play, Download, Upload, FileText, CheckSquare, Square } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { toast } from 'sonner';
import WorkflowCardSkeleton from '@/components/workflow/WorkflowCardSkeleton';

export default function WorkflowListPage() {
  const navigate = useNavigate();
  const { 
    workflows, 
    isLoading,
    error,
    workflowsTotal,
    createNewWorkflow,
    fetchWorkflows,
    deleteWorkflow,
    duplicateWorkflow,
    toggleWorkflowStatus,
    fetchWorkflowStatistics,
    bulkDeleteWorkflows,
    bulkUpdateStatus,
    exportWorkflowToFile,
    importWorkflowFromFile,
    quickExecuteWorkflow,
    getTemplates,
    createWorkflowFromTemplate
  } = useWorkflowStore();
  const [isCreating, setIsCreating] = useState(false);
  const [newWorkflowName, setNewWorkflowName] = useState('');
  const [newWorkflowDescription, setNewWorkflowDescription] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('updated_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [workflowToDelete, setWorkflowToDelete] = useState<string | null>(null);
  const [actionInProgress, setActionInProgress] = useState<Record<string, boolean>>({});
  const [selectedWorkflows, setSelectedWorkflows] = useState<Set<string>>(new Set());
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [templatesDialogOpen, setTemplatesDialogOpen] = useState(false);
  const [templates, setTemplates] = useState<any[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Statistics
  const [stats, setStats] = useState<any>(null);
  
  // Get workflow list from store
  const workflowList = Object.values(workflows);

  // Fetch workflows on mount
  useEffect(() => {
    loadWorkflows();
    loadStatistics();
  }, []);
  
  // Reload workflows when filters change
  useEffect(() => {
    const timer = setTimeout(() => {
      loadWorkflows();
    }, 300); // Debounce search
    
    return () => clearTimeout(timer);
  }, [searchQuery, statusFilter, sortBy, sortOrder]);
  
  const loadWorkflows = async () => {
    const params: any = {
      sort_by: sortBy,
      sort_order: sortOrder,
    };
    
    if (searchQuery) params.search = searchQuery;
    if (statusFilter !== 'all') params.is_active = statusFilter === 'active';
    
    await fetchWorkflows(params);
  };
  
  const loadStatistics = async () => {
    try {
      const statistics = await fetchWorkflowStatistics(7);
      setStats(statistics);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  const handleCreateWorkflow = async () => {
    if (newWorkflowName && !isSubmitting) {
      setIsSubmitting(true);
      try {
        const workflowId = await createNewWorkflow(newWorkflowName, newWorkflowDescription);
        setNewWorkflowName('');
        setNewWorkflowDescription('');
        setIsCreating(false);
        toast.success('Workflow created', {
          description: `"${newWorkflowName}" has been created successfully.`,
        });
        // Navigate to the new workflow
        navigate({ to: '/workflow/$workflowId', params: { workflowId } });
      } catch (error) {
        console.error('Failed to create workflow:', error);
        toast.error('Error', {
          description: 'Failed to create workflow. Please try again.',
        });
      } finally {
        setIsSubmitting(false);
      }
    }
  };
  
  const handleDeleteWorkflow = async () => {
    if (!workflowToDelete) return;
    
    setActionInProgress({ ...actionInProgress, [workflowToDelete]: true });
    try {
      await deleteWorkflow(workflowToDelete);
      toast.success('Workflow deleted', {
        description: 'The workflow has been deleted successfully.',
      });
      setDeleteDialogOpen(false);
      setWorkflowToDelete(null);
      await loadWorkflows();
    } catch (error) {
      console.error('Failed to delete workflow:', error);
      toast.error('Error', {
        description: 'Failed to delete workflow. Please try again.',
      });
    } finally {
      setActionInProgress({ ...actionInProgress, [workflowToDelete]: false });
    }
  };
  
  const handleDuplicateWorkflow = async (id: string, name: string) => {
    setActionInProgress({ ...actionInProgress, [id]: true });
    try {
      const newId = await duplicateWorkflow(id, `${name} (Copy)`);
      toast.success('Workflow duplicated', {
        description: `"${name}" has been duplicated successfully.`,
      });
      await loadWorkflows();
      // Navigate to the duplicated workflow
      navigate({ to: '/workflow/$workflowId', params: { workflowId: newId } });
    } catch (error) {
      console.error('Failed to duplicate workflow:', error);
      toast.error('Error', {
        description: 'Failed to duplicate workflow. Please try again.',
      });
    } finally {
      setActionInProgress({ ...actionInProgress, [id]: false });
    }
  };
  
  const handleToggleStatus = async (id: string, currentStatus: boolean) => {
    setActionInProgress({ ...actionInProgress, [id]: true });
    try {
      await toggleWorkflowStatus(id, !currentStatus);
      toast.success('Status updated', {
        description: `Workflow is now ${!currentStatus ? 'active' : 'inactive'}.`,
      });
      await loadWorkflows();
    } catch (error) {
      console.error('Failed to toggle workflow status:', error);
      toast.error('Error', {
        description: 'Failed to update workflow status. Please try again.',
      });
    } finally {
      setActionInProgress({ ...actionInProgress, [id]: false });
    }
  };
  
  const handleSelectWorkflow = (id: string) => {
    const newSelected = new Set(selectedWorkflows);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedWorkflows(newSelected);
    setShowBulkActions(newSelected.size > 0);
  };
  
  const handleSelectAll = () => {
    if (selectedWorkflows.size === filteredWorkflows.length) {
      setSelectedWorkflows(new Set());
      setShowBulkActions(false);
    } else {
      setSelectedWorkflows(new Set(filteredWorkflows.map(w => w.id)));
      setShowBulkActions(true);
    }
  };
  
  const handleBulkDelete = async () => {
    try {
      const result = await bulkDeleteWorkflows(Array.from(selectedWorkflows));
      toast.success('Bulk delete completed', {
        description: `${result.deleted_count} workflow(s) deleted. ${result.failed_count} failed.`,
      });
      setSelectedWorkflows(new Set());
      setShowBulkActions(false);
      await loadWorkflows();
    } catch (error) {
      toast.error('Error', {
        description: 'Failed to delete workflows. Please try again.',
      });
    }
  };
  
  const handleBulkActivate = async () => {
    try {
      const result = await bulkUpdateStatus(Array.from(selectedWorkflows), true);
      toast.success('Bulk activate completed', {
        description: `${result.updated_count} workflow(s) activated. ${result.failed_count} failed.`,
      });
      setSelectedWorkflows(new Set());
      setShowBulkActions(false);
      await loadWorkflows();
    } catch (error) {
      toast.error('Error', {
        description: 'Failed to activate workflows. Please try again.',
      });
    }
  };
  
  const handleBulkDeactivate = async () => {
    try {
      const result = await bulkUpdateStatus(Array.from(selectedWorkflows), false);
      toast.success('Bulk deactivate completed', {
        description: `${result.updated_count} workflow(s) deactivated. ${result.failed_count} failed.`,
      });
      setSelectedWorkflows(new Set());
      setShowBulkActions(false);
      await loadWorkflows();
    } catch (error) {
      toast.error('Error', {
        description: 'Failed to deactivate workflows. Please try again.',
      });
    }
  };
  
  const handleQuickExecute = async (id: string, name: string) => {
    setActionInProgress({ ...actionInProgress, [id]: true });
    try {
      const executionId = await quickExecuteWorkflow(id);
      toast.success('Workflow started', {
        description: `"${name}" is now running. Execution ID: ${executionId}`,
      });
    } catch (error) {
      toast.error('Error', {
        description: 'Failed to execute workflow. Please try again.',
      });
    } finally {
      setActionInProgress({ ...actionInProgress, [id]: false });
    }
  };
  
  const handleExport = async (id: string) => {
    try {
      await exportWorkflowToFile(id);
      toast.success('Workflow exported', {
        description: 'The workflow has been downloaded.',
      });
    } catch (error) {
      toast.error('Error', {
        description: 'Failed to export workflow. Please try again.',
      });
    }
  };
  
  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    try {
      const workflowId = await importWorkflowFromFile(file);
      toast.success('Workflow imported', {
        description: 'The workflow has been imported successfully.',
      });
      await loadWorkflows();
      navigate({ to: '/workflow/$workflowId', params: { workflowId } });
    } catch (error) {
      toast.error('Error', {
        description: 'Failed to import workflow. Please check the file format.',
      });
    }
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  const loadTemplates = async () => {
    try {
      const templateList = await getTemplates();
      setTemplates(templateList);
      setTemplatesDialogOpen(true);
    } catch (error) {
      toast.error('Error', {
        description: 'Failed to load templates.',
      });
    }
  };
  
  const handleCreateFromTemplate = async (templateId: string, templateTitle: string) => {
    try {
      const workflowId = await createWorkflowFromTemplate(templateId, `${templateTitle} - ${new Date().toLocaleDateString()}`);
      toast.success('Workflow created from template', {
        description: `"${templateTitle}" has been created.`,
      });
      setTemplatesDialogOpen(false);
      await loadWorkflows();
      navigate({ to: '/workflow/$workflowId', params: { workflowId } });
    } catch (error) {
      toast.error('Error', {
        description: 'Failed to create workflow from template.',
      });
    }
  };

  // Workflows are already filtered and sorted by the API
  const filteredWorkflows = workflowList;
  
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
            {isLoading && !stats ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : stats ? (
              <div className="grid grid-cols-3 gap-4">
                <div className="col-span-1">
                  <div className="flex flex-col">
                    <div className="text-sm text-gray-500 mb-1">Total executions</div>
                    <div className="text-2xl font-semibold">{stats.total_executions || 0}</div>
                    <div className="text-xs text-gray-400">Last 7 days</div>
                  </div>
                </div>
                <div className="col-span-1">
                  <div className="flex flex-col">
                    <div className="text-sm text-gray-500 mb-1">Failure rate</div>
                    <div className="text-2xl font-semibold">{stats.failure_rate || '0%'}</div>
                    <div className="text-xs text-gray-400">Last 7 days</div>
                  </div>
                </div>
                <div className="col-span-1">
                  <div className="flex flex-col">
                    <div className="text-sm text-gray-500 mb-1">Time saved</div>
                    <div className="text-2xl font-semibold">{stats.time_saved || '0h'}</div>
                    <div className="text-xs text-gray-400">Last 7 days</div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-4 text-gray-500">No statistics available</div>
            )}
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
                    <SelectItem value="updated_at">Last updated</SelectItem>
                    <SelectItem value="title">Name</SelectItem>
                    <SelectItem value="execution_count">Execution count</SelectItem>
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
          <div className="flex gap-2">
            <Button variant="outline" onClick={loadTemplates}>
              <FileText className="mr-2 h-4 w-4" />
              Templates
            </Button>
            <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
              <Upload className="mr-2 h-4 w-4" />
              Import
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              className="hidden"
              onChange={handleImport}
            />
            <Button onClick={() => setIsCreating(!isCreating)}>
              <Plus className="mr-2 h-4 w-4" />
              {isCreating ? 'Cancel' : 'Create Workflow'}
            </Button>
          </div>
        </div>
        
        {/* Bulk Actions Toolbar */}
        {selectedWorkflows.size > 0 && (
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="font-medium text-blue-900">
                    {selectedWorkflows.size} workflow(s) selected
                  </span>
                  <Button variant="outline" size="sm" onClick={() => {
                    setSelectedWorkflows(new Set());
                    setShowBulkActions(false);
                  }}>
                    Clear Selection
                  </Button>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={handleBulkActivate}>
                    Activate All
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleBulkDeactivate}>
                    Deactivate All
                  </Button>
                  <Button variant="destructive" size="sm" onClick={handleBulkDelete}>
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete All
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
        
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
                <Button onClick={handleCreateWorkflow} disabled={!newWorkflowName || isSubmitting}>
                  {isSubmitting ? 'Creating...' : 'Create Workflow'}
                </Button>
              </div>
            </div>
          </Card>
        )}
        
        {/* Workflow list */}
        <div className="grid grid-cols-1 gap-4">
          {isLoading && workflowList.length === 0 ? (
            <>
              {/* Show skeleton loaders while loading */}
              {[1, 2, 3].map((i) => (
                <WorkflowCardSkeleton key={i} />
              ))}
            </>
          ) : error ? (
            <Card className="text-center py-12">
              <p className="text-red-500 mb-2">Error loading workflows</p>
              <p className="text-gray-400 text-sm mb-4">{error}</p>
              <Button variant="outline" onClick={loadWorkflows}>
                Retry
              </Button>
            </Card>
          ) : filteredWorkflows.length === 0 ? (
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
            <>
              {/* Select All Checkbox */}
              {filteredWorkflows.length > 0 && (
                <div className="flex items-center gap-2 mb-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleSelectAll}
                    className="text-sm"
                  >
                    {selectedWorkflows.size === filteredWorkflows.length ? (
                      <CheckSquare className="h-4 w-4 mr-2" />
                    ) : (
                      <Square className="h-4 w-4 mr-2" />
                    )}
                    Select All
                  </Button>
                </div>
              )}
              
              {filteredWorkflows.map((workflow) => (
                <Card key={workflow.id} className={`hover:border-primary/50 transition-colors ${selectedWorkflows.has(workflow.id) ? 'border-blue-400 bg-blue-50' : ''}`}>
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start">
                      <div className="flex items-start gap-3 flex-1">
                        {/* Checkbox */}
                        <Button
                          variant="ghost"
                          size="icon"
                          className="mt-1"
                          onClick={() => handleSelectWorkflow(workflow.id)}
                        >
                          {selectedWorkflows.has(workflow.id) ? (
                            <CheckSquare className="h-5 w-5 text-blue-600" />
                          ) : (
                            <Square className="h-5 w-5 text-gray-400" />
                          )}
                        </Button>
                        
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
                      </div>
                      <div className="flex items-center space-x-3">
                        <Badge 
                          variant={workflow.isActive ? "success" : "secondary"}
                          className="cursor-pointer"
                          onClick={() => handleToggleStatus(workflow.id, workflow.isActive)}
                        >
                          {actionInProgress[workflow.id] ? (
                            <Loader2 className="h-3 w-3 animate-spin" />
                          ) : (
                            workflow.isActive ? 'Active' : 'Inactive'
                          )}
                        </Badge>
                        <div className="flex space-x-1">
                          <Button 
                            variant="ghost" 
                            size="icon"
                            onClick={() => handleQuickExecute(workflow.id, workflow.name)}
                            disabled={actionInProgress[workflow.id]}
                            title="Quick Execute"
                          >
                            <Play className="h-4 w-4 text-green-600" />
                          </Button>
                          <Button variant="ghost" size="icon" asChild title="Edit">
                            <Link to="/workflow/$workflowId" params={{ workflowId: workflow.id }}>
                              <Edit className="h-4 w-4 text-gray-500" />
                            </Link>
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon"
                            onClick={() => handleDuplicateWorkflow(workflow.id, workflow.name)}
                            disabled={actionInProgress[workflow.id]}
                            title="Duplicate"
                          >
                            {actionInProgress[workflow.id] ? (
                              <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
                            ) : (
                              <Copy className="h-4 w-4 text-gray-500" />
                            )}
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon"
                            onClick={() => handleExport(workflow.id)}
                            title="Export"
                          >
                            <Download className="h-4 w-4 text-gray-500" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon"
                            onClick={() => {
                              setWorkflowToDelete(workflow.id);
                              setDeleteDialogOpen(true);
                            }}
                            disabled={actionInProgress[workflow.id]}
                            title="Delete"
                          >
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
              ))}
            </>
          )}
        </div>
      </div>
      
      {/* Delete confirmation dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the workflow
              and all associated execution history.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setWorkflowToDelete(null)}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteWorkflow}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
      
      {/* Templates dialog */}
      <AlertDialog open={templatesDialogOpen} onOpenChange={setTemplatesDialogOpen}>
        <AlertDialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <AlertDialogHeader>
            <AlertDialogTitle>Workflow Templates</AlertDialogTitle>
            <AlertDialogDescription>
              Choose a template to create a new workflow
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 py-4">
            {templates.length === 0 ? (
              <div className="col-span-2 text-center py-8 text-gray-500">
                No templates available
              </div>
            ) : (
              templates.map((template) => (
                <Card 
                  key={template.name} 
                  className="cursor-pointer hover:border-primary transition-colors"
                  onClick={() => handleCreateFromTemplate(template.name, template.title)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg">{template.title}</h3>
                        <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                        {template.category && (
                          <Badge variant="outline" className="mt-2">
                            {template.category}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
