import frappe
import random
import time
from datetime import datetime
import json
import math
from .node_handlers import NodeHandlerRegistry, BaseNodeHandler


@NodeHandlerRegistry.register("test_echo")
class TestEchoNodeHandler(BaseNodeHandler):
    """Test node handler that simply echoes input to output"""
    
    def execute(self):
        """Execute the echo node"""
        # Get message parameter
        message = self.get_param("message", "Hello, world!")
        
        # Get input data from connected nodes if available
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        input_data = {}
        
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id) or {}
        
        # Prepare output
        output_data = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "input_data": input_data
        }
        
        self.log_info(f"Echo message: {message}")
        self.set_output(output_data)
        
        return {
            "success": True,
            "data": output_data
        }


@NodeHandlerRegistry.register("test_random")
class TestRandomNodeHandler(BaseNodeHandler):
    """Test node handler that generates random data"""
    
    def execute(self):
        """Execute the random node"""
        # Get parameters
        data_type = self.get_param("data_type", "number")
        min_value = self.get_param("min_value", 1)
        max_value = self.get_param("max_value", 100)
        length = self.get_param("length", 10)
        
        # Generate random data based on type
        random_data = None
        
        if data_type == "number":
            random_data = random.randint(int(min_value), int(max_value))
        elif data_type == "float":
            random_data = random.uniform(float(min_value), float(max_value))
        elif data_type == "boolean":
            random_data = random.choice([True, False])
        elif data_type == "string":
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            random_data = ''.join(random.choice(chars) for _ in range(int(length)))
        elif data_type == "array":
            random_data = [random.randint(int(min_value), int(max_value)) for _ in range(int(length))]
        elif data_type == "object":
            keys = [f"item{i}" for i in range(int(length))]
            values = [random.randint(int(min_value), int(max_value)) for _ in range(int(length))]
            random_data = dict(zip(keys, values))
        
        # Prepare output
        output_data = {
            "type": data_type,
            "value": random_data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_info(f"Generated random {data_type}: {random_data}")
        self.set_output(output_data)
        
        return {
            "success": True,
            "data": output_data
        }


@NodeHandlerRegistry.register("test_delay")
class TestDelayNodeHandler(BaseNodeHandler):
    """Test node handler that introduces a delay in the workflow"""
    
    def execute(self):
        """Execute the delay node"""
        # Get parameters
        duration = self.get_param("duration", 5)  # default 5 seconds
        
        # Get input data from connected nodes if available
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        input_data = {}
        
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id) or {}
        
        # Log start
        self.log_info(f"Starting delay of {duration} seconds")
        
        # Delay execution
        time.sleep(int(duration))
        
        # Prepare output
        output_data = {
            "delay_duration": duration,
            "input_data": input_data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_info(f"Delay of {duration} seconds completed")
        self.set_output(output_data)
        
        return {
            "success": True,
            "data": output_data
        }


@NodeHandlerRegistry.register("test_math")
class TestMathNodeHandler(BaseNodeHandler):
    """Test node handler that performs mathematical operations"""
    
    def execute(self):
        """Execute the math node"""
        # Get parameters
        operation = self.get_param("operation", "add")
        operand1 = self.get_param("operand1", 0)
        operand2 = self.get_param("operand2", 0)
        
        # Get input data from connected nodes if available
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id) or {}
            
            # Check if input has values to use
            if "value" in input_data and isinstance(input_data["value"], (int, float)):
                operand1 = input_data["value"]
            elif "operand1" in input_data:
                operand1 = input_data["operand1"]
            elif "operand2" in input_data:
                operand2 = input_data["operand2"]
        
        # Ensure operands are numeric
        try:
            operand1 = float(operand1)
            operand2 = float(operand2)
        except (ValueError, TypeError):
            self.log_error(f"Invalid operands: {operand1}, {operand2}")
            return {
                "success": False,
                "error": f"Invalid operands: {operand1}, {operand2}"
            }
        
        # Perform operation
        result = None
        
        if operation == "add":
            result = operand1 + operand2
        elif operation == "subtract":
            result = operand1 - operand2
        elif operation == "multiply":
            result = operand1 * operand2
        elif operation == "divide":
            if operand2 == 0:
                self.log_error("Division by zero error")
                return {
                    "success": False,
                    "error": "Division by zero error"
                }
            result = operand1 / operand2
        elif operation == "power":
            result = math.pow(operand1, operand2)
        elif operation == "modulo":
            if operand2 == 0:
                self.log_error("Modulo by zero error")
                return {
                    "success": False,
                    "error": "Modulo by zero error"
                }
            result = operand1 % operand2
        else:
            self.log_error(f"Unknown operation: {operation}")
            return {
                "success": False,
                "error": f"Unknown operation: {operation}"
            }
        
        # Prepare output
        output_data = {
            "operation": operation,
            "operand1": operand1,
            "operand2": operand2,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_info(f"Math {operation}: {operand1} {operation} {operand2} = {result}")
        self.set_output(output_data)
        
        return {
            "success": True,
            "data": output_data
        }


@NodeHandlerRegistry.register("test_error")
class TestErrorNodeHandler(BaseNodeHandler):
    """Test node handler that deliberately generates an error"""
    
    def execute(self):
        """Execute the error node"""
        # Get parameters
        error_type = self.get_param("error_type", "standard")
        error_message = self.get_param("error_message", "Test error message")
        should_fail = self.get_param("should_fail", True)
        
        # Log the error attempt
        self.log_info(f"Testing error handling with type: {error_type}")
        
        if should_fail:
            # Generate different types of errors based on parameter
            if error_type == "standard":
                self.log_error(error_message)
                return {
                    "success": False,
                    "error": error_message
                }
            elif error_type == "exception":
                # Deliberately raise an exception
                raise Exception(error_message)
            elif error_type == "division_by_zero":
                # Deliberately cause a division by zero error
                result = 1 / 0
                return {
                    "success": True,
                    "data": {"result": result}
                }
            elif error_type == "key_error":
                # Deliberately cause a key error
                empty_dict = {}
                result = empty_dict["non_existent_key"]
                return {
                    "success": True,
                    "data": {"result": result}
                }
            else:
                self.log_error(f"Unknown error type: {error_type}")
                return {
                    "success": False,
                    "error": f"Unknown error type: {error_type}"
                }
        else:
            # Don't actually fail, just simulate testing error handling
            output_data = {
                "error_tested": True,
                "error_type": error_type,
                "error_message": error_message,
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_info(f"Error handling test completed without actual failure")
            self.set_output(output_data)
            
            return {
                "success": True,
                "data": output_data
            }


@NodeHandlerRegistry.register("test_transform")
class TestTransformNodeHandler(BaseNodeHandler):
    """Test node handler that transforms data"""
    
    def execute(self):
        """Execute the transform node"""
        # Get parameters
        transform_type = self.get_param("transform_type", "uppercase")
        
        # Get input data from connected nodes if available
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        input_data = {}
        input_value = None
        
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id) or {}
            
            # Try to extract a value to transform
            if "value" in input_data:
                input_value = input_data["value"]
            elif "result" in input_data:
                input_value = input_data["result"]
            elif "message" in input_data:
                input_value = input_data["message"]
            else:
                # Use the whole input data as value
                input_value = input_data
        else:
            # Use default value if no input
            input_value = self.get_param("value", "")
        
        # Apply transformation
        result = None
        
        try:
            if transform_type == "uppercase" and isinstance(input_value, str):
                result = input_value.upper()
            elif transform_type == "lowercase" and isinstance(input_value, str):
                result = input_value.lower()
            elif transform_type == "capitalize" and isinstance(input_value, str):
                result = input_value.capitalize()
            elif transform_type == "reverse" and isinstance(input_value, str):
                result = input_value[::-1]
            elif transform_type == "length":
                result = len(input_value) if hasattr(input_value, "__len__") else 0
            elif transform_type == "to_json" and not isinstance(input_value, str):
                result = json.dumps(input_value)
            elif transform_type == "from_json" and isinstance(input_value, str):
                result = json.loads(input_value)
            elif transform_type == "increment" and isinstance(input_value, (int, float)):
                result = input_value + 1
            elif transform_type == "decrement" and isinstance(input_value, (int, float)):
                result = input_value - 1
            elif transform_type == "double" and isinstance(input_value, (int, float)):
                result = input_value * 2
            elif transform_type == "half" and isinstance(input_value, (int, float)):
                result = input_value / 2
            else:
                self.log_error(f"Transformation {transform_type} not applicable to input: {input_value}")
                return {
                    "success": False,
                    "error": f"Transformation {transform_type} not applicable to input: {input_value}"
                }
        except Exception as e:
            self.log_error(f"Error applying transformation: {str(e)}")
            return {
                "success": False,
                "error": f"Error applying transformation: {str(e)}"
            }
        
        # Prepare output
        output_data = {
            "transform_type": transform_type,
            "input_value": input_value,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_info(f"Transformed data using {transform_type}: {result}")
        self.set_output(output_data)
        
        return {
            "success": True,
            "data": output_data
        }


# Function to create test node types in the database
def create_test_node_types():
    """Create test node types in the database"""
    test_node_types = [
        {
            "name": "test_echo",
            "type": "test_echo",
            "label": "Echo Test",
            "description": "A test node that echoes input to output",
            "icon": "echo",
            "color": "#3498db",
            "category": "test",
            "is_system": 1,
            "is_enabled": 1,
            "inputs": json.dumps([
                {
                    "name": "message",
                    "label": "Message",
                    "type": "string",
                    "default": "Hello, world!"
                }
            ]),
            "outputs": json.dumps([
                {
                    "name": "message",
                    "label": "Message",
                    "type": "string"
                },
                {
                    "name": "timestamp",
                    "label": "Timestamp",
                    "type": "string"
                }
            ])
        },
        {
            "name": "test_random",
            "type": "test_random",
            "label": "Random Generator",
            "description": "Generates random data for testing",
            "icon": "dice",
            "color": "#9b59b6",
            "category": "test",
            "is_system": 1,
            "is_enabled": 1,
            "inputs": json.dumps([
                {
                    "name": "data_type",
                    "label": "Data Type",
                    "type": "select",
                    "options": ["number", "float", "boolean", "string", "array", "object"],
                    "default": "number"
                },
                {
                    "name": "min_value",
                    "label": "Min Value",
                    "type": "number",
                    "default": 1
                },
                {
                    "name": "max_value",
                    "label": "Max Value",
                    "type": "number",
                    "default": 100
                },
                {
                    "name": "length",
                    "label": "Length",
                    "type": "number",
                    "default": 10
                }
            ]),
            "outputs": json.dumps([
                {
                    "name": "value",
                    "label": "Random Value",
                    "type": "any"
                },
                {
                    "name": "type",
                    "label": "Data Type",
                    "type": "string"
                }
            ])
        },
        {
            "name": "test_delay",
            "type": "test_delay",
            "label": "Delay",
            "description": "Introduces a delay in the workflow for testing",
            "icon": "clock",
            "color": "#e74c3c",
            "category": "test",
            "is_system": 1,
            "is_enabled": 1,
            "inputs": json.dumps([
                {
                    "name": "duration",
                    "label": "Duration (seconds)",
                    "type": "number",
                    "default": 5
                }
            ]),
            "outputs": json.dumps([
                {
                    "name": "delay_duration",
                    "label": "Delay Duration",
                    "type": "number"
                },
                {
                    "name": "timestamp",
                    "label": "Completion Time",
                    "type": "string"
                }
            ])
        },
        {
            "name": "test_math",
            "type": "test_math",
            "label": "Math Operation",
            "description": "Performs a math operation for testing",
            "icon": "calculator",
            "color": "#f1c40f",
            "category": "test",
            "is_system": 1,
            "is_enabled": 1,
            "inputs": json.dumps([
                {
                    "name": "operation",
                    "label": "Operation",
                    "type": "select",
                    "options": ["add", "subtract", "multiply", "divide", "power", "modulo"],
                    "default": "add"
                },
                {
                    "name": "operand1",
                    "label": "First Operand",
                    "type": "number",
                    "default": 0
                },
                {
                    "name": "operand2",
                    "label": "Second Operand",
                    "type": "number",
                    "default": 0
                }
            ]),
            "outputs": json.dumps([
                {
                    "name": "result",
                    "label": "Result",
                    "type": "number"
                },
                {
                    "name": "operation",
                    "label": "Operation",
                    "type": "string"
                }
            ])
        },
        {
            "name": "test_error",
            "type": "test_error",
            "label": "Error Generator",
            "description": "Generates errors for testing error handling",
            "icon": "bug",
            "color": "#e74c3c",
            "category": "test",
            "is_system": 1,
            "is_enabled": 1,
            "inputs": json.dumps([
                {
                    "name": "error_type",
                    "label": "Error Type",
                    "type": "select",
                    "options": ["standard", "exception", "division_by_zero", "key_error"],
                    "default": "standard"
                },
                {
                    "name": "error_message",
                    "label": "Error Message",
                    "type": "string",
                    "default": "Test error message"
                },
                {
                    "name": "should_fail",
                    "label": "Should Fail",
                    "type": "boolean",
                    "default": True
                }
            ]),
            "outputs": json.dumps([
                {
                    "name": "error_tested",
                    "label": "Error Tested",
                    "type": "boolean"
                }
            ])
        },
        {
            "name": "test_transform",
            "type": "test_transform",
            "label": "Transform",
            "description": "Transforms data for testing",
            "icon": "transform",
            "color": "#2ecc71",
            "category": "test",
            "is_system": 1,
            "is_enabled": 1,
            "inputs": json.dumps([
                {
                    "name": "transform_type",
                    "label": "Transform Type",
                    "type": "select",
                    "options": [
                        "uppercase", "lowercase", "capitalize", "reverse", "length",
                        "to_json", "from_json", "increment", "decrement", "double", "half"
                    ],
                    "default": "uppercase"
                },
                {
                    "name": "value",
                    "label": "Default Value",
                    "type": "string",
                    "default": ""
                }
            ]),
            "outputs": json.dumps([
                {
                    "name": "result",
                    "label": "Result",
                    "type": "any"
                },
                {
                    "name": "transform_type",
                    "label": "Transform Type",
                    "type": "string"
                }
            ])
        }
    ]
    
    # Create test node types
    for node_type in test_node_types:
        if not frappe.db.exists("Automesh Node Type", node_type["name"]):
            doc = frappe.new_doc("Automesh Node Type")
            for key, value in node_type.items():
                doc.set(key, value)
            doc.insert()
            print(f"Created test node type: {node_type['name']}")
        else:
            # Update existing node type
            doc = frappe.get_doc("Automesh Node Type", node_type["name"])
            for key, value in node_type.items():
                doc.set(key, value)
            doc.save()
            print(f"Updated test node type: {node_type['name']}")

# Function to create a test workflow
def create_test_workflow():
    """Create a test workflow"""
    workflow_name = "test_workflow"
    
    if frappe.db.exists("Automesh Workflow", workflow_name):
        print(f"Test workflow already exists: {workflow_name}")
        return
    
    # Create a simple test workflow
    workflow = frappe.new_doc("Automesh Workflow")
    workflow.name = workflow_name
    workflow.title = "Test Workflow"
    workflow.description = "A simple test workflow"
    workflow.version = "1.0.0"
    workflow.is_active = 1
    workflow.tags = "test,demo"
    workflow.created_at = datetime.now().isoformat()
    workflow.updated_at = datetime.now().isoformat()
    
    # Define workflow JSON
    workflow_json = {
        "nodes": [
            {
                "id": "start1",
                "type": "start",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Start",
                    "params": {}
                }
            },
            {
                "id": "echo1",
                "type": "test_echo",
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "Echo Test",
                    "params": {
                        "message": "Hello from Automesh Test Workflow!"
                    }
                }
            },
            {
                "id": "random1",
                "type": "test_random",
                "position": {"x": 500, "y": 100},
                "data": {
                    "label": "Random Number",
                    "params": {
                        "data_type": "number",
                        "min_value": 1,
                        "max_value": 100
                    }
                }
            },
            {
                "id": "math1",
                "type": "test_math",
                "position": {"x": 700, "y": 100},
                "data": {
                    "label": "Double It",
                    "params": {
                        "operation": "multiply",
                        "operand1": 0,
                        "operand2": 2
                    }
                }
            },
            {
                "id": "transform1",
                "type": "test_transform",
                "position": {"x": 900, "y": 100},
                "data": {
                    "label": "Convert to JSON",
                    "params": {
                        "transform_type": "to_json"
                    }
                }
            },
            {
                "id": "end1",
                "type": "end",
                "position": {"x": 1100, "y": 100},
                "data": {
                    "label": "End",
                    "params": {}
                }
            }
        ],
        "edges": [
            {
                "id": "e1-2",
                "source": "start1",
                "target": "echo1",
                "type": "default"
            },
            {
                "id": "e2-3",
                "source": "echo1",
                "target": "random1",
                "type": "default"
            },
            {
                "id": "e3-4",
                "source": "random1",
                "target": "math1",
                "type": "default"
            },
            {
                "id": "e4-5",
                "source": "math1",
                "target": "transform1",
                "type": "default"
            },
            {
                "id": "e5-6",
                "source": "transform1",
                "target": "end1",
                "type": "default"
            }
        ]
    }
    
    workflow.workflow_json = json.dumps(workflow_json)
    
    # Add a few test variables
    workflow.append("variables", {
        "key": "test_string",
        "value": "This is a test string",
        "datatype": "string",
        "is_secret": 0
    })
    
    workflow.append("variables", {
        "key": "test_number",
        "value": "42",
        "datatype": "number",
        "is_secret": 0
    })
    
    workflow.append("variables", {
        "key": "api_key",
        "value": "fake_api_key_for_testing",
        "datatype": "string",
        "is_secret": 1
    })
    
    # Save the workflow
    workflow.insert()
    print(f"Created test workflow: {workflow_name}")

# Main function to set up all test components
def setup_test_components():
    """Set up all test components"""
    create_test_node_types()
    create_test_workflow()
    print("Test components setup complete")

if __name__ == "__main__":
    setup_test_components()
