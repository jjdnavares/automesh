"""
Setup script for Writer integration nodes

This script creates the node type definitions in the Automesh Node Type DocType
for all Writer app integration nodes.

Usage:
    bench console
    >>> from automesh.workflow_engine.setup_writer_nodes import setup_writer_nodes
    >>> setup_writer_nodes()
"""

import frappe
import json


def setup_writer_nodes():
    """Create or update Writer integration node types in the database"""
    
    writer_node_types = [
        {
            "name": "writer_generate_content",
            "type": "writer_generate_content",
            "label": "Writer: Generate Content",
            "description": "Generate content using Writer app's LLM providers (OpenAI, Anthropic, Google, etc.)",
            "icon": "file-text",
            "color": "#8b5cf6",
            "category": "content",
            "is_system": 1,
            "is_enabled": 1,
            "handler_module": "automesh.workflow_engine.writer_nodes",
            "handler_function": "WriterGenerateContentNodeHandler",
            "inputs": json.dumps([
                {
                    "name": "keyword",
                    "label": "Keyword/Topic",
                    "type": "string",
                    "description": "Main keyword or topic for content generation",
                    "required": True,
                    "default": ""
                },
                {
                    "name": "content_type",
                    "label": "Content Type",
                    "type": "select",
                    "description": "Type of content to generate",
                    "options": [
                        "Blog Post",
                        "Article",
                        "Product Description",
                        "Landing Page",
                        "SEO Meta Description",
                        "Social Media Post",
                        "Blog Outline"
                    ],
                    "default": "Blog Post",
                    "required": True
                },
                {
                    "name": "tone",
                    "label": "Tone",
                    "type": "select",
                    "description": "Tone and style of the content",
                    "options": [
                        "Professional",
                        "Casual",
                        "Friendly",
                        "Formal",
                        "Humorous",
                        "Technical"
                    ],
                    "default": "Professional",
                    "required": True
                },
                {
                    "name": "provider",
                    "label": "LLM Provider",
                    "type": "select",
                    "description": "LLM provider to use for generation",
                    "options": [
                        "openai",
                        "anthropic",
                        "google",
                        "groq",
                        "mistral",
                        "ollama",
                        "cohere",
                        "perplexity",
                        "together",
                        "amazon_bedrock",
                        "open_router"
                    ],
                    "default": "openai",
                    "required": True
                },
                {
                    "name": "model",
                    "label": "Model",
                    "type": "string",
                    "description": "Model name (e.g., gpt-4, claude-3-opus, gemini-pro)",
                    "default": "gpt-4",
                    "required": True
                }
            ]),
            "outputs": json.dumps([
                {
                    "name": "generated_text",
                    "label": "Generated Text",
                    "type": "string",
                    "description": "The generated content text"
                },
                {
                    "name": "title",
                    "label": "Title",
                    "type": "string",
                    "description": "Title of the generated content"
                },
                {
                    "name": "doc_name",
                    "label": "Document Name",
                    "type": "string",
                    "description": "Name of the saved Generated Content document"
                },
                {
                    "name": "prompt_used",
                    "label": "Prompt Used",
                    "type": "string",
                    "description": "The prompt that was used for generation"
                },
                {
                    "name": "keyword",
                    "label": "Keyword",
                    "type": "string",
                    "description": "The keyword used"
                },
                {
                    "name": "content_type",
                    "label": "Content Type",
                    "type": "string",
                    "description": "Type of content generated"
                },
                {
                    "name": "provider",
                    "label": "Provider",
                    "type": "string",
                    "description": "LLM provider used"
                },
                {
                    "name": "model",
                    "label": "Model",
                    "type": "string",
                    "description": "Model used"
                }
            ]),
            "schema_json": json.dumps({
                "type": "object",
                "properties": {
                    "keyword": {"type": "string"},
                    "content_type": {"type": "string"},
                    "tone": {"type": "string"},
                    "provider": {"type": "string"},
                    "model": {"type": "string"}
                },
                "required": ["keyword", "content_type", "tone", "provider", "model"]
            })
        },
        {
            "name": "writer_custom_prompt",
            "type": "writer_custom_prompt",
            "label": "Writer: Custom Prompt",
            "description": "Generate content with a custom prompt using Writer's LLM providers",
            "icon": "edit",
            "color": "#8b5cf6",
            "category": "content",
            "is_system": 1,
            "is_enabled": 1,
            "handler_module": "automesh.workflow_engine.writer_nodes",
            "handler_function": "WriterCustomPromptNodeHandler",
            "inputs": json.dumps([
                {
                    "name": "prompt",
                    "label": "Prompt",
                    "type": "text",
                    "description": "Custom prompt text. Use {variable} for placeholders from input data.",
                    "required": True,
                    "default": ""
                },
                {
                    "name": "provider",
                    "label": "LLM Provider",
                    "type": "select",
                    "description": "LLM provider to use",
                    "options": [
                        "openai",
                        "anthropic",
                        "google",
                        "groq",
                        "mistral",
                        "ollama",
                        "cohere",
                        "perplexity",
                        "together",
                        "amazon_bedrock",
                        "open_router"
                    ],
                    "default": "openai",
                    "required": True
                },
                {
                    "name": "model",
                    "label": "Model",
                    "type": "string",
                    "description": "Model name (e.g., gpt-4, claude-3-opus)",
                    "default": "gpt-4",
                    "required": True
                }
            ]),
            "outputs": json.dumps([
                {
                    "name": "generated_text",
                    "label": "Generated Text",
                    "type": "string",
                    "description": "The generated response"
                },
                {
                    "name": "prompt_used",
                    "label": "Prompt Used",
                    "type": "string",
                    "description": "The final prompt that was used"
                },
                {
                    "name": "provider",
                    "label": "Provider",
                    "type": "string",
                    "description": "LLM provider used"
                },
                {
                    "name": "model",
                    "label": "Model",
                    "type": "string",
                    "description": "Model used"
                }
            ]),
            "schema_json": json.dumps({
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "provider": {"type": "string"},
                    "model": {"type": "string"}
                },
                "required": ["prompt", "provider", "model"]
            })
        },
        {
            "name": "writer_get_content",
            "type": "writer_get_content",
            "label": "Writer: Get Content",
            "description": "Retrieve previously generated content from Writer app",
            "icon": "database",
            "color": "#8b5cf6",
            "category": "content",
            "is_system": 1,
            "is_enabled": 1,
            "handler_module": "automesh.workflow_engine.writer_nodes",
            "handler_function": "WriterGetContentNodeHandler",
            "inputs": json.dumps([
                {
                    "name": "doc_name",
                    "label": "Document Name",
                    "type": "string",
                    "description": "Specific document name to retrieve (optional)",
                    "required": False,
                    "default": ""
                },
                {
                    "name": "limit",
                    "label": "Limit",
                    "type": "number",
                    "description": "Maximum number of documents to retrieve",
                    "default": 10,
                    "required": False
                },
                {
                    "name": "keyword_filter",
                    "label": "Keyword Filter",
                    "type": "string",
                    "description": "Filter by keyword (partial match)",
                    "required": False,
                    "default": ""
                },
                {
                    "name": "content_type_filter",
                    "label": "Content Type Filter",
                    "type": "select",
                    "description": "Filter by content type",
                    "options": [
                        "",
                        "Blog Post",
                        "Article",
                        "Product Description",
                        "Landing Page",
                        "SEO Meta Description",
                        "Social Media Post",
                        "Blog Outline"
                    ],
                    "default": "",
                    "required": False
                }
            ]),
            "outputs": json.dumps([
                {
                    "name": "contents",
                    "label": "Contents",
                    "type": "array",
                    "description": "List of generated content documents"
                },
                {
                    "name": "count",
                    "label": "Count",
                    "type": "number",
                    "description": "Total number of documents retrieved"
                }
            ]),
            "schema_json": json.dumps({
                "type": "object",
                "properties": {
                    "doc_name": {"type": "string"},
                    "limit": {"type": "number"},
                    "keyword_filter": {"type": "string"},
                    "content_type_filter": {"type": "string"}
                }
            })
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for node_type in writer_node_types:
        try:
            if not frappe.db.exists("Automesh Node Type", node_type["name"]):
                # Create new node type
                doc = frappe.new_doc("Automesh Node Type")
                for key, value in node_type.items():
                    doc.set(key, value)
                doc.insert()
                frappe.db.commit()
                print(f"✓ Created Writer node type: {node_type['label']}")
                created_count += 1
            else:
                # Update existing node type
                doc = frappe.get_doc("Automesh Node Type", node_type["name"])
                for key, value in node_type.items():
                    if key != "name":  # Don't update the name field
                        doc.set(key, value)
                doc.save()
                frappe.db.commit()
                print(f"✓ Updated Writer node type: {node_type['label']}")
                updated_count += 1
                
        except Exception as e:
            print(f"✗ Error processing node type {node_type['name']}: {str(e)}")
            frappe.log_error(frappe.get_traceback(), f"Writer Node Setup Error - {node_type['name']}")
    
    print(f"\n{'='*60}")
    print(f"Writer Nodes Setup Complete!")
    print(f"Created: {created_count} | Updated: {updated_count}")
    print(f"{'='*60}\n")
    
    return {
        "created": created_count,
        "updated": updated_count,
        "total": len(writer_node_types)
    }


if __name__ == "__main__":
    setup_writer_nodes()
