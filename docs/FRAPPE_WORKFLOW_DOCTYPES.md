# Setting Up Frappe DocTypes for Automesh Workflow System

This guide provides instructions for setting up the required Frappe DocTypes for the Automesh Workflow System. These DocTypes form the foundation of the workflow engine and need to be created manually in the Frappe framework.

## Overview

**Important Note:** The naming convention used in this document avoids conflicts with Frappe's built-in DocTypes such as 'Workflow'. All DocTypes are prefixed with 'Automesh' to ensure they are distinct from standard Frappe DocTypes.

## General Steps to Create DocTypes in Frappe

1. Log into your Frappe instance as Administrator
2. Navigate to **Developer** > **DocType** in the sidebar
3. Click **New** to create a new DocType
4. Fill in the details as specified for each DocType
5. Click **Save** to create the DocType
6. Repeat for all the DocTypes listed below

> **Important Note About Reserved Fields**: Frappe has several reserved fields that are automatically created by the system:
>
> - The `name` field is a special reserved field that acts as the primary key. The actual value is determined by the Naming Rule you select.
> - The `modified_by` field tracks the user who last modified the document.
> - Other standard fields include `owner`, `creation`, `modified`, and `docstatus`.
>
> These fields should not be manually added when creating DocTypes as they are handled by the Frappe framework.

## Naming Rule Options

When configuring DocTypes in Frappe, the following naming rule options are available:

| Naming Rule | Description | Used By |
|-------------|-------------|----------|
| Set by user | User manually enters the document name | - |
| Autoincrement | Auto-increments a number for each new document | - |
| By fieldname | Uses value from a specific field (e.g., `field:title`) | Automesh Workflow, Automesh Node Type, Automesh Template |
| By "Naming Series" field | Uses a naming series field for sequential naming | - |
| Expression | Uses a formatted expression (e.g., `AMWF-{workflow}-{#####}`) | Automesh Execution, Automesh Node Execution |
| Expression (old style) | Legacy format for expressions | - |
| Random | Generates a random name | - |
| UUID | Generates a Universally Unique Identifier | - |
| By script | Uses a custom script to generate the name | - |
| hash | Generates a hash-based name | Automesh Variable, Automesh Connection |

## DocType Creation Process

### Step 1: Create the Basic DocTypes

#### 1. Automesh Workflow

1. Go to **DocType List** and click on **New**.
2. Enter the following basic information:
   - **DocType Name**: `Automesh Workflow`
   - **Module**: `Automesh`

#### DocType Configuration:
- **Type**: Document (Standard)
- **Module**: Automesh
- **Quick Entry**: No
- **Track Changes**: Yes
- **Track Views**: Yes
- **Is Submittable**: No
- **Engine**: InnoDB
- **Custom?**: No

#### Field Structure

| Field Name | Field Type | Options | Required | Description | Default |
|------------|------------|---------|----------|-------------|--------|
| title | Data | | **Yes** | Title of the workflow | None |
| description | Text Editor | | No | Detailed description | None |
| version | Data | | No | Version number | "1.0.0" |
| is_active | Check | | No | Whether workflow is active | 0 (Unchecked) |
| tags | Small Text | | No | Tags for categorization | None |
| created_at | DateTime | | No | Creation timestamp | Current timestamp |
| updated_at | DateTime | | No | Last update timestamp | Current timestamp |
| last_executed_at | DateTime | | No | Last execution timestamp | None |
| execution_count | Int | | No | Number of executions | 0 |
| workflow_json | Code (JSON) | | **Yes** | Complete workflow data including nodes and edges | None |
| created_by | Link | User | Auto | User who created the workflow | Current user |

#### Features:
- `autoname`: "field:title"
- `track_changes`: 1
- `track_views`: 1
- `search_fields`: "title, description, tags"
- `allow_rename`: 1
- `allow_import`: 1
- `allow_export`: 1

#### Indexes:
- `workflow_idx_title`: Column - `title`
- `workflow_idx_is_active`: Column - `is_active`
- `workflow_idx_tags`: Column - `tags`

#### Permission Levels:
- **Level 0**: All standard permissions for System Manager, Workflow Admin
- **Level 1**: Read, Write permissions for Workflow User
- **Level 2**: Read permissions for all

#### Technical Notes:
- The `workflow_json` field stores the complete JSON representation of the workflow, including nodes and edges
- Maximum size for `workflow_json` should be set appropriately (recommending at least 10MB)
- Consider implementing JSON compression for very large workflows
- The `version` field should be used for change tracking and API compatibility

### 2. Automesh Node Type

1. Go to **DocType List** and click on **New**.
2. Enter the following basic information:
   - **DocType Name**: `Automesh Node Type`
   - **Module**: `Automesh`

#### DocType Configuration:
- **Type**: Document (Standard)
- **Module**: Automesh
- **Quick Entry**: Yes
- **Track Changes**: Yes
- **Track Views**: No
- **Is Submittable**: No
- **Engine**: InnoDB
- **Custom?**: No

#### Field Structure

| Field Name | Field Type | Options | Required | Description | Default |
|------------|------------|---------|----------|-------------|--------|
| type | Data | | **Yes** | Unique node type identifier | None |
| label | Data | | **Yes** | Human-readable label | None |
| description | Text | | No | Detailed description | None |
| icon | Data | | No | Icon for UI representation | None |
| color | Data | | No | Color code for UI | None |
| category | Select | automation<br>content<br>communication<br>integration | No | Node category | None |
| inputs | Small Text | | No | Input specifications in JSON format | None |
| outputs | Small Text | | No | Output specifications in JSON format | None |
| is_system | Check | | No | Whether it's a system node type | 1 (Checked) |
| is_enabled | Check | | No | Whether the node type is enabled | 1 (Checked) |
| handler_module | Data | | No | Python module path for the handler | None |
| handler_function | Data | | No | Python function name for handler | None |
| schema_json | Code (JSON) | | No | JSON schema for node parameters | None |
| created_by | Link | User | Auto | User who created the node type | Current user |

#### Features:
- `autoname`: "field:type"
- `track_changes`: 1
- `search_fields`: "type, label, description, category"
- `allow_rename`: 0
- `allow_import`: 1
- `allow_export`: 1

#### Indexes:
- `node_type_idx_type`: Column - `type` (unique)
- `node_type_idx_category`: Column - `category`
- `node_type_idx_is_enabled`: Column - `is_enabled`

#### Permission Levels:
- **Level 0**: All standard permissions for System Manager, Developer
- **Level 1**: Read, Write permissions for Workflow Admin
- **Level 2**: Read permissions for Workflow User

#### Technical Notes:
- Node types are foundational to the workflow system and should be created by administrators/developers
- The `schema_json` field defines the parameter schema for the node in JSON Schema format
- The `handler_module` and `handler_function` fields point to Python code that executes the node's logic
- `inputs` and `outputs` fields should be JSON arrays defining the expected inputs/outputs

### 3. Automesh Execution

1. Go to **DocType List** and click on **New**.
2. Enter the following basic information:
   - **DocType Name**: `Automesh Execution`
   - **Module**: `Automesh`

#### DocType Configuration:
- **Type**: Document (Transactional)
- **Module**: Automesh
- **Quick Entry**: No
- **Track Changes**: Yes
- **Track Views**: Yes
- **Is Submittable**: No
- **Engine**: InnoDB
- **Custom?**: No

#### Field Structure

| Field Name | Field Type | Options | Required | Description | Default |
|------------|------------|---------|----------|-------------|--------|
| workflow | Link | Automesh Workflow | **Yes** | Reference to the workflow being executed | None |
| status | Select | draft<br>queued<br>running<br>completed<br>failed<br>paused<br>cancelled | No | Current execution status | "draft" |
| start_time | DateTime | | No | When execution started | None |
| end_time | DateTime | | No | When execution completed | None |
| input_data | Code (JSON) | | No | Input data for the workflow | None |
| output_data | Code (JSON) | | No | Final output from the workflow | None |
| execution_data | Code (JSON) | | No | Stores intermediate execution data | None |
| error_message | Long Text | | No | Error details if execution failed | None |
| created_by | Link | User | Auto | User who initiated the execution | Current user |

#### Features:
- `autoname`: "format:AMWF-{workflow}-{#####}"
- `track_changes`: 1
- `track_views`: 1
- `search_fields`: "workflow, status"
- `allow_rename`: 0
- `allow_import`: 0
- `allow_export`: 1

#### Indexes:
- `execution_idx_workflow`: Column - `workflow`
- `execution_idx_status`: Column - `status`
- `execution_idx_start_time`: Column - `start_time`
- `execution_idx_end_time`: Column - `end_time`

#### Permission Levels:
- **Level 0**: All standard permissions for System Manager, Workflow Admin
- **Level 1**: Read, Create, Write permissions for Workflow User
- **Level 2**: Read permissions for specified roles

#### Technical Notes:
- Each execution record captures a single run of a workflow
- Designed for high-volume transaction processing
- `execution_data` stores the input, intermediate, and output data for the workflow
- Consider implementing a data retention policy for execution records
- Long-running executions should be handled asynchronously using background workers

### 4. Automesh Node Execution

1. Go to **DocType List** and click on **New**.
2. Enter the following basic information:
   - **DocType Name**: `Automesh Node Execution`
   - **Module**: `Automesh`
   - Check **Is Child Table**

#### DocType Configuration:
- **Type**: Document (Child Table)
- **Module**: Automesh
- **Istable**: Yes
- **Parent DocType**: Automesh Execution
- **Track Changes**: Yes
- **Engine**: InnoDB
- **Custom?**: No

#### Field Structure

| Field Name | Field Type | Options | Required | Description | Default |
|------------|------------|---------|----------|-------------|--------|
| workflow_execution | Link | Automesh Execution | **Yes** | Reference to the parent execution | None |
| node_id | Data | | **Yes** | Unique node identifier in the workflow | None |
| node_type | Link | Automesh Node Type | **Yes** | Type of node being executed | None |
| status | Select | pending<br>queued<br>running<br>completed<br>error | No | Current node execution status | "pending" |
| start_time | DateTime | | No | When node execution started | None |
| end_time | DateTime | | No | When node execution completed | None |
| input_data | Code (JSON) | | No | Input data for the node | None |
| output_data | Code (JSON) | | No | Output data from the node | None |
| error_message | Long Text | | No | Error details if node execution failed | None |
| created_by | Link | User | Auto | User who initiated the node execution | Current user |

#### Features:
- `autoname`: "format:AMNE-{workflow_execution}-{node_id}"
- `track_changes`: 1
- `search_fields`: "workflow_execution, node_id, node_type, status"
- `allow_rename`: 0
- `allow_import`: 0
- `allow_export`: 1

#### Indexes:
- `node_exec_idx_workflow_execution`: Column - `workflow_execution`
- `node_exec_idx_node_id`: Column - `node_id`
- `node_exec_idx_status`: Column - `status`
- `node_exec_idx_node_type`: Column - `node_type`

#### Permission Levels:
- Inherits permissions from parent (Automesh Execution)

#### Technical Notes:
- Linked to parent Automesh Execution via `workflow_execution` field
- Each record represents the execution of a single node within a workflow
- The combination of `workflow_execution` and `node_id` must be unique
- `input_data` and `output_data` store JSON data flowing into and out of the node
- Consider using JSON compression for large data payloads
- Error handling is critical - detailed error information should be captured

### 5. Automesh Template

1. Go to **DocType List** and click on **New**.
2. Enter the following basic information:
   - **DocType Name**: `Automesh Template`
   - **Module**: `Automesh`

#### DocType Configuration:
- **Type**: Document (Master)
- **Module**: Automesh
- **Quick Entry**: No
- **Track Changes**: Yes
- **Track Views**: Yes
- **Is Submittable**: No
- **Engine**: InnoDB
- **Custom?**: No

#### Field Structure

| Field Name | Field Type | Options | Required | Description | Default |
|------------|------------|---------|----------|-------------|--------|
| title | Data | | **Yes** | Template title | None |
| description | Text Editor | | No | Detailed description | None |
| category | Select | automation<br>content<br>communication<br>integration | No | Template category | None |
| tags | Small Text | | No | Tags for categorization | None |
| version | Data | | No | Template version | "1.0.0" |
| is_featured | Check | | No | Whether template is featured | 0 (Unchecked) |
| template_json | Code (JSON) | | **Yes** | Complete template definition | None |
| created_by | Link | User | Auto | User who created the template | Current user |

#### Features:
- `autoname`: "field:title"
- `track_changes`: 1
- `search_fields`: "title, description, category, tags"
- `allow_rename`: 1
- `allow_import`: 1
- `allow_export`: 1

#### Indexes:
- `template_idx_title`: Column - `title`
- `template_idx_category`: Column - `category`
- `template_idx_tags`: Column - `tags`
- `template_idx_is_featured`: Column - `is_featured`

#### Permission Levels:
- **Level 0**: All standard permissions for System Manager, Workflow Admin
- **Level 1**: Read, Write permissions for Template Creator
- **Level 2**: Read permissions for Workflow User

#### Technical Notes:
- Templates provide reusable workflow patterns that users can quickly adapt
- The `template_json` field contains a complete workflow definition minus the execution details
- Templates can include variables that are filled in when a workflow is created from the template
- Consider implementing a categorization and tagging system for easier template discovery
- Featured templates should be reviewed for quality and usefulness

## API Implementation

After creating the DocTypes, implement the following API endpoints to interact with the workflow system.

### Automesh Workflow API Endpoints

#### Create a new workflow:
- Route: `POST /api/method/automesh.api.automesh_workflow.create_workflow`
- Parameters: `title, description, workflow_json`

#### Get workflow:
- Route: `GET /api/method/automesh.api.automesh_workflow.get_workflow`
- Parameters: `name`

#### Update workflow:
- Route: `PUT /api/method/automesh.api.automesh_workflow.update_workflow`
- Parameters: `name, title, description, workflow_json, is_active`

#### List workflows:
- Route: `GET /api/method/automesh.api.automesh_workflow.list_workflows`
- Parameters: `filters, page, page_length`

#### Delete workflow:
- Route: `DELETE /api/method/automesh.api.automesh_workflow.delete_workflow`
- Parameters: `name`

### Automesh Execution API Endpoints

#### Execute workflow:
- Route: `POST /api/method/automesh.api.automesh_workflow.execute_workflow`
- Parameters: `workflow_name, input_data`

#### Get execution status:
- Route: `GET /api/method/automesh.api.automesh_workflow.get_execution_status`
- Parameters: `execution_name`

#### Pause execution:
- Route: `PUT /api/method/automesh.api.automesh_workflow.pause_execution`
- Parameters: `execution_name`

#### Resume execution:
- Route: `PUT /api/method/automesh.api.automesh_workflow.resume_execution`
- Parameters: `execution_name`

#### Cancel execution:
- Route: `PUT /api/method/automesh.api.automesh_workflow.cancel_execution`
- Parameters: `execution_name`

## Technical Considerations

When implementing the Automesh workflow system, consider the following technical aspects for optimal performance and security.

### Database Considerations
- All DocTypes use InnoDB engine for transaction support
- JSON fields use LONGTEXT type in MySQL/MariaDB
- Appropriate indexes are created for frequent query patterns
- Consider setting up table partitioning for execution logs if high volume is expected

### Server-side Processing
- All node execution should happen asynchronously using background workers
- Consider implementing a queuing system for high-volume workflow processing
- Rate limiting should be implemented for external API calls
- Implement caching for frequently accessed workflow templates and node types

### Security Considerations
- Implement proper input validation for all API endpoints
- Secret variables should be encrypted at rest
- Implement appropriate access controls through permission system
- Consider adding field-level permissions for sensitive fields
- Add request throttling to prevent abuse

### Performance Optimization
- Large workflows should be paginated in the UI
- Consider using read replicas for reporting purposes
- Implement efficient logging with rotation policies
- Execution data should be cleaned up according to a retention policy
- Implement metrics collection for system monitoring


### 6. Automesh Variable

1. Go to **DocType List** and click on **New**.
2. Enter the following basic information:
   - **DocType Name**: `Automesh Variable`
   - **Module**: `Automesh`
   - Check **Is Child Table**

#### DocType Configuration:
- **Type**: Document (Child Table)
- **Module**: Automesh
- **Istable**: Yes
- **Parent DocType**: Automesh Workflow
- **Engine**: InnoDB
- **Custom?**: No

#### Field Structure

| Field Name | Field Type | Options | Required | Description | Default |
|------------|------------|---------|----------|-------------|--------|
| parent | Link | Automesh Workflow | Auto | Parent workflow | None |
| parenttype | Data | | Auto | Parent DocType | "Automesh Workflow" |
| parentfield | Data | | Auto | Parent field name | "variables" |
| key | Data | | **Yes** | Variable name (must be unique) | None |
| value | Data | | No | Variable value | None |
| datatype | Select | string<br>number<br>boolean<br>object<br>array | No | Data type of the variable | "string" |
| is_secret | Check | | No | Whether the variable contains sensitive data | 0 (Unchecked) |

#### Features:
- `autoname`: "hash"
- `istable`: 1

#### Technical Notes:
- Used to store variables that can be referenced throughout the workflow
- Secret variables should be encrypted in the database
- Variables can be referenced in node parameters using a templating syntax like `{{variables.varName}}`
- Provides flexibility for workflow parameterization and reuse

### 7. Automesh Connection

1. Go to **DocType List** and click on **New**.
2. Enter the following basic information:
   - **DocType Name**: `Automesh Connection`
   - **Module**: `Automesh`
   - Check **Is Child Table**

#### DocType Configuration:
- **Type**: Document (Child Table)
- **Module**: Automesh
- **Istable**: Yes
- **Parent DocType**: Automesh Workflow
- **Track Changes**: Yes
- **Engine**: InnoDB
- **Custom?**: No

#### Field Structure

| Field Name | Field Type | Options | Required | Description | Default |
|------------|------------|---------|----------|-------------|--------|
| parent | Link | Automesh Workflow | Auto | Parent workflow | None |
| parenttype | Data | | Auto | Parent DocType | "Automesh Workflow" |
| parentfield | Data | | Auto | Parent field name | "connections" |
| source_node_id | Data | | **Yes** | ID of the source node | None |
| target_node_id | Data | | **Yes** | ID of the target node | None |
| source_handle | Data | | No | Source connection point | None |
| target_handle | Data | | No | Target connection point | None |
| label | Data | | No | Connection label | None |
| condition_json | Code (JSON) | | No | Conditions for edge traversal | None |
| transformation_json | Code (JSON) | | No | Data transformations for the connection | None |

#### Features:
- `autoname`: "hash"
- `istable`: 1

#### Technical Notes:
- Stores connection information between nodes outside of the main workflow JSON
- Useful for analytics and optimizing workflow execution
- Conditions determine whether execution flows through this connection
- Transformations modify the data as it passes through the connection

## Implementation Steps

After creating all the DocTypes, follow these steps to implement the workflow system:

1. Create the corresponding API methods in the `automesh.api.automesh_workflow` module
2. For each node type, implement a handler function in the appropriate module
3. Develop the workflow execution engine as a Python module that can process workflow JSON and execute each node
4. Configure permissions to control who can create, view, and execute workflows

## Data Migration Approach

If you have existing workflow data that needs to be migrated:

1. Export the existing data to JSON format
2. Write a migration script to convert the data to the new DocType format
3. Use the Frappe Data Import tool to import the converted data

## Code Examples

### Example Node Handler

The following code demonstrates how to implement a node handler for the workflow system:

```python
# File: automesh/workflow_handlers/content_handlers.py

def handle_seo_writer(node_execution, input_data):
    """
    Handler for the SEO Writer node.
    
    Args:
        node_execution: The Automesh Node Execution doc
        input_data: Input data for the node
        
    Returns:
        dict: Output data from the node
    """
    try:
        # Get parameters from the node
        parameters = json.loads(node_execution.parameters)
        keywords = parameters.get('keywords', '')
        content_length = parameters.get('contentLength', 'medium')
        
        # Process the data (example)
        # In a real implementation, this would call an AI service or other content generator
        output = generate_seo_content(keywords, content_length)
        
        # Update the node execution
        frappe.db.set_value('Automesh Node Execution', node_execution.name, {
            'status': 'success',
            'end_time': now(),
            'output_data': json.dumps(output)
        })
        
        return output
        
    except Exception as e:
        # Handle errors
        error_message = str(e)
        frappe.db.set_value('Automesh Node Execution', node_execution.name, {
            'status': 'error',
            'end_time': now(),
            'error_message': error_message
        })
        frappe.log_error(error_message, "Automesh Node Execution Error")
        
        raise
```

## Conclusion

By following this guide, you should be able to successfully set up all the required DocTypes for the Automesh Workflow System in Frappe. After creating these DocTypes, you can then implement the API methods and handlers to build a complete workflow automation solution.

If you encounter any issues during the implementation, refer to the Frappe documentation or seek assistance from the Automesh development team.
