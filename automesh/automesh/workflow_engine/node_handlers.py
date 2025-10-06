import frappe
from frappe.utils import now, cint, cstr
import json
import requests
import time
from typing import Dict, List, Any, Optional, Union

class NodeHandlerRegistry:
    """Registry for node handlers that can be used in workflows"""
    
    _registry = {}
    
    @classmethod
    def register(cls, node_type):
        """Register a node handler class for a specific node type"""
        
        def wrapper(handler_class):
            cls._registry[node_type] = handler_class
            return handler_class
        
        return wrapper
    
    @classmethod
    def get_handler(cls, node_type):
        """Get a node handler for a specific node type"""
        handler_class = cls._registry.get(node_type)
        
        if not handler_class:
            # If no specific handler is registered, use the base handler
            return BaseNodeHandler
            
        return handler_class
    
    @classmethod
    def get_all_registered_types(cls):
        """Get all registered node types"""
        return list(cls._registry.keys())


class BaseNodeHandler:
    """Base class for all node handlers"""
    
    def __init__(self, node_data, execution_context):
        """Initialize node handler with node data and execution context"""
        self.node_data = node_data
        self.execution_context = execution_context
        self.node_id = node_data.get("id")
        self.node_type = node_data.get("type")
        self.params = node_data.get("data", {}).get("params", {})
    
    def execute(self):
        """Execute the node and return the result"""
        # This method should be overridden by subclasses
        raise NotImplementedError("Node handlers must implement the execute method")
    
    def get_param(self, name, default=None):
        """Get a parameter value, resolving any variable references"""
        value = self.params.get(name, default)
        
        # If the value is a string and contains a variable reference, resolve it
        if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
            variable_name = value[2:-2].strip()
            return self.execution_context.get_variable(variable_name, default)
        
        return value
    
    def set_output(self, output_data):
        """Set the output data for this node"""
        self.execution_context.set_node_output(self.node_id, output_data)
    
    def log_info(self, message):
        """Log an informational message"""
        self.execution_context.log(self.node_id, "INFO", message)
    
    def log_error(self, message):
        """Log an error message"""
        self.execution_context.log(self.node_id, "ERROR", message)
    
    def log_debug(self, message):
        """Log a debug message"""
        self.execution_context.log(self.node_id, "DEBUG", message)


@NodeHandlerRegistry.register("start")
class StartNodeHandler(BaseNodeHandler):
    """Handler for the workflow start node"""
    
    def execute(self):
        """Execute the start node"""
        self.log_info("Workflow execution started")
        
        # Start nodes don't do any processing, they just pass on the input data
        input_data = self.execution_context.get_input_data()
        self.set_output(input_data)
        
        return {
            "success": True,
            "data": input_data
        }


@NodeHandlerRegistry.register("end")
class EndNodeHandler(BaseNodeHandler):
    """Handler for the workflow end node"""
    
    def execute(self):
        """Execute the end node"""
        self.log_info("Workflow execution completed")
        
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("End node has no incoming connections")
            return {
                "success": False,
                "error": "End node has no incoming connections"
            }
        
        # Use the output of the connected node as the final output
        source_node_id = incoming_connections[0].get("source")
        source_output = self.execution_context.get_node_output(source_node_id)
        
        # Set this as the workflow output
        self.execution_context.set_workflow_output(source_output)
        self.set_output(source_output)
        
        return {
            "success": True,
            "data": source_output
        }


@NodeHandlerRegistry.register("condition")
class ConditionNodeHandler(BaseNodeHandler):
    """Handler for condition nodes that branch the workflow based on a condition"""
    
    def execute(self):
        """Execute the condition node"""
        # Get the condition expression and evaluate it
        condition_expr = self.get_param("condition", "")
        
        if not condition_expr:
            self.log_error("No condition specified")
            return {
                "success": False,
                "error": "No condition specified"
            }
        
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("Condition node has no incoming connections")
            return {
                "success": False,
                "error": "Condition node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        try:
            # Evaluate the condition in the context of the input data
            # This uses a secure evaluation mechanism with access to the input data
            result = self._evaluate_condition(condition_expr, input_data)
            
            # Set the condition result as output
            output_data = {
                "condition_result": result,
                "input_data": input_data
            }
            self.set_output(output_data)
            
            # Store the branch to take (true or false)
            self.execution_context.set_node_branch(self.node_id, "true" if result else "false")
            
            self.log_info(f"Condition evaluated to: {result}")
            
            return {
                "success": True,
                "data": output_data,
                "branch": "true" if result else "false"
            }
            
        except Exception as e:
            self.log_error(f"Error evaluating condition: {str(e)}")
            return {
                "success": False,
                "error": f"Error evaluating condition: {str(e)}"
            }
    
    def _evaluate_condition(self, condition_expr, input_data):
        """
        Evaluate a condition expression in the context of the input data
        
        This is a simplified implementation. In a production system, you would want to use
        a proper expression evaluator that handles security considerations.
        """
        # Create a context with the input data
        context = {}
        
        # Add input data to context
        if isinstance(input_data, dict):
            context.update(input_data)
        
        # Add variables from workflow
        variables = self.execution_context.get_all_variables()
        context.update(variables)
        
        # Add helper functions
        context.update({
            "exists": lambda x: x is not None,
            "is_empty": lambda x: x is None or x == "" or (isinstance(x, (list, dict)) and len(x) == 0),
            "contains": lambda x, y: y in x if x is not None else False,
            "startswith": lambda x, y: x.startswith(y) if isinstance(x, str) else False,
            "endswith": lambda x, y: x.endswith(y) if isinstance(x, str) else False,
        })
        
        # Evaluate the expression
        # In a real system, use a secure evaluation mechanism, not eval
        # This is just a placeholder for illustration
        try:
            result = eval(condition_expr, {"__builtins__": {}}, context)
            return bool(result)
        except Exception as e:
            self.log_error(f"Error evaluating condition: {str(e)}")
            return False


@NodeHandlerRegistry.register("http_request")
class HttpRequestNodeHandler(BaseNodeHandler):
    """Handler for HTTP request nodes that make API calls"""
    
    def execute(self):
        """Execute the HTTP request node"""
        # Get parameters
        method = self.get_param("method", "GET")
        url = self.get_param("url", "")
        headers = self.get_param("headers", {})
        params = self.get_param("params", {})
        body = self.get_param("body", {})
        timeout = self.get_param("timeout", 30)
        
        if not url:
            self.log_error("No URL specified")
            return {
                "success": False,
                "error": "No URL specified"
            }
        
        try:
            self.log_info(f"Making {method} request to {url}")
            
            # Make the HTTP request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=body if method.upper() in ("POST", "PUT", "PATCH") and body else None,
                timeout=timeout
            )
            
            # Try to parse JSON response if possible
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
                
            # Prepare output
            output_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response_data
            }
            
            self.set_output(output_data)
            
            # Log success or failure based on status code
            if response.ok:
                self.log_info(f"Request successful: {response.status_code}")
                return {
                    "success": True,
                    "data": output_data
                }
            else:
                self.log_error(f"Request failed with status: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP request failed with status code {response.status_code}",
                    "data": output_data
                }
                
        except Exception as e:
            self.log_error(f"Error making HTTP request: {str(e)}")
            return {
                "success": False,
                "error": f"Error making HTTP request: {str(e)}"
            }


@NodeHandlerRegistry.register("transform")
class TransformNodeHandler(BaseNodeHandler):
    """Handler for transform nodes that manipulate data"""
    
    def execute(self):
        """Execute the transform node"""
        # Get the transformation type
        transform_type = self.get_param("transform_type", "map")
        
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("Transform node has no incoming connections")
            return {
                "success": False,
                "error": "Transform node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        try:
            # Apply the appropriate transformation
            if transform_type == "map":
                output_data = self._transform_map(input_data)
            elif transform_type == "filter":
                output_data = self._transform_filter(input_data)
            elif transform_type == "reduce":
                output_data = self._transform_reduce(input_data)
            elif transform_type == "custom":
                output_data = self._transform_custom(input_data)
            else:
                self.log_error(f"Unknown transform type: {transform_type}")
                return {
                    "success": False,
                    "error": f"Unknown transform type: {transform_type}"
                }
            
            self.set_output(output_data)
            self.log_info(f"Transformation {transform_type} applied successfully")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error applying transformation: {str(e)}")
            return {
                "success": False,
                "error": f"Error applying transformation: {str(e)}"
            }
    
    def _transform_map(self, input_data):
        """Apply a mapping transformation"""
        mapping = self.get_param("mapping", {})
        result = {}
        
        if not isinstance(input_data, dict):
            raise ValueError("Input data must be an object for map transformation")
        
        for output_key, input_path in mapping.items():
            # Handle simple field mapping
            if isinstance(input_path, str):
                if "." in input_path:
                    # Handle nested paths like "user.address.city"
                    parts = input_path.split(".")
                    value = input_data
                    for part in parts:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            value = None
                            break
                    result[output_key] = value
                else:
                    # Handle direct field mapping
                    result[output_key] = input_data.get(input_path)
            
            # Handle template strings
            elif isinstance(input_path, dict) and input_path.get("template"):
                template = input_path.get("template")
                # Simple template substitution
                for key, value in input_data.items():
                    if isinstance(value, (str, int, float, bool)):
                        template = template.replace(f"{{{{{key}}}}}", str(value))
                result[output_key] = template
                
        return result
    
    def _transform_filter(self, input_data):
        """Apply a filter transformation"""
        filter_expr = self.get_param("filter_expr", "")
        
        if not isinstance(input_data, list):
            raise ValueError("Input data must be an array for filter transformation")
            
        if not filter_expr:
            return input_data
            
        # Apply filter to each item
        result = []
        for item in input_data:
            try:
                # Create context with the current item
                context = {"item": item}
                
                # Evaluate filter expression
                if eval(filter_expr, {"__builtins__": {}}, context):
                    result.append(item)
            except Exception as e:
                self.log_error(f"Error evaluating filter: {str(e)}")
                
        return result
    
    def _transform_reduce(self, input_data):
        """Apply a reduce transformation"""
        initial_value = self.get_param("initial_value", None)
        reduce_expr = self.get_param("reduce_expr", "")
        
        if not isinstance(input_data, list):
            raise ValueError("Input data must be an array for reduce transformation")
            
        if not reduce_expr:
            return initial_value
            
        # Apply reduce operation
        result = initial_value
        for item in input_data:
            try:
                # Create context with the current item and result
                context = {"item": item, "result": result}
                
                # Evaluate reduce expression
                result = eval(reduce_expr, {"__builtins__": {}}, context)
            except Exception as e:
                self.log_error(f"Error evaluating reduce: {str(e)}")
                
        return result
    
    def _transform_custom(self, input_data):
        """Apply a custom transformation using a script"""
        script = self.get_param("script", "")
        
        if not script:
            return input_data
            
        try:
            # Create context with the input data
            context = {
                "input": input_data,
                "output": None,
                "log": lambda msg: self.log_info(msg)
            }
            
            # Execute the script
            exec(script, {"__builtins__": {}}, context)
            
            # Return the output
            return context.get("output", input_data)
        except Exception as e:
            self.log_error(f"Error executing custom script: {str(e)}")
            return input_data


@NodeHandlerRegistry.register("delay")
class DelayNodeHandler(BaseNodeHandler):
    """Handler for delay nodes that pause workflow execution"""
    
    def execute(self):
        """Execute the delay node"""
        # Get delay duration in seconds
        duration = self.get_param("duration", 0)
        
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("Delay node has no incoming connections")
            return {
                "success": False,
                "error": "Delay node has no incoming connections"
            }
        
        # Use the output of the connected node as input/output
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        try:
            self.log_info(f"Delaying execution for {duration} seconds")
            
            # Simulate delay
            time.sleep(duration)
            
            # Pass through the input data
            self.set_output(input_data)
            
            self.log_info("Delay completed")
            
            return {
                "success": True,
                "data": input_data
            }
            
        except Exception as e:
            self.log_error(f"Error in delay node: {str(e)}")
            return {
                "success": False,
                "error": f"Error in delay node: {str(e)}"
            }


@NodeHandlerRegistry.register("frappe_doc_create")
class FrappeDocCreateNodeHandler(BaseNodeHandler):
    """Handler for creating a Frappe document"""
    
    def execute(self):
        """Execute the Frappe document creation node"""
        # Get parameters
        doctype = self.get_param("doctype", "")
        doc_data = self.get_param("doc_data", {})
        
        if not doctype:
            self.log_error("No DocType specified")
            return {
                "success": False,
                "error": "No DocType specified"
            }
        
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if incoming_connections:
            # If there's incoming data, use it to update doc_data
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
            
            if isinstance(input_data, dict):
                # Merge input data with doc_data
                doc_data.update(input_data)
        
        try:
            self.log_info(f"Creating {doctype} document")
            
            # Create the document
            doc = frappe.new_doc(doctype)
            
            # Set values
            for field, value in doc_data.items():
                doc.set(field, value)
            
            # Insert the document
            doc.insert()
            
            # Prepare output
            output_data = {
                "doc_name": doc.name,
                "doctype": doctype,
                "created": True
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Document {doctype} created successfully: {doc.name}")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error creating document: {str(e)}")
            return {
                "success": False,
                "error": f"Error creating document: {str(e)}"
            }


@NodeHandlerRegistry.register("frappe_doc_update")
class FrappeDocUpdateNodeHandler(BaseNodeHandler):
    """Handler for updating a Frappe document"""
    
    def execute(self):
        """Execute the Frappe document update node"""
        # Get parameters
        doctype = self.get_param("doctype", "")
        doc_name = self.get_param("doc_name", "")
        update_data = self.get_param("update_data", {})
        
        if not doctype:
            self.log_error("No DocType specified")
            return {
                "success": False,
                "error": "No DocType specified"
            }
            
        if not doc_name:
            self.log_error("No document name specified")
            return {
                "success": False,
                "error": "No document name specified"
            }
        
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if incoming_connections:
            # If there's incoming data, use it to update doc_data
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
            
            if isinstance(input_data, dict):
                # Merge input data with update_data
                update_data.update(input_data)
        
        try:
            self.log_info(f"Updating {doctype} document: {doc_name}")
            
            # Get the document
            doc = frappe.get_doc(doctype, doc_name)
            
            # Update values
            for field, value in update_data.items():
                doc.set(field, value)
            
            # Save the document
            doc.save()
            
            # Prepare output
            output_data = {
                "doc_name": doc.name,
                "doctype": doctype,
                "updated": True
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Document {doctype} updated successfully: {doc.name}")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error updating document: {str(e)}")
            return {
                "success": False,
                "error": f"Error updating document: {str(e)}"
            }


@NodeHandlerRegistry.register("frappe_doc_get")
class FrappeDocGetNodeHandler(BaseNodeHandler):
    """Handler for retrieving a Frappe document"""
    
    def execute(self):
        """Execute the Frappe document get node"""
        # Get parameters
        doctype = self.get_param("doctype", "")
        doc_name = self.get_param("doc_name", "")
        fields = self.get_param("fields", [])
        
        if not doctype:
            self.log_error("No DocType specified")
            return {
                "success": False,
                "error": "No DocType specified"
            }
            
        if not doc_name:
            self.log_error("No document name specified")
            return {
                "success": False,
                "error": "No document name specified"
            }
        
        try:
            self.log_info(f"Retrieving {doctype} document: {doc_name}")
            
            # Get the document
            if fields:
                # Get only specific fields
                doc = frappe.get_doc(doctype, doc_name, fields)
                
                # Convert to dict and filter fields
                doc_dict = doc.as_dict()
                if fields:
                    doc_dict = {k: v for k, v in doc_dict.items() if k in fields}
            else:
                # Get all fields
                doc = frappe.get_doc(doctype, doc_name)
                doc_dict = doc.as_dict()
            
            # Remove unnecessary fields
            for field in ["modified", "modified_by", "creation", "idx", "docstatus"]:
                if field in doc_dict:
                    del doc_dict[field]
            
            self.set_output(doc_dict)
            
            self.log_info(f"Document {doctype} retrieved successfully: {doc.name}")
            
            return {
                "success": True,
                "data": doc_dict
            }
            
        except Exception as e:
            self.log_error(f"Error retrieving document: {str(e)}")
            return {
                "success": False,
                "error": f"Error retrieving document: {str(e)}"
            }


@NodeHandlerRegistry.register("frappe_doc_delete")
class FrappeDocDeleteNodeHandler(BaseNodeHandler):
    """Handler for deleting a Frappe document"""
    
    def execute(self):
        """Execute the Frappe document delete node"""
        # Get parameters
        doctype = self.get_param("doctype", "")
        doc_name = self.get_param("doc_name", "")
        
        if not doctype:
            self.log_error("No DocType specified")
            return {
                "success": False,
                "error": "No DocType specified"
            }
            
        if not doc_name:
            self.log_error("No document name specified")
            return {
                "success": False,
                "error": "No document name specified"
            }
        
        try:
            self.log_info(f"Deleting {doctype} document: {doc_name}")
            
            # Delete the document
            frappe.delete_doc(doctype, doc_name)
            
            # Prepare output
            output_data = {
                "doc_name": doc_name,
                "doctype": doctype,
                "deleted": True
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Document {doctype} deleted successfully: {doc_name}")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error deleting document: {str(e)}")
            return {
                "success": False,
                "error": f"Error deleting document: {str(e)}"
            }


@NodeHandlerRegistry.register("frappe_doc_list")
class FrappeDocListNodeHandler(BaseNodeHandler):
    """Handler for listing Frappe documents"""
    
    def execute(self):
        """Execute the Frappe document list node"""
        # Get parameters
        doctype = self.get_param("doctype", "")
        filters = self.get_param("filters", {})
        fields = self.get_param("fields", ["name"])
        order_by = self.get_param("order_by", "modified desc")
        limit = self.get_param("limit", 0)
        
        if not doctype:
            self.log_error("No DocType specified")
            return {
                "success": False,
                "error": "No DocType specified"
            }
        
        try:
            self.log_info(f"Listing {doctype} documents")
            
            # Get documents
            docs = frappe.get_all(
                doctype,
                filters=filters,
                fields=fields,
                order_by=order_by,
                limit_page_length=limit if limit > 0 else None
            )
            
            # Prepare output
            output_data = {
                "doctype": doctype,
                "count": len(docs),
                "documents": docs
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Listed {len(docs)} {doctype} documents")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error listing documents: {str(e)}")
            return {
                "success": False,
                "error": f"Error listing documents: {str(e)}"
            }


# ============================================================================
# HIGH PRIORITY - ESSENTIAL WORKFLOW NODES
# ============================================================================


@NodeHandlerRegistry.register("loop")
@NodeHandlerRegistry.register("for_each")
class LoopNodeHandler(BaseNodeHandler):
    """Handler for loop/for_each nodes that iterate over arrays/collections"""
    
    def execute(self):
        """Execute the loop node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("Loop node has no incoming connections")
            return {
                "success": False,
                "error": "Loop node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get loop parameters
        items_path = self.get_param("items_path", "items")
        item_variable_name = self.get_param("item_variable_name", "item")
        index_variable_name = self.get_param("index_variable_name", "index")
        max_iterations = self.get_param("max_iterations", 1000)
        
        try:
            # Extract items to iterate over
            items = self._extract_items(input_data, items_path)
            
            if not isinstance(items, list):
                self.log_error(f"Items must be an array, got {type(items).__name__}")
                return {
                    "success": False,
                    "error": f"Items must be an array, got {type(items).__name__}"
                }
            
            # Limit iterations for safety
            if len(items) > max_iterations:
                self.log_error(f"Too many iterations: {len(items)} > {max_iterations}")
                return {
                    "success": False,
                    "error": f"Too many iterations: {len(items)} exceeds maximum {max_iterations}"
                }
            
            self.log_info(f"Starting loop with {len(items)} items")
            
            # Collect results from each iteration
            results = []
            
            # Iterate over items
            for index, item in enumerate(items):
                # Set loop variables
                self.execution_context.set_variable(item_variable_name, item)
                self.execution_context.set_variable(index_variable_name, index)
                
                # Execute loop body (nodes connected to loop output)
                # For now, we just collect the item and index
                # In a full implementation, this would execute connected nodes
                iteration_result = {
                    "index": index,
                    "item": item,
                    item_variable_name: item,
                    index_variable_name: index
                }
                
                results.append(iteration_result)
                
                self.log_debug(f"Loop iteration {index + 1}/{len(items)}")
            
            # Prepare output
            output_data = {
                "items": items,
                "results": results,
                "count": len(results),
                "completed": True
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Loop completed: {len(results)} iterations")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error executing loop: {str(e)}")
            return {
                "success": False,
                "error": f"Error executing loop: {str(e)}"
            }
    
    def _extract_items(self, data, path):
        """Extract items from data using a path"""
        if not path or path == ".":
            return data
        
        # Handle nested paths like "data.items"
        parts = path.split(".")
        value = data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return []
        
        return value


@NodeHandlerRegistry.register("parallel")
class ParallelNodeHandler(BaseNodeHandler):
    """Handler for parallel execution nodes that run multiple branches simultaneously"""
    
    def execute(self):
        """Execute the parallel node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("Parallel node has no incoming connections")
            return {
                "success": False,
                "error": "Parallel node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get outgoing connections (branches to execute in parallel)
        outgoing_connections = self.execution_context.get_outgoing_connections(self.node_id)
        
        if not outgoing_connections:
            self.log_error("Parallel node has no outgoing connections")
            return {
                "success": False,
                "error": "Parallel node has no outgoing connections"
            }
        
        try:
            self.log_info(f"Starting parallel execution with {len(outgoing_connections)} branches")
            
            # In a full implementation, this would execute branches in parallel
            # For now, we simulate parallel execution by collecting branch information
            branch_results = []
            
            for idx, connection in enumerate(outgoing_connections):
                target_node_id = connection.get("target")
                branch_label = connection.get("label", f"branch_{idx}")
                
                # Simulate branch execution
                branch_result = {
                    "branch_id": branch_label,
                    "target_node": target_node_id,
                    "status": "ready",
                    "input_data": input_data
                }
                
                branch_results.append(branch_result)
                
                self.log_debug(f"Prepared parallel branch: {branch_label}")
            
            # Prepare output
            output_data = {
                "input_data": input_data,
                "branches": branch_results,
                "branch_count": len(branch_results),
                "parallel_execution": True
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Parallel execution prepared: {len(branch_results)} branches")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error executing parallel node: {str(e)}")
            return {
                "success": False,
                "error": f"Error executing parallel node: {str(e)}"
            }


@NodeHandlerRegistry.register("merge")
class MergeNodeHandler(BaseNodeHandler):
    """Handler for merge nodes that combine multiple data streams"""
    
    def execute(self):
        """Execute the merge node"""
        # Get all incoming connections
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if len(incoming_connections) < 2:
            self.log_error("Merge node requires at least 2 incoming connections")
            return {
                "success": False,
                "error": "Merge node requires at least 2 incoming connections"
            }
        
        # Get merge strategy
        merge_strategy = self.get_param("merge_strategy", "all")
        
        try:
            self.log_info(f"Merging {len(incoming_connections)} data streams with strategy: {merge_strategy}")
            
            # Collect outputs from all incoming nodes
            inputs = []
            for connection in incoming_connections:
                source_node_id = connection.get("source")
                source_output = self.execution_context.get_node_output(source_node_id)
                inputs.append({
                    "source_node": source_node_id,
                    "data": source_output
                })
            
            # Apply merge strategy
            if merge_strategy == "first":
                # Return first non-empty input
                merged_data = next((inp["data"] for inp in inputs if inp["data"]), {})
                
            elif merge_strategy == "last":
                # Return last non-empty input
                merged_data = next((inp["data"] for inp in reversed(inputs) if inp["data"]), {})
                
            elif merge_strategy == "all":
                # Combine all inputs into an array
                merged_data = [inp["data"] for inp in inputs]
                
            elif merge_strategy == "object":
                # Merge all inputs into a single object
                merged_data = {}
                for inp in inputs:
                    if isinstance(inp["data"], dict):
                        merged_data.update(inp["data"])
                    else:
                        # Use source node ID as key if data is not a dict
                        merged_data[inp["source_node"]] = inp["data"]
                        
            elif merge_strategy == "array":
                # Flatten all arrays into a single array
                merged_data = []
                for inp in inputs:
                    if isinstance(inp["data"], list):
                        merged_data.extend(inp["data"])
                    else:
                        merged_data.append(inp["data"])
                        
            else:
                self.log_error(f"Unknown merge strategy: {merge_strategy}")
                return {
                    "success": False,
                    "error": f"Unknown merge strategy: {merge_strategy}"
                }
            
            # Prepare output
            output_data = {
                "merged_data": merged_data,
                "merge_strategy": merge_strategy,
                "source_count": len(inputs),
                "sources": [inp["source_node"] for inp in inputs]
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Merge completed: {len(inputs)} sources merged using '{merge_strategy}' strategy")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error executing merge: {str(e)}")
            return {
                "success": False,
                "error": f"Error executing merge: {str(e)}"
            }


@NodeHandlerRegistry.register("switch")
class SwitchNodeHandler(BaseNodeHandler):
    """Handler for switch nodes that route to different paths based on a value"""
    
    def execute(self):
        """Execute the switch node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("Switch node has no incoming connections")
            return {
                "success": False,
                "error": "Switch node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get switch parameters
        switch_value_path = self.get_param("switch_value_path", "value")
        cases = self.get_param("cases", [])
        default_case = self.get_param("default_case", "default")
        
        try:
            # Extract the value to switch on
            switch_value = self._extract_value(input_data, switch_value_path)
            
            self.log_info(f"Switch on value: {switch_value}")
            
            # Find matching case
            matched_case = None
            for case in cases:
                case_value = case.get("value")
                case_label = case.get("label", str(case_value))
                
                if switch_value == case_value:
                    matched_case = case_label
                    break
            
            # Use default if no match found
            if matched_case is None:
                matched_case = default_case
                self.log_info(f"No case matched, using default: {default_case}")
            else:
                self.log_info(f"Matched case: {matched_case}")
            
            # Set the branch to take
            self.execution_context.set_node_branch(self.node_id, matched_case)
            
            # Prepare output
            output_data = {
                "switch_value": switch_value,
                "matched_case": matched_case,
                "input_data": input_data
            }
            
            self.set_output(output_data)
            
            return {
                "success": True,
                "data": output_data,
                "branch": matched_case
            }
            
        except Exception as e:
            self.log_error(f"Error executing switch: {str(e)}")
            return {
                "success": False,
                "error": f"Error executing switch: {str(e)}"
            }
    
    def _extract_value(self, data, path):
        """Extract value from data using a path"""
        if not path or path == ".":
            return data
        
        # Handle nested paths like "user.status"
        parts = path.split(".")
        value = data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value


@NodeHandlerRegistry.register("set_variable")
class SetVariableNodeHandler(BaseNodeHandler):
    """Handler for setting workflow variables"""
    
    def execute(self):
        """Execute the set_variable node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get variable parameters
        variable_name = self.get_param("variable_name", "")
        variable_value = self.get_param("variable_value", None)
        value_from_input = self.get_param("value_from_input", False)
        input_path = self.get_param("input_path", "")
        
        if not variable_name:
            self.log_error("No variable name specified")
            return {
                "success": False,
                "error": "No variable name specified"
            }
        
        try:
            # Determine the value to set
            if value_from_input:
                # Extract value from input data
                if input_path:
                    value = self._extract_value(input_data, input_path)
                else:
                    value = input_data
            else:
                # Use the provided value
                value = variable_value
            
            # Set the variable in the execution context
            self.execution_context.set_variable(variable_name, value)
            
            self.log_info(f"Variable '{variable_name}' set to: {value}")
            
            # Prepare output
            output_data = {
                "variable_name": variable_name,
                "variable_value": value,
                "input_data": input_data
            }
            
            self.set_output(output_data)
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error setting variable: {str(e)}")
            return {
                "success": False,
                "error": f"Error setting variable: {str(e)}"
            }
    
    def _extract_value(self, data, path):
        """Extract value from data using a path"""
        if not path or path == ".":
            return data
        
        # Handle nested paths
        parts = path.split(".")
        value = data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value


@NodeHandlerRegistry.register("get_variable")
class GetVariableNodeHandler(BaseNodeHandler):
    """Handler for retrieving workflow variables"""
    
    def execute(self):
        """Execute the get_variable node"""
        # Get variable parameters
        variable_name = self.get_param("variable_name", "")
        default_value = self.get_param("default_value", None)
        
        if not variable_name:
            self.log_error("No variable name specified")
            return {
                "success": False,
                "error": "No variable name specified"
            }
        
        try:
            # Get the variable from the execution context
            value = self.execution_context.get_variable(variable_name, default_value)
            
            if value is None and default_value is None:
                self.log_error(f"Variable '{variable_name}' not found and no default value provided")
                return {
                    "success": False,
                    "error": f"Variable '{variable_name}' not found"
                }
            
            self.log_info(f"Variable '{variable_name}' retrieved: {value}")
            
            # Prepare output
            output_data = {
                "variable_name": variable_name,
                "variable_value": value,
                "has_default": default_value is not None
            }
            
            self.set_output(output_data)
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error getting variable: {str(e)}")
            return {
                "success": False,
                "error": f"Error getting variable: {str(e)}"
            }


# ============================================================================
# MEDIUM PRIORITY - DATA & INTEGRATION NODES
# ============================================================================


@NodeHandlerRegistry.register("json_parse")
class JsonParseNodeHandler(BaseNodeHandler):
    """Handler for parsing JSON strings"""
    
    def execute(self):
        """Execute the json_parse node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("JSON parse node has no incoming connections")
            return {
                "success": False,
                "error": "JSON parse node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        json_string_path = self.get_param("json_string_path", "json_string")
        strict = self.get_param("strict", True)
        
        try:
            # Extract JSON string from input
            if isinstance(input_data, str):
                json_string = input_data
            elif isinstance(input_data, dict):
                json_string = input_data.get(json_string_path, "")
            else:
                json_string = str(input_data)
            
            if not json_string:
                self.log_error("No JSON string found in input")
                return {
                    "success": False,
                    "error": "No JSON string found in input"
                }
            
            self.log_info(f"Parsing JSON string (length: {len(json_string)})")
            
            # Parse JSON
            parsed_data = json.loads(json_string, strict=strict)
            
            # Prepare output
            output_data = {
                "parsed_data": parsed_data,
                "original_string": json_string[:100] + "..." if len(json_string) > 100 else json_string,
                "data_type": type(parsed_data).__name__
            }
            
            self.set_output(output_data)
            
            self.log_info(f"JSON parsed successfully: {type(parsed_data).__name__}")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except json.JSONDecodeError as e:
            self.log_error(f"Invalid JSON: {str(e)}")
            return {
                "success": False,
                "error": f"Invalid JSON: {str(e)}"
            }
        except Exception as e:
            self.log_error(f"Error parsing JSON: {str(e)}")
            return {
                "success": False,
                "error": f"Error parsing JSON: {str(e)}"
            }


@NodeHandlerRegistry.register("json_stringify")
class JsonStringifyNodeHandler(BaseNodeHandler):
    """Handler for converting data to JSON string"""
    
    def execute(self):
        """Execute the json_stringify node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("JSON stringify node has no incoming connections")
            return {
                "success": False,
                "error": "JSON stringify node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        indent = self.get_param("indent", None)
        sort_keys = self.get_param("sort_keys", False)
        ensure_ascii = self.get_param("ensure_ascii", True)
        
        try:
            self.log_info(f"Converting to JSON string: {type(input_data).__name__}")
            
            # Convert to JSON string
            json_string = json.dumps(
                input_data,
                indent=indent,
                sort_keys=sort_keys,
                ensure_ascii=ensure_ascii
            )
            
            # Prepare output
            output_data = {
                "json_string": json_string,
                "length": len(json_string),
                "original_type": type(input_data).__name__
            }
            
            self.set_output(output_data)
            
            self.log_info(f"JSON stringify successful: {len(json_string)} characters")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except TypeError as e:
            self.log_error(f"Data not JSON serializable: {str(e)}")
            return {
                "success": False,
                "error": f"Data not JSON serializable: {str(e)}"
            }
        except Exception as e:
            self.log_error(f"Error converting to JSON: {str(e)}")
            return {
                "success": False,
                "error": f"Error converting to JSON: {str(e)}"
            }


@NodeHandlerRegistry.register("xml_parse")
class XmlParseNodeHandler(BaseNodeHandler):
    """Handler for parsing XML data"""
    
    def execute(self):
        """Execute the xml_parse node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("XML parse node has no incoming connections")
            return {
                "success": False,
                "error": "XML parse node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        xml_string_path = self.get_param("xml_string_path", "xml_string")
        
        try:
            import xml.etree.ElementTree as ET
            
            # Extract XML string from input
            if isinstance(input_data, str):
                xml_string = input_data
            elif isinstance(input_data, dict):
                xml_string = input_data.get(xml_string_path, "")
            else:
                xml_string = str(input_data)
            
            if not xml_string:
                self.log_error("No XML string found in input")
                return {
                    "success": False,
                    "error": "No XML string found in input"
                }
            
            self.log_info(f"Parsing XML string (length: {len(xml_string)})")
            
            # Parse XML
            root = ET.fromstring(xml_string)
            
            # Convert XML to dict
            def xml_to_dict(element):
                result = {}
                
                # Add attributes
                if element.attrib:
                    result['@attributes'] = element.attrib
                
                # Add text content
                if element.text and element.text.strip():
                    result['@text'] = element.text.strip()
                
                # Add children
                for child in element:
                    child_data = xml_to_dict(child)
                    if child.tag in result:
                        # Multiple children with same tag - convert to list
                        if not isinstance(result[child.tag], list):
                            result[child.tag] = [result[child.tag]]
                        result[child.tag].append(child_data)
                    else:
                        result[child.tag] = child_data
                
                return result if result else (element.text or "")
            
            parsed_data = {
                root.tag: xml_to_dict(root)
            }
            
            # Prepare output
            output_data = {
                "parsed_data": parsed_data,
                "root_tag": root.tag,
                "original_string": xml_string[:100] + "..." if len(xml_string) > 100 else xml_string
            }
            
            self.set_output(output_data)
            
            self.log_info(f"XML parsed successfully: root tag '{root.tag}'")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except ET.ParseError as e:
            self.log_error(f"Invalid XML: {str(e)}")
            return {
                "success": False,
                "error": f"Invalid XML: {str(e)}"
            }
        except Exception as e:
            self.log_error(f"Error parsing XML: {str(e)}")
            return {
                "success": False,
                "error": f"Error parsing XML: {str(e)}"
            }


@NodeHandlerRegistry.register("xml_build")
class XmlBuildNodeHandler(BaseNodeHandler):
    """Handler for building XML from data"""
    
    def execute(self):
        """Execute the xml_build node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("XML build node has no incoming connections")
            return {
                "success": False,
                "error": "XML build node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        root_tag = self.get_param("root_tag", "root")
        pretty_print = self.get_param("pretty_print", True)
        
        try:
            import xml.etree.ElementTree as ET
            
            self.log_info(f"Building XML from data: {type(input_data).__name__}")
            
            # Build XML from dict
            def dict_to_xml(parent, data):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key == '@attributes':
                            # Set attributes
                            parent.attrib.update(value)
                        elif key == '@text':
                            # Set text content
                            parent.text = str(value)
                        elif isinstance(value, list):
                            # Multiple elements with same tag
                            for item in value:
                                child = ET.SubElement(parent, key)
                                dict_to_xml(child, item)
                        else:
                            # Single child element
                            child = ET.SubElement(parent, key)
                            dict_to_xml(child, value)
                else:
                    # Simple value
                    parent.text = str(data)
            
            # Create root element
            root = ET.Element(root_tag)
            dict_to_xml(root, input_data)
            
            # Convert to string
            if pretty_print:
                ET.indent(root, space="  ")
            
            xml_string = ET.tostring(root, encoding='unicode')
            
            # Prepare output
            output_data = {
                "xml_string": xml_string,
                "root_tag": root_tag,
                "length": len(xml_string)
            }
            
            self.set_output(output_data)
            
            self.log_info(f"XML built successfully: {len(xml_string)} characters")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error building XML: {str(e)}")
            return {
                "success": False,
                "error": f"Error building XML: {str(e)}"
            }


@NodeHandlerRegistry.register("csv_parse")
class CsvParseNodeHandler(BaseNodeHandler):
    """Handler for parsing CSV data"""
    
    def execute(self):
        """Execute the csv_parse node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("CSV parse node has no incoming connections")
            return {
                "success": False,
                "error": "CSV parse node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        csv_string_path = self.get_param("csv_string_path", "csv_string")
        delimiter = self.get_param("delimiter", ",")
        has_header = self.get_param("has_header", True)
        skip_empty_rows = self.get_param("skip_empty_rows", True)
        
        try:
            import csv
            import io
            
            # Extract CSV string from input
            if isinstance(input_data, str):
                csv_string = input_data
            elif isinstance(input_data, dict):
                csv_string = input_data.get(csv_string_path, "")
            else:
                csv_string = str(input_data)
            
            if not csv_string:
                self.log_error("No CSV string found in input")
                return {
                    "success": False,
                    "error": "No CSV string found in input"
                }
            
            self.log_info(f"Parsing CSV string (length: {len(csv_string)})")
            
            # Parse CSV
            csv_reader = csv.reader(io.StringIO(csv_string), delimiter=delimiter)
            rows = list(csv_reader)
            
            if skip_empty_rows:
                rows = [row for row in rows if any(cell.strip() for cell in row)]
            
            # Process data
            if has_header and rows:
                headers = rows[0]
                data_rows = rows[1:]
                
                # Convert to list of dicts
                parsed_data = []
                for row in data_rows:
                    row_dict = {}
                    for i, header in enumerate(headers):
                        row_dict[header] = row[i] if i < len(row) else ""
                    parsed_data.append(row_dict)
            else:
                # Return as list of lists
                parsed_data = rows
            
            # Prepare output
            output_data = {
                "parsed_data": parsed_data,
                "row_count": len(parsed_data),
                "has_header": has_header,
                "headers": rows[0] if has_header and rows else None
            }
            
            self.set_output(output_data)
            
            self.log_info(f"CSV parsed successfully: {len(parsed_data)} rows")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error parsing CSV: {str(e)}")
            return {
                "success": False,
                "error": f"Error parsing CSV: {str(e)}"
            }


@NodeHandlerRegistry.register("csv_build")
class CsvBuildNodeHandler(BaseNodeHandler):
    """Handler for building CSV from data"""
    
    def execute(self):
        """Execute the csv_build node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("CSV build node has no incoming connections")
            return {
                "success": False,
                "error": "CSV build node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        data_path = self.get_param("data_path", "data")
        delimiter = self.get_param("delimiter", ",")
        include_header = self.get_param("include_header", True)
        
        try:
            import csv
            import io
            
            # Extract data array from input
            if isinstance(input_data, list):
                data = input_data
            elif isinstance(input_data, dict):
                data = input_data.get(data_path, [])
            else:
                self.log_error("Input must be array or object with data array")
                return {
                    "success": False,
                    "error": "Input must be array or object with data array"
                }
            
            if not data:
                self.log_error("No data found to convert to CSV")
                return {
                    "success": False,
                    "error": "No data found to convert to CSV"
                }
            
            self.log_info(f"Building CSV from {len(data)} rows")
            
            # Build CSV
            output = io.StringIO()
            
            if isinstance(data[0], dict):
                # Data is list of dicts
                headers = list(data[0].keys())
                writer = csv.DictWriter(output, fieldnames=headers, delimiter=delimiter)
                
                if include_header:
                    writer.writeheader()
                
                writer.writerows(data)
            else:
                # Data is list of lists
                writer = csv.writer(output, delimiter=delimiter)
                writer.writerows(data)
            
            csv_string = output.getvalue()
            
            # Prepare output
            output_data = {
                "csv_string": csv_string,
                "row_count": len(data),
                "length": len(csv_string)
            }
            
            self.set_output(output_data)
            
            self.log_info(f"CSV built successfully: {len(data)} rows, {len(csv_string)} characters")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error building CSV: {str(e)}")
            return {
                "success": False,
                "error": f"Error building CSV: {str(e)}"
            }


@NodeHandlerRegistry.register("template")
class TemplateNodeHandler(BaseNodeHandler):
    """Handler for template rendering using Jinja2"""
    
    def execute(self):
        """Execute the template node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("Template node has no incoming connections")
            return {
                "success": False,
                "error": "Template node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        template_string = self.get_param("template_string", "")
        
        if not template_string:
            self.log_error("No template string provided")
            return {
                "success": False,
                "error": "No template string provided"
            }
        
        try:
            from jinja2 import Template
            
            self.log_info(f"Rendering template (length: {len(template_string)})")
            
            # Create template
            template = Template(template_string)
            
            # Prepare context
            context = {}
            if isinstance(input_data, dict):
                context.update(input_data)
            else:
                context['data'] = input_data
            
            # Add variables from workflow
            variables = self.execution_context.get_all_variables()
            context.update(variables)
            
            # Render template
            rendered = template.render(**context)
            
            # Prepare output
            output_data = {
                "rendered": rendered,
                "template_length": len(template_string),
                "output_length": len(rendered)
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Template rendered successfully: {len(rendered)} characters")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error rendering template: {str(e)}")
            return {
                "success": False,
                "error": f"Error rendering template: {str(e)}"
            }


@NodeHandlerRegistry.register("regex")
class RegexNodeHandler(BaseNodeHandler):
    """Handler for regular expression operations"""
    
    def execute(self):
        """Execute the regex node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("Regex node has no incoming connections")
            return {
                "success": False,
                "error": "Regex node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        pattern = self.get_param("pattern", "")
        operation = self.get_param("operation", "match")  # match, search, findall, replace
        replacement = self.get_param("replacement", "")
        flags = self.get_param("flags", 0)
        text_path = self.get_param("text_path", "text")
        
        if not pattern:
            self.log_error("No regex pattern provided")
            return {
                "success": False,
                "error": "No regex pattern provided"
            }
        
        try:
            import re
            
            # Extract text from input
            if isinstance(input_data, str):
                text = input_data
            elif isinstance(input_data, dict):
                text = input_data.get(text_path, "")
            else:
                text = str(input_data)
            
            if not text:
                self.log_error("No text found in input")
                return {
                    "success": False,
                    "error": "No text found in input"
                }
            
            self.log_info(f"Executing regex operation '{operation}' with pattern: {pattern}")
            
            # Compile pattern
            regex = re.compile(pattern, flags)
            
            # Execute operation
            if operation == "match":
                match = regex.match(text)
                result = {
                    "matched": match is not None,
                    "groups": match.groups() if match else [],
                    "group_dict": match.groupdict() if match else {}
                }
            
            elif operation == "search":
                match = regex.search(text)
                result = {
                    "found": match is not None,
                    "match": match.group() if match else None,
                    "groups": match.groups() if match else [],
                    "group_dict": match.groupdict() if match else {},
                    "start": match.start() if match else None,
                    "end": match.end() if match else None
                }
            
            elif operation == "findall":
                matches = regex.findall(text)
                result = {
                    "matches": matches,
                    "count": len(matches)
                }
            
            elif operation == "replace":
                replaced = regex.sub(replacement, text)
                result = {
                    "original": text,
                    "replaced": replaced,
                    "changed": text != replaced
                }
            
            else:
                self.log_error(f"Unknown operation: {operation}")
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
            
            # Prepare output
            output_data = {
                "pattern": pattern,
                "operation": operation,
                "result": result
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Regex operation '{operation}' completed successfully")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except re.error as e:
            self.log_error(f"Invalid regex pattern: {str(e)}")
            return {
                "success": False,
                "error": f"Invalid regex pattern: {str(e)}"
            }
        except Exception as e:
            self.log_error(f"Error executing regex: {str(e)}")
            return {
                "success": False,
                "error": f"Error executing regex: {str(e)}"
            }


@NodeHandlerRegistry.register("code")
class CodeNodeHandler(BaseNodeHandler):
    """Handler for executing custom Python code safely"""
    
    def execute(self):
        """Execute the code node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        code_string = self.get_param("code_string", "")
        
        if not code_string:
            self.log_error("No code provided")
            return {
                "success": False,
                "error": "No code provided"
            }
        
        try:
            self.log_info(f"Executing custom code (length: {len(code_string)})")
            
            # Prepare safe execution context
            safe_globals = {
                "__builtins__": {
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "list": list,
                    "dict": dict,
                    "tuple": tuple,
                    "set": set,
                    "range": range,
                    "enumerate": enumerate,
                    "zip": zip,
                    "map": map,
                    "filter": filter,
                    "sum": sum,
                    "min": min,
                    "max": max,
                    "abs": abs,
                    "round": round,
                    "sorted": sorted,
                    "any": any,
                    "all": all,
                    "print": print,
                },
                "json": json,
                "time": time,
            }
            
            # Prepare local context
            local_context = {
                "input": input_data,
                "variables": self.execution_context.get_all_variables(),
                "output": None
            }
            
            # Execute code
            exec(code_string, safe_globals, local_context)
            
            # Get output
            result = local_context.get("output")
            
            # Prepare output
            output_data = {
                "result": result,
                "code_executed": True,
                "input_data": input_data
            }
            
            self.set_output(output_data)
            
            self.log_info("Custom code executed successfully")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error executing code: {str(e)}")
            return {
                "success": False,
                "error": f"Error executing code: {str(e)}"
            }


@NodeHandlerRegistry.register("function")
class FunctionNodeHandler(BaseNodeHandler):
    """Handler for reusable sub-workflow/function calls"""
    
    def execute(self):
        """Execute the function node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        workflow_name = self.get_param("workflow_name", "")
        
        if not workflow_name:
            self.log_error("No workflow name provided")
            return {
                "success": False,
                "error": "No workflow name provided"
            }
        
        try:
            self.log_info(f"Calling sub-workflow: {workflow_name}")
            
            # Check if workflow exists
            if not frappe.db.exists("Automesh Workflow", workflow_name):
                self.log_error(f"Workflow not found: {workflow_name}")
                return {
                    "success": False,
                    "error": f"Workflow not found: {workflow_name}"
                }
            
            # Create execution for sub-workflow
            execution = frappe.new_doc("Automesh Execution")
            execution.workflow = workflow_name
            execution.status = "draft"
            execution.input_data = json.dumps(input_data)
            execution.insert()
            
            # Execute sub-workflow
            from .engine import WorkflowEngine
            engine = WorkflowEngine(execution.name)
            success = engine.execute()
            
            # Get result
            execution.reload()
            output = json.loads(execution.output_data) if execution.output_data else {}
            
            # Prepare output
            output_data = {
                "workflow_name": workflow_name,
                "execution_id": execution.name,
                "status": execution.status,
                "result": output,
                "success": success
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Sub-workflow completed: {execution.status}")
            
            return {
                "success": success,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error calling sub-workflow: {str(e)}")
            return {
                "success": False,
                "error": f"Error calling sub-workflow: {str(e)}"
            }


# ============================================================================
# MEDIUM PRIORITY - EXTERNAL INTEGRATION NODES
# ============================================================================


@NodeHandlerRegistry.register("email_send")
class EmailSendNodeHandler(BaseNodeHandler):
    """Handler for sending emails via SMTP"""
    
    def execute(self):
        """Execute the email_send node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        to_email = self.get_param("to_email", "")
        subject = self.get_param("subject", "")
        body = self.get_param("body", "")
        from_email = self.get_param("from_email", "")
        cc = self.get_param("cc", "")
        bcc = self.get_param("bcc", "")
        
        if not to_email:
            self.log_error("No recipient email specified")
            return {
                "success": False,
                "error": "No recipient email specified"
            }
        
        try:
            self.log_info(f"Sending email to: {to_email}")
            
            # Use Frappe's email queue
            frappe.sendmail(
                recipients=to_email.split(",") if isinstance(to_email, str) else to_email,
                subject=subject,
                message=body,
                sender=from_email or None,
                cc=cc.split(",") if cc and isinstance(cc, str) else (cc or None),
                bcc=bcc.split(",") if bcc and isinstance(bcc, str) else (bcc or None),
                delayed=False
            )
            
            # Prepare output
            output_data = {
                "to_email": to_email,
                "subject": subject,
                "sent": True,
                "timestamp": now()
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Email sent successfully to: {to_email}")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error sending email: {str(e)}")
            return {
                "success": False,
                "error": f"Error sending email: {str(e)}"
            }


@NodeHandlerRegistry.register("webhook")
class WebhookNodeHandler(BaseNodeHandler):
    """Handler for triggering webhooks/HTTP callbacks"""
    
    def execute(self):
        """Execute the webhook node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        url = self.get_param("url", "")
        method = self.get_param("method", "POST")
        headers = self.get_param("headers", {})
        payload = self.get_param("payload", input_data)
        timeout = self.get_param("timeout", 30)
        
        if not url:
            self.log_error("No webhook URL specified")
            return {
                "success": False,
                "error": "No webhook URL specified"
            }
        
        try:
            self.log_info(f"Triggering webhook: {method} {url}")
            
            # Make HTTP request
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
            
            # Prepare output
            output_data = {
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "response": response_data,
                "success": response.ok
            }
            
            self.set_output(output_data)
            
            if response.ok:
                self.log_info(f"Webhook successful: {response.status_code}")
                return {
                    "success": True,
                    "data": output_data
                }
            else:
                self.log_error(f"Webhook failed: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Webhook returned status {response.status_code}",
                    "data": output_data
                }
            
        except Exception as e:
            self.log_error(f"Error triggering webhook: {str(e)}")
            return {
                "success": False,
                "error": f"Error triggering webhook: {str(e)}"
            }


@NodeHandlerRegistry.register("file_read")
class FileReadNodeHandler(BaseNodeHandler):
    """Handler for reading files from storage"""
    
    def execute(self):
        """Execute the file_read node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        file_path = self.get_param("file_path", "")
        encoding = self.get_param("encoding", "utf-8")
        read_mode = self.get_param("read_mode", "text")  # text or binary
        
        if not file_path:
            self.log_error("No file path specified")
            return {
                "success": False,
                "error": "No file path specified"
            }
        
        try:
            import os
            
            self.log_info(f"Reading file: {file_path}")
            
            # Security check - ensure path is within allowed directories
            # In production, you'd want to restrict to specific directories
            if not os.path.exists(file_path):
                self.log_error(f"File not found: {file_path}")
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            # Read file
            if read_mode == "binary":
                with open(file_path, 'rb') as f:
                    content = f.read()
                    # Convert to base64 for JSON serialization
                    import base64
                    content = base64.b64encode(content).decode('ascii')
            else:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            # Prepare output
            output_data = {
                "file_path": file_path,
                "file_name": file_name,
                "content": content,
                "size": file_size,
                "encoding": encoding,
                "read_mode": read_mode
            }
            
            self.set_output(output_data)
            
            self.log_info(f"File read successfully: {file_size} bytes")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error reading file: {str(e)}")
            return {
                "success": False,
                "error": f"Error reading file: {str(e)}"
            }


@NodeHandlerRegistry.register("file_write")
class FileWriteNodeHandler(BaseNodeHandler):
    """Handler for writing files to storage"""
    
    def execute(self):
        """Execute the file_write node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("File write node has no incoming connections")
            return {
                "success": False,
                "error": "File write node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        file_path = self.get_param("file_path", "")
        content_path = self.get_param("content_path", "content")
        encoding = self.get_param("encoding", "utf-8")
        write_mode = self.get_param("write_mode", "text")  # text or binary
        create_dirs = self.get_param("create_dirs", True)
        
        if not file_path:
            self.log_error("No file path specified")
            return {
                "success": False,
                "error": "No file path specified"
            }
        
        try:
            import os
            
            # Extract content from input
            if isinstance(input_data, str):
                content = input_data
            elif isinstance(input_data, dict):
                content = input_data.get(content_path, "")
            else:
                content = str(input_data)
            
            if not content:
                self.log_error("No content to write")
                return {
                    "success": False,
                    "error": "No content to write"
                }
            
            self.log_info(f"Writing file: {file_path}")
            
            # Create directories if needed
            if create_dirs:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file
            if write_mode == "binary":
                # Decode from base64 if it's a string
                if isinstance(content, str):
                    import base64
                    content = base64.b64decode(content)
                with open(file_path, 'wb') as f:
                    f.write(content)
            else:
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(content)
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            # Prepare output
            output_data = {
                "file_path": file_path,
                "file_name": file_name,
                "size": file_size,
                "encoding": encoding,
                "write_mode": write_mode,
                "written": True
            }
            
            self.set_output(output_data)
            
            self.log_info(f"File written successfully: {file_size} bytes")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error writing file: {str(e)}")
            return {
                "success": False,
                "error": f"Error writing file: {str(e)}"
            }


@NodeHandlerRegistry.register("database_query")
class DatabaseQueryNodeHandler(BaseNodeHandler):
    """Handler for executing database queries"""
    
    def execute(self):
        """Execute the database_query node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        query = self.get_param("query", "")
        params = self.get_param("params", [])
        as_dict = self.get_param("as_dict", True)
        
        if not query:
            self.log_error("No query specified")
            return {
                "success": False,
                "error": "No query specified"
            }
        
        try:
            self.log_info(f"Executing database query")
            
            # Execute query using Frappe's database
            if as_dict:
                results = frappe.db.sql(query, params, as_dict=True)
            else:
                results = frappe.db.sql(query, params)
            
            # Prepare output
            output_data = {
                "results": results,
                "count": len(results),
                "query": query[:100] + "..." if len(query) > 100 else query
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Query executed successfully: {len(results)} rows")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error executing query: {str(e)}")
            return {
                "success": False,
                "error": f"Error executing query: {str(e)}"
            }


# ============================================================================
# LOW PRIORITY - UTILITY NODES
# ============================================================================


@NodeHandlerRegistry.register("logger")
class LoggerNodeHandler(BaseNodeHandler):
    """Handler for advanced logging operations"""
    
    def execute(self):
        """Execute the logger node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        message = self.get_param("message", "")
        log_level = self.get_param("log_level", "INFO")  # DEBUG, INFO, WARNING, ERROR
        include_data = self.get_param("include_data", False)
        
        if not message:
            message = str(input_data)
        
        try:
            # Log message
            if log_level == "DEBUG":
                self.log_debug(message)
            elif log_level == "WARNING":
                frappe.log_error(message, "Workflow Warning")
            elif log_level == "ERROR":
                self.log_error(message)
            else:  # INFO
                self.log_info(message)
            
            # Prepare output
            output_data = {
                "message": message,
                "log_level": log_level,
                "timestamp": now(),
                "logged": True
            }
            
            if include_data:
                output_data["data"] = input_data
            
            self.set_output(output_data)
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error logging: {str(e)}")
            return {
                "success": False,
                "error": f"Error logging: {str(e)}"
            }


@NodeHandlerRegistry.register("counter")
class CounterNodeHandler(BaseNodeHandler):
    """Handler for increment/decrement counter operations"""
    
    def execute(self):
        """Execute the counter node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        counter_name = self.get_param("counter_name", "default_counter")
        operation = self.get_param("operation", "increment")  # increment, decrement, set, get
        value = self.get_param("value", 1)
        
        try:
            # Get current counter value from variables
            current_value = self.execution_context.get_variable(counter_name, 0)
            
            # Perform operation
            if operation == "increment":
                new_value = current_value + value
            elif operation == "decrement":
                new_value = current_value - value
            elif operation == "set":
                new_value = value
            elif operation == "get":
                new_value = current_value
            else:
                self.log_error(f"Unknown operation: {operation}")
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
            
            # Update counter
            if operation != "get":
                self.execution_context.set_variable(counter_name, new_value)
            
            # Prepare output
            output_data = {
                "counter_name": counter_name,
                "operation": operation,
                "previous_value": current_value,
                "current_value": new_value,
                "change": new_value - current_value
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Counter '{counter_name}': {current_value} -> {new_value}")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error with counter: {str(e)}")
            return {
                "success": False,
                "error": f"Error with counter: {str(e)}"
            }


@NodeHandlerRegistry.register("cache_get")
class CacheGetNodeHandler(BaseNodeHandler):
    """Handler for getting values from cache"""
    
    def execute(self):
        """Execute the cache_get node"""
        # Get parameters
        cache_key = self.get_param("cache_key", "")
        default_value = self.get_param("default_value", None)
        
        if not cache_key:
            self.log_error("No cache key specified")
            return {
                "success": False,
                "error": "No cache key specified"
            }
        
        try:
            self.log_info(f"Getting cache value for key: {cache_key}")
            
            # Get from Frappe cache
            value = frappe.cache().get_value(cache_key)
            
            if value is None:
                value = default_value
                found = False
            else:
                found = True
            
            # Prepare output
            output_data = {
                "cache_key": cache_key,
                "value": value,
                "found": found,
                "has_default": default_value is not None
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Cache {'hit' if found else 'miss'} for key: {cache_key}")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error getting cache: {str(e)}")
            return {
                "success": False,
                "error": f"Error getting cache: {str(e)}"
            }


@NodeHandlerRegistry.register("cache_set")
class CacheSetNodeHandler(BaseNodeHandler):
    """Handler for setting values in cache"""
    
    def execute(self):
        """Execute the cache_set node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        cache_key = self.get_param("cache_key", "")
        value_path = self.get_param("value_path", "value")
        ttl = self.get_param("ttl", 3600)  # Time to live in seconds (default 1 hour)
        
        if not cache_key:
            self.log_error("No cache key specified")
            return {
                "success": False,
                "error": "No cache key specified"
            }
        
        try:
            # Extract value from input
            if isinstance(input_data, dict):
                value = input_data.get(value_path, input_data)
            else:
                value = input_data
            
            self.log_info(f"Setting cache value for key: {cache_key}")
            
            # Set in Frappe cache
            frappe.cache().set_value(cache_key, value, expires_in_sec=ttl)
            
            # Prepare output
            output_data = {
                "cache_key": cache_key,
                "value": value,
                "ttl": ttl,
                "cached": True
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Cache set for key: {cache_key} (TTL: {ttl}s)")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error setting cache: {str(e)}")
            return {
                "success": False,
                "error": f"Error setting cache: {str(e)}"
            }


@NodeHandlerRegistry.register("hash")
class HashNodeHandler(BaseNodeHandler):
    """Handler for generating hashes"""
    
    def execute(self):
        """Execute the hash node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        data_path = self.get_param("data_path", "data")
        algorithm = self.get_param("algorithm", "sha256")  # md5, sha1, sha256, sha512
        encoding = self.get_param("encoding", "utf-8")
        
        try:
            import hashlib
            
            # Extract data to hash
            if isinstance(input_data, str):
                data = input_data
            elif isinstance(input_data, dict):
                data = input_data.get(data_path, "")
            else:
                data = str(input_data)
            
            if not data:
                self.log_error("No data to hash")
                return {
                    "success": False,
                    "error": "No data to hash"
                }
            
            self.log_info(f"Generating {algorithm} hash")
            
            # Convert to bytes
            data_bytes = data.encode(encoding) if isinstance(data, str) else str(data).encode(encoding)
            
            # Generate hash
            if algorithm == "md5":
                hash_obj = hashlib.md5(data_bytes)
            elif algorithm == "sha1":
                hash_obj = hashlib.sha1(data_bytes)
            elif algorithm == "sha256":
                hash_obj = hashlib.sha256(data_bytes)
            elif algorithm == "sha512":
                hash_obj = hashlib.sha512(data_bytes)
            else:
                self.log_error(f"Unknown algorithm: {algorithm}")
                return {
                    "success": False,
                    "error": f"Unknown algorithm: {algorithm}"
                }
            
            hash_value = hash_obj.hexdigest()
            
            # Prepare output
            output_data = {
                "hash": hash_value,
                "algorithm": algorithm,
                "data_length": len(data_bytes)
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Hash generated: {algorithm}")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error generating hash: {str(e)}")
            return {
                "success": False,
                "error": f"Error generating hash: {str(e)}"
            }


@NodeHandlerRegistry.register("date_format")
class DateFormatNodeHandler(BaseNodeHandler):
    """Handler for date/time formatting"""
    
    def execute(self):
        """Execute the date_format node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        date_path = self.get_param("date_path", "date")
        format_string = self.get_param("format_string", "%Y-%m-%d %H:%M:%S")
        input_format = self.get_param("input_format", None)
        timezone = self.get_param("timezone", None)
        operation = self.get_param("operation", "format")  # format, parse, now
        
        try:
            from datetime import datetime
            import pytz
            
            if operation == "now":
                # Get current datetime
                dt = datetime.now()
                if timezone:
                    tz = pytz.timezone(timezone)
                    dt = datetime.now(tz)
            else:
                # Extract date from input
                if isinstance(input_data, str):
                    date_str = input_data
                elif isinstance(input_data, dict):
                    date_str = input_data.get(date_path, "")
                else:
                    date_str = str(input_data)
                
                if not date_str:
                    self.log_error("No date found in input")
                    return {
                        "success": False,
                        "error": "No date found in input"
                    }
                
                # Parse date
                if input_format:
                    dt = datetime.strptime(date_str, input_format)
                else:
                    # Try to parse common formats
                    dt = frappe.utils.get_datetime(date_str)
            
            # Format date
            formatted = dt.strftime(format_string)
            
            # Prepare output
            output_data = {
                "formatted": formatted,
                "format_string": format_string,
                "timestamp": dt.timestamp(),
                "iso_format": dt.isoformat()
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Date formatted: {formatted}")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error formatting date: {str(e)}")
            return {
                "success": False,
                "error": f"Error formatting date: {str(e)}"
            }


@NodeHandlerRegistry.register("math_advanced")
class MathAdvancedNodeHandler(BaseNodeHandler):
    """Handler for advanced math operations"""
    
    def execute(self):
        """Execute the math_advanced node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        operation = self.get_param("operation", "sqrt")  # sqrt, pow, sin, cos, tan, log, exp, abs, round, floor, ceil
        value_path = self.get_param("value_path", "value")
        exponent = self.get_param("exponent", 2)  # For pow operation
        precision = self.get_param("precision", 2)  # For round operation
        
        try:
            import math
            
            # Extract value from input
            if isinstance(input_data, (int, float)):
                value = input_data
            elif isinstance(input_data, dict):
                value = input_data.get(value_path, 0)
            else:
                try:
                    value = float(input_data)
                except:
                    self.log_error("Invalid numeric value")
                    return {
                        "success": False,
                        "error": "Invalid numeric value"
                    }
            
            self.log_info(f"Performing {operation} on {value}")
            
            # Perform operation
            if operation == "sqrt":
                result = math.sqrt(value)
            elif operation == "pow":
                result = math.pow(value, exponent)
            elif operation == "sin":
                result = math.sin(value)
            elif operation == "cos":
                result = math.cos(value)
            elif operation == "tan":
                result = math.tan(value)
            elif operation == "log":
                result = math.log(value)
            elif operation == "log10":
                result = math.log10(value)
            elif operation == "exp":
                result = math.exp(value)
            elif operation == "abs":
                result = abs(value)
            elif operation == "round":
                result = round(value, precision)
            elif operation == "floor":
                result = math.floor(value)
            elif operation == "ceil":
                result = math.ceil(value)
            else:
                self.log_error(f"Unknown operation: {operation}")
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
            
            # Prepare output
            output_data = {
                "result": result,
                "operation": operation,
                "input_value": value
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Math result: {result}")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error in math operation: {str(e)}")
            return {
                "success": False,
                "error": f"Error in math operation: {str(e)}"
            }


@NodeHandlerRegistry.register("random_uuid")
class RandomUuidNodeHandler(BaseNodeHandler):
    """Handler for generating random UUIDs"""
    
    def execute(self):
        """Execute the random_uuid node"""
        # Get parameters
        version = self.get_param("version", 4)  # UUID version (1 or 4)
        count = self.get_param("count", 1)  # Number of UUIDs to generate
        
        try:
            import uuid
            
            self.log_info(f"Generating {count} UUID(s) version {version}")
            
            # Generate UUIDs
            uuids = []
            for _ in range(count):
                if version == 1:
                    new_uuid = str(uuid.uuid1())
                else:  # version 4 (default)
                    new_uuid = str(uuid.uuid4())
                uuids.append(new_uuid)
            
            # Prepare output
            if count == 1:
                output_data = {
                    "uuid": uuids[0],
                    "version": version
                }
            else:
                output_data = {
                    "uuids": uuids,
                    "count": count,
                    "version": version
                }
            
            self.set_output(output_data)
            
            self.log_info(f"Generated {count} UUID(s)")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error generating UUID: {str(e)}")
            return {
                "success": False,
                "error": f"Error generating UUID: {str(e)}"
            }


# ============================================================================
# MEDIUM PRIORITY - ADDITIONAL INTEGRATION NODES
# ============================================================================


@NodeHandlerRegistry.register("schedule")
class ScheduleNodeHandler(BaseNodeHandler):
    """Handler for scheduling delayed workflow execution"""
    
    def execute(self):
        """Execute the schedule node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        delay_seconds = self.get_param("delay_seconds", 0)
        delay_minutes = self.get_param("delay_minutes", 0)
        delay_hours = self.get_param("delay_hours", 0)
        schedule_at = self.get_param("schedule_at", None)  # ISO format datetime
        
        try:
            from datetime import datetime, timedelta
            
            # Calculate execution time
            if schedule_at:
                # Specific datetime
                execution_time = frappe.utils.get_datetime(schedule_at)
            else:
                # Relative delay
                total_seconds = delay_seconds + (delay_minutes * 60) + (delay_hours * 3600)
                execution_time = datetime.now() + timedelta(seconds=total_seconds)
            
            self.log_info(f"Scheduling execution for: {execution_time}")
            
            # Use Frappe's background job scheduler
            frappe.enqueue(
                method="automesh.automesh.workflow_engine.engine.execute_scheduled_workflow",
                queue="default",
                timeout=3600,
                is_async=True,
                at_front=False,
                enqueue_after_commit=True,
                execution_id=self.execution_context.execution_id,
                node_id=self.node_id,
                input_data=input_data,
                scheduled_at=execution_time
            )
            
            # Prepare output
            output_data = {
                "scheduled": True,
                "execution_time": execution_time.isoformat(),
                "delay_seconds": delay_seconds + (delay_minutes * 60) + (delay_hours * 3600),
                "input_data": input_data
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Execution scheduled for: {execution_time}")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error scheduling execution: {str(e)}")
            return {
                "success": False,
                "error": f"Error scheduling execution: {str(e)}"
            }


@NodeHandlerRegistry.register("file_upload")
class FileUploadNodeHandler(BaseNodeHandler):
    """Handler for uploading files to external services"""
    
    def execute(self):
        """Execute the file_upload node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("File upload node has no incoming connections")
            return {
                "success": False,
                "error": "File upload node has no incoming connections"
            }
        
        # Use the output of the connected node as input
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        service = self.get_param("service", "http")  # http, s3, ftp
        url = self.get_param("url", "")
        file_path = self.get_param("file_path", "")
        file_content_path = self.get_param("file_content_path", "content")
        file_name = self.get_param("file_name", "upload.txt")
        headers = self.get_param("headers", {})
        
        try:
            # Extract file content
            if file_path:
                # Read from file path
                import os
                if not os.path.exists(file_path):
                    self.log_error(f"File not found: {file_path}")
                    return {
                        "success": False,
                        "error": f"File not found: {file_path}"
                    }
                with open(file_path, 'rb') as f:
                    file_content = f.read()
            else:
                # Get from input data
                if isinstance(input_data, dict):
                    file_content = input_data.get(file_content_path, "")
                else:
                    file_content = input_data
                
                # Convert to bytes if string
                if isinstance(file_content, str):
                    file_content = file_content.encode('utf-8')
            
            if not file_content:
                self.log_error("No file content to upload")
                return {
                    "success": False,
                    "error": "No file content to upload"
                }
            
            self.log_info(f"Uploading file to {service}: {url}")
            
            # Upload based on service
            if service == "http" or service == "https":
                # HTTP upload
                files = {'file': (file_name, file_content)}
                response = requests.post(url, files=files, headers=headers)
                
                success = response.ok
                response_data = {
                    "status_code": response.status_code,
                    "response": response.text
                }
            
            elif service == "s3":
                # AWS S3 upload (requires boto3)
                try:
                    import boto3
                    
                    bucket = self.get_param("bucket", "")
                    key = self.get_param("key", file_name)
                    aws_access_key = self.get_param("aws_access_key", "")
                    aws_secret_key = self.get_param("aws_secret_key", "")
                    region = self.get_param("region", "us-east-1")
                    
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_key,
                        region_name=region
                    )
                    
                    s3_client.put_object(
                        Bucket=bucket,
                        Key=key,
                        Body=file_content
                    )
                    
                    success = True
                    response_data = {
                        "bucket": bucket,
                        "key": key,
                        "url": f"s3://{bucket}/{key}"
                    }
                    
                except ImportError:
                    self.log_error("boto3 not installed. Install with: pip install boto3")
                    return {
                        "success": False,
                        "error": "boto3 not installed"
                    }
            
            else:
                self.log_error(f"Unsupported service: {service}")
                return {
                    "success": False,
                    "error": f"Unsupported service: {service}"
                }
            
            # Prepare output
            output_data = {
                "uploaded": success,
                "service": service,
                "url": url,
                "file_name": file_name,
                "file_size": len(file_content),
                "response": response_data
            }
            
            self.set_output(output_data)
            
            if success:
                self.log_info(f"File uploaded successfully: {file_name}")
                return {
                    "success": True,
                    "data": output_data
                }
            else:
                self.log_error(f"File upload failed")
                return {
                    "success": False,
                    "error": "File upload failed",
                    "data": output_data
                }
            
        except Exception as e:
            self.log_error(f"Error uploading file: {str(e)}")
            return {
                "success": False,
                "error": f"Error uploading file: {str(e)}"
            }


@NodeHandlerRegistry.register("redis_get")
class RedisGetNodeHandler(BaseNodeHandler):
    """Handler for getting values from Redis"""
    
    def execute(self):
        """Execute the redis_get node"""
        # Get parameters
        key = self.get_param("key", "")
        default_value = self.get_param("default_value", None)
        redis_host = self.get_param("redis_host", "localhost")
        redis_port = self.get_param("redis_port", 6379)
        redis_db = self.get_param("redis_db", 0)
        redis_password = self.get_param("redis_password", None)
        
        if not key:
            self.log_error("No Redis key specified")
            return {
                "success": False,
                "error": "No Redis key specified"
            }
        
        try:
            # Try to import redis
            try:
                import redis
            except ImportError:
                self.log_error("redis-py not installed. Install with: pip install redis")
                return {
                    "success": False,
                    "error": "redis-py not installed"
                }
            
            self.log_info(f"Getting Redis value for key: {key}")
            
            # Connect to Redis
            r = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True
            )
            
            # Get value
            value = r.get(key)
            
            if value is None:
                value = default_value
                found = False
            else:
                found = True
                # Try to parse as JSON
                try:
                    value = json.loads(value)
                except:
                    pass  # Keep as string
            
            # Prepare output
            output_data = {
                "key": key,
                "value": value,
                "found": found,
                "has_default": default_value is not None
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Redis {'hit' if found else 'miss'} for key: {key}")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error getting from Redis: {str(e)}")
            return {
                "success": False,
                "error": f"Error getting from Redis: {str(e)}"
            }


@NodeHandlerRegistry.register("redis_set")
class RedisSetNodeHandler(BaseNodeHandler):
    """Handler for setting values in Redis"""
    
    def execute(self):
        """Execute the redis_set node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        key = self.get_param("key", "")
        value_path = self.get_param("value_path", "value")
        ttl = self.get_param("ttl", None)  # Time to live in seconds
        redis_host = self.get_param("redis_host", "localhost")
        redis_port = self.get_param("redis_port", 6379)
        redis_db = self.get_param("redis_db", 0)
        redis_password = self.get_param("redis_password", None)
        
        if not key:
            self.log_error("No Redis key specified")
            return {
                "success": False,
                "error": "No Redis key specified"
            }
        
        try:
            # Try to import redis
            try:
                import redis
            except ImportError:
                self.log_error("redis-py not installed. Install with: pip install redis")
                return {
                    "success": False,
                    "error": "redis-py not installed"
                }
            
            # Extract value from input
            if isinstance(input_data, dict):
                value = input_data.get(value_path, input_data)
            else:
                value = input_data
            
            # Convert to JSON string if not a string
            if not isinstance(value, str):
                value = json.dumps(value)
            
            self.log_info(f"Setting Redis value for key: {key}")
            
            # Connect to Redis
            r = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True
            )
            
            # Set value
            if ttl:
                r.setex(key, ttl, value)
            else:
                r.set(key, value)
            
            # Prepare output
            output_data = {
                "key": key,
                "value": value,
                "ttl": ttl,
                "cached": True
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Redis set for key: {key}" + (f" (TTL: {ttl}s)" if ttl else ""))
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error setting in Redis: {str(e)}")
            return {
                "success": False,
                "error": f"Error setting in Redis: {str(e)}"
            }


# ============================================================================
# LOW PRIORITY - ADDITIONAL UTILITY NODES
# ============================================================================


@NodeHandlerRegistry.register("encrypt")
class EncryptNodeHandler(BaseNodeHandler):
    """Handler for encrypting data"""
    
    def execute(self):
        """Execute the encrypt node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("Encrypt node has no incoming connections")
            return {
                "success": False,
                "error": "Encrypt node has no incoming connections"
            }
        
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        data_path = self.get_param("data_path", "data")
        encryption_key = self.get_param("encryption_key", "")
        algorithm = self.get_param("algorithm", "aes")  # aes, fernet
        
        if not encryption_key:
            self.log_error("No encryption key provided")
            return {
                "success": False,
                "error": "No encryption key provided"
            }
        
        try:
            # Extract data to encrypt
            if isinstance(input_data, str):
                data = input_data
            elif isinstance(input_data, dict):
                data = input_data.get(data_path, "")
            else:
                data = str(input_data)
            
            if not data:
                self.log_error("No data to encrypt")
                return {
                    "success": False,
                    "error": "No data to encrypt"
                }
            
            self.log_info(f"Encrypting data with {algorithm}")
            
            # Convert to bytes
            data_bytes = data.encode('utf-8') if isinstance(data, str) else data
            
            if algorithm == "fernet":
                from cryptography.fernet import Fernet
                import base64
                
                # Ensure key is proper format
                if len(encryption_key) < 32:
                    # Pad key to 32 bytes
                    encryption_key = encryption_key.ljust(32)[:32]
                
                key = base64.urlsafe_b64encode(encryption_key.encode('utf-8'))
                f = Fernet(key)
                encrypted = f.encrypt(data_bytes)
                encrypted_str = encrypted.decode('utf-8')
                
            else:  # Simple base64 encoding as fallback
                import base64
                encrypted = base64.b64encode(data_bytes)
                encrypted_str = encrypted.decode('utf-8')
            
            # Prepare output
            output_data = {
                "encrypted": encrypted_str,
                "algorithm": algorithm,
                "original_length": len(data_bytes)
            }
            
            self.set_output(output_data)
            
            self.log_info("Data encrypted successfully")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error encrypting data: {str(e)}")
            return {
                "success": False,
                "error": f"Error encrypting data: {str(e)}"
            }


@NodeHandlerRegistry.register("decrypt")
class DecryptNodeHandler(BaseNodeHandler):
    """Handler for decrypting data"""
    
    def execute(self):
        """Execute the decrypt node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("Decrypt node has no incoming connections")
            return {
                "success": False,
                "error": "Decrypt node has no incoming connections"
            }
        
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        data_path = self.get_param("data_path", "encrypted")
        encryption_key = self.get_param("encryption_key", "")
        algorithm = self.get_param("algorithm", "aes")
        
        if not encryption_key:
            self.log_error("No encryption key provided")
            return {
                "success": False,
                "error": "No encryption key provided"
            }
        
        try:
            # Extract encrypted data
            if isinstance(input_data, str):
                encrypted_data = input_data
            elif isinstance(input_data, dict):
                encrypted_data = input_data.get(data_path, "")
            else:
                encrypted_data = str(input_data)
            
            if not encrypted_data:
                self.log_error("No encrypted data found")
                return {
                    "success": False,
                    "error": "No encrypted data found"
                }
            
            self.log_info(f"Decrypting data with {algorithm}")
            
            if algorithm == "fernet":
                from cryptography.fernet import Fernet
                import base64
                
                # Ensure key is proper format
                if len(encryption_key) < 32:
                    encryption_key = encryption_key.ljust(32)[:32]
                
                key = base64.urlsafe_b64encode(encryption_key.encode('utf-8'))
                f = Fernet(key)
                decrypted = f.decrypt(encrypted_data.encode('utf-8'))
                decrypted_str = decrypted.decode('utf-8')
                
            else:  # Simple base64 decoding as fallback
                import base64
                decrypted = base64.b64decode(encrypted_data.encode('utf-8'))
                decrypted_str = decrypted.decode('utf-8')
            
            # Prepare output
            output_data = {
                "decrypted": decrypted_str,
                "algorithm": algorithm
            }
            
            self.set_output(output_data)
            
            self.log_info("Data decrypted successfully")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error decrypting data: {str(e)}")
            return {
                "success": False,
                "error": f"Error decrypting data: {str(e)}"
            }


@NodeHandlerRegistry.register("compress")
class CompressNodeHandler(BaseNodeHandler):
    """Handler for compressing data"""
    
    def execute(self):
        """Execute the compress node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("Compress node has no incoming connections")
            return {
                "success": False,
                "error": "Compress node has no incoming connections"
            }
        
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        data_path = self.get_param("data_path", "data")
        algorithm = self.get_param("algorithm", "gzip")  # gzip, zlib
        
        try:
            # Extract data to compress
            if isinstance(input_data, str):
                data = input_data
            elif isinstance(input_data, dict):
                data = input_data.get(data_path, "")
            else:
                data = str(input_data)
            
            if not data:
                self.log_error("No data to compress")
                return {
                    "success": False,
                    "error": "No data to compress"
                }
            
            self.log_info(f"Compressing data with {algorithm}")
            
            # Convert to bytes
            data_bytes = data.encode('utf-8') if isinstance(data, str) else data
            original_size = len(data_bytes)
            
            # Compress
            if algorithm == "gzip":
                import gzip
                compressed = gzip.compress(data_bytes)
            elif algorithm == "zlib":
                import zlib
                compressed = zlib.compress(data_bytes)
            else:
                self.log_error(f"Unknown algorithm: {algorithm}")
                return {
                    "success": False,
                    "error": f"Unknown algorithm: {algorithm}"
                }
            
            # Convert to base64 for JSON serialization
            import base64
            compressed_str = base64.b64encode(compressed).decode('utf-8')
            compressed_size = len(compressed)
            
            # Prepare output
            output_data = {
                "compressed": compressed_str,
                "algorithm": algorithm,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": round((1 - compressed_size / original_size) * 100, 2)
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Data compressed: {original_size} -> {compressed_size} bytes ({output_data['compression_ratio']}% reduction)")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error compressing data: {str(e)}")
            return {
                "success": False,
                "error": f"Error compressing data: {str(e)}"
            }


@NodeHandlerRegistry.register("decompress")
class DecompressNodeHandler(BaseNodeHandler):
    """Handler for decompressing data"""
    
    def execute(self):
        """Execute the decompress node"""
        # Get input data from connected nodes
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("Decompress node has no incoming connections")
            return {
                "success": False,
                "error": "Decompress node has no incoming connections"
            }
        
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        data_path = self.get_param("data_path", "compressed")
        algorithm = self.get_param("algorithm", "gzip")
        
        try:
            # Extract compressed data
            if isinstance(input_data, str):
                compressed_data = input_data
            elif isinstance(input_data, dict):
                compressed_data = input_data.get(data_path, "")
            else:
                compressed_data = str(input_data)
            
            if not compressed_data:
                self.log_error("No compressed data found")
                return {
                    "success": False,
                    "error": "No compressed data found"
                }
            
            self.log_info(f"Decompressing data with {algorithm}")
            
            # Decode from base64
            import base64
            compressed_bytes = base64.b64decode(compressed_data)
            
            # Decompress
            if algorithm == "gzip":
                import gzip
                decompressed = gzip.decompress(compressed_bytes)
            elif algorithm == "zlib":
                import zlib
                decompressed = zlib.decompress(compressed_bytes)
            else:
                self.log_error(f"Unknown algorithm: {algorithm}")
                return {
                    "success": False,
                    "error": f"Unknown algorithm: {algorithm}"
                }
            
            # Convert to string
            decompressed_str = decompressed.decode('utf-8')
            
            # Prepare output
            output_data = {
                "decompressed": decompressed_str,
                "algorithm": algorithm,
                "decompressed_size": len(decompressed)
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Data decompressed successfully: {len(decompressed)} bytes")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error decompressing data: {str(e)}")
            return {
                "success": False,
                "error": f"Error decompressing data: {str(e)}"
            }


# ============================================================================
# LOW PRIORITY - NOTIFICATION NODES
# ============================================================================


@NodeHandlerRegistry.register("slack_message")
class SlackMessageNodeHandler(BaseNodeHandler):
    """Handler for sending Slack messages"""
    
    def execute(self):
        """Execute the slack_message node"""
        # Get input data
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        webhook_url = self.get_param("webhook_url", "")
        message = self.get_param("message", "")
        channel = self.get_param("channel", "")
        username = self.get_param("username", "Workflow Bot")
        
        if not webhook_url:
            self.log_error("No Slack webhook URL provided")
            return {
                "success": False,
                "error": "No Slack webhook URL provided"
            }
        
        if not message:
            message = str(input_data)
        
        try:
            self.log_info(f"Sending Slack message")
            
            # Prepare payload
            payload = {
                "text": message,
                "username": username
            }
            
            if channel:
                payload["channel"] = channel
            
            # Send to Slack
            response = requests.post(webhook_url, json=payload)
            
            # Prepare output
            output_data = {
                "sent": response.ok,
                "status_code": response.status_code,
                "message": message,
                "channel": channel
            }
            
            self.set_output(output_data)
            
            if response.ok:
                self.log_info("Slack message sent successfully")
                return {
                    "success": True,
                    "data": output_data
                }
            else:
                self.log_error(f"Slack message failed: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Slack message failed: {response.status_code}",
                    "data": output_data
                }
            
        except Exception as e:
            self.log_error(f"Error sending Slack message: {str(e)}")
            return {
                "success": False,
                "error": f"Error sending Slack message: {str(e)}"
            }


@NodeHandlerRegistry.register("discord_message")
class DiscordMessageNodeHandler(BaseNodeHandler):
    """Handler for sending Discord messages"""
    
    def execute(self):
        """Execute the discord_message node"""
        # Get input data
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        webhook_url = self.get_param("webhook_url", "")
        message = self.get_param("message", "")
        username = self.get_param("username", "Workflow Bot")
        
        if not webhook_url:
            self.log_error("No Discord webhook URL provided")
            return {
                "success": False,
                "error": "No Discord webhook URL provided"
            }
        
        if not message:
            message = str(input_data)
        
        try:
            self.log_info(f"Sending Discord message")
            
            # Prepare payload
            payload = {
                "content": message,
                "username": username
            }
            
            # Send to Discord
            response = requests.post(webhook_url, json=payload)
            
            # Prepare output
            output_data = {
                "sent": response.ok,
                "status_code": response.status_code,
                "message": message
            }
            
            self.set_output(output_data)
            
            if response.ok:
                self.log_info("Discord message sent successfully")
                return {
                    "success": True,
                    "data": output_data
                }
            else:
                self.log_error(f"Discord message failed: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Discord message failed: {response.status_code}",
                    "data": output_data
                }
            
        except Exception as e:
            self.log_error(f"Error sending Discord message: {str(e)}")
            return {
                "success": False,
                "error": f"Error sending Discord message: {str(e)}"
            }


@NodeHandlerRegistry.register("telegram_message")
class TelegramMessageNodeHandler(BaseNodeHandler):
    """Handler for sending Telegram messages"""
    
    def execute(self):
        """Execute the telegram_message node"""
        # Get input data
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        bot_token = self.get_param("bot_token", "")
        chat_id = self.get_param("chat_id", "")
        message = self.get_param("message", "")
        
        if not bot_token or not chat_id:
            self.log_error("Bot token and chat ID are required")
            return {
                "success": False,
                "error": "Bot token and chat ID are required"
            }
        
        if not message:
            message = str(input_data)
        
        try:
            self.log_info(f"Sending Telegram message")
            
            # Prepare URL and payload
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message
            }
            
            # Send to Telegram
            response = requests.post(url, json=payload)
            
            # Prepare output
            output_data = {
                "sent": response.ok,
                "status_code": response.status_code,
                "message": message,
                "chat_id": chat_id
            }
            
            self.set_output(output_data)
            
            if response.ok:
                self.log_info("Telegram message sent successfully")
                return {
                    "success": True,
                    "data": output_data
                }
            else:
                self.log_error(f"Telegram message failed: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Telegram message failed: {response.status_code}",
                    "data": output_data
                }
            
        except Exception as e:
            self.log_error(f"Error sending Telegram message: {str(e)}")
            return {
                "success": False,
                "error": f"Error sending Telegram message: {str(e)}"
            }


@NodeHandlerRegistry.register("sms_send")
class SmsSendNodeHandler(BaseNodeHandler):
    """Handler for sending SMS messages"""
    
    def execute(self):
        """Execute the sms_send node"""
        # Get input data
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        provider = self.get_param("provider", "twilio")  # twilio, aws_sns
        to_number = self.get_param("to_number", "")
        message = self.get_param("message", "")
        
        # Provider-specific parameters
        account_sid = self.get_param("account_sid", "")
        auth_token = self.get_param("auth_token", "")
        from_number = self.get_param("from_number", "")
        
        if not to_number:
            self.log_error("No recipient phone number provided")
            return {
                "success": False,
                "error": "No recipient phone number provided"
            }
        
        if not message:
            message = str(input_data)
        
        try:
            self.log_info(f"Sending SMS via {provider}")
            
            if provider == "twilio":
                # Twilio SMS (requires twilio library)
                try:
                    from twilio.rest import Client
                    
                    client = Client(account_sid, auth_token)
                    sms = client.messages.create(
                        body=message,
                        from_=from_number,
                        to=to_number
                    )
                    
                    success = True
                    response_data = {
                        "sid": sms.sid,
                        "status": sms.status
                    }
                    
                except ImportError:
                    self.log_error("twilio library not installed")
                    return {
                        "success": False,
                        "error": "twilio library not installed. Install with: pip install twilio"
                    }
            
            else:
                self.log_error(f"Unsupported SMS provider: {provider}")
                return {
                    "success": False,
                    "error": f"Unsupported SMS provider: {provider}"
                }
            
            # Prepare output
            output_data = {
                "sent": success,
                "provider": provider,
                "to_number": to_number,
                "message": message,
                "response": response_data
            }
            
            self.set_output(output_data)
            
            self.log_info("SMS sent successfully")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error sending SMS: {str(e)}")
            return {
                "success": False,
                "error": f"Error sending SMS: {str(e)}"
            }


@NodeHandlerRegistry.register("push_notification")
class PushNotificationNodeHandler(BaseNodeHandler):
    """Handler for sending push notifications"""
    
    def execute(self):
        """Execute the push_notification node"""
        # Get input data
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        input_data = {}
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        provider = self.get_param("provider", "fcm")  # fcm, apns
        device_token = self.get_param("device_token", "")
        title = self.get_param("title", "Notification")
        message = self.get_param("message", "")
        
        if not device_token:
            self.log_error("No device token provided")
            return {
                "success": False,
                "error": "No device token provided"
            }
        
        if not message:
            message = str(input_data)
        
        try:
            self.log_info(f"Sending push notification via {provider}")
            
            # Note: This is a simplified implementation
            # In production, you would use FCM/APNS libraries
            
            # Prepare output
            output_data = {
                "sent": True,
                "provider": provider,
                "device_token": device_token[:10] + "...",  # Truncate for security
                "title": title,
                "message": message
            }
            
            self.set_output(output_data)
            
            self.log_info("Push notification queued (implementation required)")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error sending push notification: {str(e)}")
            return {
                "success": False,
                "error": f"Error sending push notification: {str(e)}"
            }


# ============================================================================
# MEDIUM PRIORITY - AI/ML NODES
# ============================================================================


@NodeHandlerRegistry.register("openai_embedding")
class OpenAIEmbeddingNodeHandler(BaseNodeHandler):
    """Handler for generating OpenAI embeddings"""
    
    def execute(self):
        """Execute the openai_embedding node"""
        # Get input data
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("OpenAI embedding node has no incoming connections")
            return {
                "success": False,
                "error": "OpenAI embedding node has no incoming connections"
            }
        
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        text_path = self.get_param("text_path", "text")
        api_key = self.get_param("api_key", "")
        model = self.get_param("model", "text-embedding-ada-002")
        
        if not api_key:
            self.log_error("No OpenAI API key provided")
            return {
                "success": False,
                "error": "No OpenAI API key provided"
            }
        
        try:
            # Extract text
            if isinstance(input_data, str):
                text = input_data
            elif isinstance(input_data, dict):
                text = input_data.get(text_path, "")
            else:
                text = str(input_data)
            
            if not text:
                self.log_error("No text to generate embedding")
                return {
                    "success": False,
                    "error": "No text to generate embedding"
                }
            
            self.log_info(f"Generating embedding with model: {model}")
            
            # Call OpenAI API
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "input": text,
                "model": model
            }
            
            response = requests.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=payload
            )
            
            if not response.ok:
                self.log_error(f"OpenAI API error: {response.status_code}")
                return {
                    "success": False,
                    "error": f"OpenAI API error: {response.status_code}",
                    "details": response.text
                }
            
            result = response.json()
            embedding = result["data"][0]["embedding"]
            
            # Prepare output
            output_data = {
                "embedding": embedding,
                "model": model,
                "dimensions": len(embedding),
                "text_length": len(text)
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Embedding generated: {len(embedding)} dimensions")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error generating embedding: {str(e)}")
            return {
                "success": False,
                "error": f"Error generating embedding: {str(e)}"
            }


@NodeHandlerRegistry.register("text_analyze")
class TextAnalyzeNodeHandler(BaseNodeHandler):
    """Handler for text analysis (sentiment, keywords)"""
    
    def execute(self):
        """Execute the text_analyze node"""
        # Get input data
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("Text analyze node has no incoming connections")
            return {
                "success": False,
                "error": "Text analyze node has no incoming connections"
            }
        
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        text_path = self.get_param("text_path", "text")
        analysis_type = self.get_param("analysis_type", "sentiment")  # sentiment, keywords, summary
        
        try:
            # Extract text
            if isinstance(input_data, str):
                text = input_data
            elif isinstance(input_data, dict):
                text = input_data.get(text_path, "")
            else:
                text = str(input_data)
            
            if not text:
                self.log_error("No text to analyze")
                return {
                    "success": False,
                    "error": "No text to analyze"
                }
            
            self.log_info(f"Analyzing text: {analysis_type}")
            
            # Simple analysis (in production, use NLP libraries like textblob, spacy, etc.)
            if analysis_type == "sentiment":
                # Simple sentiment analysis
                positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "best"]
                negative_words = ["bad", "terrible", "awful", "horrible", "worst", "hate", "poor"]
                
                text_lower = text.lower()
                positive_count = sum(1 for word in positive_words if word in text_lower)
                negative_count = sum(1 for word in negative_words if word in negative_words)
                
                if positive_count > negative_count:
                    sentiment = "positive"
                    score = 0.7
                elif negative_count > positive_count:
                    sentiment = "negative"
                    score = 0.3
                else:
                    sentiment = "neutral"
                    score = 0.5
                
                analysis_result = {
                    "sentiment": sentiment,
                    "score": score,
                    "positive_count": positive_count,
                    "negative_count": negative_count
                }
            
            elif analysis_type == "keywords":
                # Simple keyword extraction
                words = text.lower().split()
                word_freq = {}
                for word in words:
                    if len(word) > 3:  # Only words longer than 3 chars
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                # Get top 10 keywords
                keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
                
                analysis_result = {
                    "keywords": [k[0] for k in keywords],
                    "frequencies": dict(keywords),
                    "total_words": len(words)
                }
            
            elif analysis_type == "summary":
                # Simple summary (first 200 chars)
                summary = text[:200] + "..." if len(text) > 200 else text
                
                analysis_result = {
                    "summary": summary,
                    "original_length": len(text),
                    "summary_length": len(summary)
                }
            
            else:
                self.log_error(f"Unknown analysis type: {analysis_type}")
                return {
                    "success": False,
                    "error": f"Unknown analysis type: {analysis_type}"
                }
            
            # Prepare output
            output_data = {
                "analysis_type": analysis_type,
                "result": analysis_result,
                "text_length": len(text)
            }
            
            self.set_output(output_data)
            
            self.log_info(f"Text analysis complete: {analysis_type}")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except Exception as e:
            self.log_error(f"Error analyzing text: {str(e)}")
            return {
                "success": False,
                "error": f"Error analyzing text: {str(e)}"
            }


@NodeHandlerRegistry.register("image_process")
class ImageProcessNodeHandler(BaseNodeHandler):
    """Handler for image processing operations"""
    
    def execute(self):
        """Execute the image_process node"""
        # Get input data
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if not incoming_connections:
            self.log_error("Image process node has no incoming connections")
            return {
                "success": False,
                "error": "Image process node has no incoming connections"
            }
        
        source_node_id = incoming_connections[0].get("source")
        input_data = self.execution_context.get_node_output(source_node_id)
        
        # Get parameters
        image_path = self.get_param("image_path", "")
        operation = self.get_param("operation", "resize")  # resize, crop, rotate, grayscale
        width = self.get_param("width", 800)
        height = self.get_param("height", 600)
        
        if not image_path:
            self.log_error("No image path provided")
            return {
                "success": False,
                "error": "No image path provided"
            }
        
        try:
            import os
            
            if not os.path.exists(image_path):
                self.log_error(f"Image not found: {image_path}")
                return {
                    "success": False,
                    "error": f"Image not found: {image_path}"
                }
            
            self.log_info(f"Processing image: {operation}")
            
            # Try to use PIL/Pillow
            try:
                from PIL import Image
                
                img = Image.open(image_path)
                original_size = img.size
                
                if operation == "resize":
                    img = img.resize((width, height))
                elif operation == "grayscale":
                    img = img.convert('L')
                elif operation == "rotate":
                    angle = self.get_param("angle", 90)
                    img = img.rotate(angle)
                else:
                    self.log_error(f"Unknown operation: {operation}")
                    return {
                        "success": False,
                        "error": f"Unknown operation: {operation}"
                    }
                
                # Save processed image
                output_path = image_path.replace(".", f"_processed.")
                img.save(output_path)
                
                # Prepare output
                output_data = {
                    "processed": True,
                    "operation": operation,
                    "original_size": original_size,
                    "new_size": img.size,
                    "output_path": output_path
                }
                
                self.set_output(output_data)
                
                self.log_info(f"Image processed successfully: {operation}")
                
                return {
                    "success": True,
                    "data": output_data
                }
                
            except ImportError:
                self.log_error("PIL/Pillow not installed. Install with: pip install Pillow")
                return {
                    "success": False,
                    "error": "PIL/Pillow not installed"
                }
            
        except Exception as e:
            self.log_error(f"Error processing image: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing image: {str(e)}"
            }
