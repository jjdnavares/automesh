import frappe
import json
import argparse
import sys
from frappe.utils import now
from .engine import WorkflowEngine


def execute_workflow(workflow_id, input_data=None, wait=True):
    """
    Execute a workflow from the console
    
    Args:
        workflow_id: ID of the workflow to execute
        input_data: Input data for the workflow (JSON string or dict)
        wait: Whether to wait for workflow completion
    
    Returns:
        Execution ID
    """
    if not workflow_id:
        print("Error: Workflow ID is required")
        return None
    
    # Parse input data if provided as string
    if isinstance(input_data, str):
        try:
            input_data = json.loads(input_data)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON input data: {input_data}")
            return None
    
    if not input_data:
        input_data = {}
    
    # Create execution
    execution = frappe.new_doc("Automesh Execution")
    execution.workflow = workflow_id
    execution.status = "queued"
    execution.start_time = now()
    
    if input_data:
        execution.input_data = json.dumps(input_data)
    
    execution.insert()
    
    # Update workflow
    workflow = frappe.get_doc("Automesh Workflow", workflow_id)
    workflow.execution_count = (workflow.execution_count or 0) + 1
    workflow.last_executed_at = now()
    workflow.save()
    
    execution_id = execution.name
    print(f"Created workflow execution: {execution_id}")
    
    if wait:
        # Execute workflow directly (not as background job)
        engine = WorkflowEngine(execution_id)
        success = engine.execute()
        
        if success:
            print(f"Workflow execution completed successfully")
            
            # Get execution result
            execution.reload()
            if execution.output_data:
                try:
                    output = json.loads(execution.output_data)
                    print(f"Workflow output: {json.dumps(output, indent=2)}")
                except:
                    print(f"Workflow output: {execution.output_data}")
        else:
            print(f"Workflow execution failed")
            print(f"Error: {execution.error_message}")
    else:
        # Start background job
        frappe.enqueue(
            "automesh.automesh.workflow_engine.engine.process_workflow_execution",
            execution=execution_id,
            timeout=1800
        )
        print(f"Workflow execution started in background")
    
    return execution_id


def main():
    """Console entry point"""
    parser = argparse.ArgumentParser(description="Execute an Automesh workflow")
    parser.add_argument("workflow_id", help="ID of the workflow to execute")
    parser.add_argument("--input", "-i", help="Input data (JSON string)")
    parser.add_argument("--file", "-f", help="Input data file (JSON)")
    parser.add_argument("--background", "-b", action="store_true", help="Run in background")
    
    args = parser.parse_args()
    
    input_data = None
    
    if args.file:
        try:
            with open(args.file, 'r') as f:
                input_data = json.load(f)
        except Exception as e:
            print(f"Error reading input file: {e}")
            return 1
    elif args.input:
        try:
            input_data = json.loads(args.input)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON input: {args.input}")
            return 1
    
    execute_workflow(args.workflow_id, input_data, not args.background)
    return 0


if __name__ == "__main__":
    sys.exit(main())
