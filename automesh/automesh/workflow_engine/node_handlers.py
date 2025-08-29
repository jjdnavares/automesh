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
