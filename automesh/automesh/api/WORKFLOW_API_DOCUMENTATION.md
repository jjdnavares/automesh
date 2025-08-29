# Automesh Workflow API Documentation

This document provides detailed information about the Workflow API endpoints available in the Automesh application. These endpoints facilitate the creation, management, execution, and monitoring of workflows.

## Base URL

All API endpoints are relative to your Frappe instance base URL, typically:

```
https://yourdomain.com/api/method/automesh.automesh.api.workflow.[endpoint]
```

## Authentication

All API calls require authentication. Make sure to include the appropriate session token in your requests.

## Response Format

API responses follow the standard Frappe format:

```json
{
  "message": [Response Data],
  "exc": [Exception if any]
}
```

For successful requests, the response data will be in the `message` field. For errors, check the `exc` field.

## Endpoints

### Workflow Management

#### Get Workflows

Retrieves all workflows accessible to the current user.

- **Endpoint**: `get_workflows`
- **Method**: GET
- **Response**: List of workflows with their nodes and edges

Example response:
```json
[
  {
    "id": "WORKFLOW001",
    "name": "Customer Onboarding",
    "description": "New customer welcome sequence",
    "nodes": [...],
    "edges": [...],
    "metadata": {
      "createdAt": "2025-08-25T10:00:00Z",
      "updatedAt": "2025-08-27T15:30:00Z",
      "executionCount": 12,
      "isActive": true
    }
  }
]
```

#### Get Workflow

Retrieves a specific workflow by its ID.

- **Endpoint**: `get_workflow`
- **Method**: GET
- **Parameters**:
  - `workflow_id`: ID of the workflow to retrieve
- **Response**: Complete workflow object including nodes and edges

#### Create Workflow

Creates a new workflow.

- **Endpoint**: `create_workflow`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "name": "New Workflow",
    "description": "Description of the workflow",
    "nodes": [...],
    "edges": [...]
  }
  ```
- **Response**: The newly created workflow

#### Update Workflow

Updates an existing workflow.

- **Endpoint**: `update_workflow`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "workflow_id": "WORKFLOW001",
    "workflow": {
      "name": "Updated Workflow Name",
      "description": "Updated description",
      "nodes": [...],
      "edges": [...],
      "metadata": {
        "isActive": true
      }
    }
  }
  ```
- **Response**: The updated workflow

#### Delete Workflow

Deletes a workflow.

- **Endpoint**: `delete_workflow`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "workflow_id": "WORKFLOW001"
  }
  ```
- **Response**: Success confirmation

### Workflow Execution

#### Execute Workflow

Starts the execution of a workflow.

- **Endpoint**: `execute_workflow`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "workflow_id": "WORKFLOW001",
    "input_data": {
      "param1": "value1",
      "param2": "value2"
    }
  }
  ```
- **Response**: Execution ID for tracking

Example response:
```json
{
  "execution_id": "EXECUTION001"
}
```

#### Stop Workflow Execution

Stops an ongoing workflow execution.

- **Endpoint**: `stop_workflow_execution`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "execution_id": "EXECUTION001"
  }
  ```
- **Response**: Success confirmation

#### Get Execution Status

Retrieves the status of a workflow execution.

- **Endpoint**: `get_execution_status`
- **Method**: GET
- **Parameters**:
  - `execution_id`: ID of the execution to check
- **Response**: Execution status with node statuses

Example response:
```json
{
  "id": "EXECUTION001",
  "workflowId": "WORKFLOW001",
  "status": "running",
  "startTime": "2025-08-28T10:00:00Z",
  "endTime": null,
  "nodes": {
    "node1": {
      "status": "completed",
      "message": null,
      "startTime": "2025-08-28T10:00:05Z",
      "endTime": "2025-08-28T10:00:15Z"
    },
    "node2": {
      "status": "running",
      "message": null,
      "startTime": "2025-08-28T10:00:20Z",
      "endTime": null
    }
  },
  "output": {}
}
```

### Node Types

#### Get Node Types

Retrieves all available node types.

- **Endpoint**: `get_node_types`
- **Method**: GET
- **Response**: List of available node types

Example response:
```json
[
  {
    "id": "HTTP_REQUEST",
    "type": "httpRequest",
    "category": "Integration",
    "description": "Makes an HTTP request to an external API",
    "icon": "🌐",
    "color": "#6366F1",
    "inputs": [
      { "id": "input", "label": "Input" }
    ],
    "outputs": [
      { "id": "success", "label": "Success" },
      { "id": "error", "label": "Error" }
    ],
    "paramsSchema": {
      "url": {
        "type": "string",
        "label": "URL",
        "required": true
      },
      "method": {
        "type": "select",
        "label": "Method",
        "options": ["GET", "POST", "PUT", "DELETE"],
        "default": "GET"
      },
      "headers": {
        "type": "json",
        "label": "Headers"
      }
    }
  }
]
```

### Templates

#### Get Workflow Templates

Retrieves all available workflow templates.

- **Endpoint**: `get_workflow_templates`
- **Method**: GET
- **Response**: List of available templates

#### Create From Template

Creates a new workflow from a template.

- **Endpoint**: `create_from_template`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "template_id": "TEMPLATE001",
    "name": "My New Workflow"
  }
  ```
- **Response**: The newly created workflow

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 400: Bad request (invalid parameters)
- 403: Forbidden (insufficient permissions)
- 404: Not found
- 500: Server error

Error responses include an explanation in the `exc` field:
```json
{
  "exc": "Workflow ID is required"
}
```

## Testing API Endpoints

You can test these API endpoints using tools like cURL, Postman, or the browser console. For example:

```bash
curl -X GET "https://yourdomain.com/api/method/automesh.automesh.api.workflow.get_workflows" \
  -H "Content-Type: application/json" \
  --cookie "sid=your-session-id"
```

## Integrating with Frontend

The frontend workflow components are designed to work seamlessly with these API endpoints. For example:

```typescript
import { workflowApi } from '../../services/workflow/workflowApi';

// Example: Load all workflows
const loadWorkflows = async () => {
  try {
    const workflows = await workflowApi.getWorkflows();
    console.log(workflows);
  } catch (error) {
    console.error('Failed to load workflows:', error);
  }
};
```

## Permissions

API access depends on user permissions:
- System Managers can access all workflows
- Regular users can only access workflows they own
- Only System Managers can delete workflows

## Rate Limiting

To prevent abuse, the API implements rate limiting. If you exceed the limits, you'll receive a 429 (Too Many Requests) status code.

---

For additional support or feature requests, please contact the Automesh development team.
