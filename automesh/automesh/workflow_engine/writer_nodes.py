"""
Writer App Integration Nodes for AutoMesh Workflows

This module provides workflow nodes that integrate with the Writer app's
LLM capabilities for content generation.

Author: AutoMesh Team
Created: 2025-10-01
"""

import frappe
from frappe import _
from typing import Dict, Any
from .node_handlers import NodeHandlerRegistry, BaseNodeHandler


@NodeHandlerRegistry.register("writer_generate_content")
class WriterGenerateContentNodeHandler(BaseNodeHandler):
    """
    Generate content using Writer app's LLM providers.
    
    This node leverages the Writer app's multi-provider LLM support to generate
    various types of content (blog posts, articles, product descriptions, etc.)
    with customizable tone and style.
    
    Features:
    - Supports 11+ LLM providers (OpenAI, Anthropic, Google, Groq, etc.)
    - Multiple content types with optimized prompts
    - Automatic content humanization (two-pass generation)
    - Saves generated content to database for tracking
    """
    
    def execute(self) -> Dict[str, Any]:
        """Execute the content generation node"""
        
        # Get parameters from node configuration
        keyword = self.get_param("keyword", "")
        content_type = self.get_param("content_type", "Blog Post")
        tone = self.get_param("tone", "Professional")
        provider = self.get_param("provider", "openai")
        model = self.get_param("model", "gpt-4")
        
        # Validate required parameters
        if not keyword:
            self.log_error("Keyword is required for content generation")
            return {
                "success": False,
                "error": "Keyword parameter is required"
            }
        
        if not provider:
            self.log_error("LLM provider is required")
            return {
                "success": False,
                "error": "Provider parameter is required"
            }
        
        if not model:
            self.log_error("Model name is required")
            return {
                "success": False,
                "error": "Model parameter is required"
            }
        
        try:
            self.log_info(f"Generating {content_type} content for keyword: '{keyword}'")
            self.log_info(f"Using provider: {provider}, model: {model}, tone: {tone}")
            
            # Check if Writer app is installed
            if not frappe.db.exists("DocType", "Generated Content"):
                self.log_error("Writer app is not installed or Generated Content DocType not found")
                return {
                    "success": False,
                    "error": "Writer app is not installed. Please install the Writer app first."
                }
            
            # Call Writer's generate_content API
            # This API handles:
            # 1. Prompt template selection
            # 2. Initial content generation
            # 3. Content humanization (second pass)
            # 4. Saving to database
            result = frappe.call(
                "writer.api.generate_content",
                keyword=keyword,
                content_type=content_type,
                tone=tone,
                provider=provider,
                model=model
            )
            
            # Extract data from the result
            output_data = {
                "generated_text": result.get("generated_text", ""),
                "title": result.get("title", ""),
                "doc_name": result.get("name", ""),
                "prompt_used": result.get("prompt", ""),
                "keyword": keyword,
                "content_type": content_type,
                "tone": tone,
                "provider": provider,
                "model": model,
                "creation": result.get("creation", "")
            }
            
            # Set output for downstream nodes
            self.set_output(output_data)
            
            self.log_info(f"Content generated successfully: {output_data['title']}")
            self.log_info(f"Saved as document: {output_data['doc_name']}")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except frappe.ValidationError as e:
            # Handle validation errors (e.g., missing API key, invalid content type)
            error_msg = str(e)
            self.log_error(f"Validation error: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg
            }
            
        except frappe.PermissionError as e:
            # Handle permission errors
            error_msg = "Permission denied. You may not have access to the Writer app."
            self.log_error(error_msg)
            
            return {
                "success": False,
                "error": error_msg
            }
            
        except Exception as e:
            # Handle any other unexpected errors
            error_msg = f"Error generating content: {str(e)}"
            self.log_error(error_msg)
            frappe.log_error(frappe.get_traceback(), "Writer Node Execution Error")
            
            return {
                "success": False,
                "error": error_msg
            }


@NodeHandlerRegistry.register("writer_custom_prompt")
class WriterCustomPromptNodeHandler(BaseNodeHandler):
    """
    Generate content with a custom prompt using Writer's LLM integration.
    
    This node provides direct access to LLM providers without using predefined
    templates, allowing for maximum flexibility in content generation.
    
    Use cases:
    - Custom content generation tasks
    - Specialized prompts not covered by templates
    - Direct LLM interaction for specific use cases
    """
    
    def execute(self) -> Dict[str, Any]:
        """Execute the custom prompt node"""
        
        # Get parameters
        prompt = self.get_param("prompt", "")
        provider = self.get_param("provider", "openai")
        model = self.get_param("model", "gpt-4")
        
        # Get input data from connected nodes if available
        incoming_connections = self.execution_context.get_incoming_connections(self.node_id)
        
        if incoming_connections:
            source_node_id = incoming_connections[0].get("source")
            input_data = self.execution_context.get_node_output(source_node_id) or {}
            
            # If prompt contains placeholders, try to fill them with input data
            if isinstance(input_data, dict) and "{" in prompt and "}" in prompt:
                try:
                    prompt = prompt.format(**input_data)
                    self.log_info("Prompt populated with input data")
                except KeyError as e:
                    self.log_error(f"Missing placeholder in input data: {str(e)}")
        
        # Validate required parameters
        if not prompt:
            self.log_error("Prompt is required")
            return {
                "success": False,
                "error": "Prompt parameter is required"
            }
        
        if not provider:
            self.log_error("LLM provider is required")
            return {
                "success": False,
                "error": "Provider parameter is required"
            }
        
        if not model:
            self.log_error("Model name is required")
            return {
                "success": False,
                "error": "Model parameter is required"
            }
        
        try:
            self.log_info(f"Calling {provider} ({model}) with custom prompt")
            self.log_debug(f"Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"Prompt: {prompt}")
            
            # Call Writer's _call_llm API directly
            generated_text = frappe.call(
                "writer.api._call_llm",
                prompt=prompt,
                provider=provider,
                model=model
            )
            
            output_data = {
                "generated_text": generated_text,
                "prompt_used": prompt,
                "provider": provider,
                "model": model
            }
            
            self.set_output(output_data)
            self.log_info("Content generated successfully")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except frappe.ValidationError as e:
            error_msg = str(e)
            self.log_error(f"Validation error: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg
            }
            
        except Exception as e:
            error_msg = f"Error generating content: {str(e)}"
            self.log_error(error_msg)
            frappe.log_error(frappe.get_traceback(), "Writer Custom Prompt Error")
            
            return {
                "success": False,
                "error": error_msg
            }


@NodeHandlerRegistry.register("writer_get_content")
class WriterGetContentNodeHandler(BaseNodeHandler):
    """
    Retrieve previously generated content from Writer app.
    
    This node allows workflows to access content that was previously generated,
    enabling content reuse, analysis, or further processing.
    
    Features:
    - Retrieve specific content by document name
    - List multiple contents with filters
    - Filter by keyword or content type
    """
    
    def execute(self) -> Dict[str, Any]:
        """Execute the get content node"""
        
        # Get parameters
        doc_name = self.get_param("doc_name")
        limit = self.get_param("limit", 10)
        keyword_filter = self.get_param("keyword_filter")
        content_type_filter = self.get_param("content_type_filter")
        
        try:
            # Check if Writer app is installed
            if not frappe.db.exists("DocType", "Generated Content"):
                self.log_error("Writer app is not installed")
                return {
                    "success": False,
                    "error": "Writer app is not installed. Please install the Writer app first."
                }
            
            if doc_name:
                # Get specific document
                self.log_info(f"Retrieving content document: {doc_name}")
                
                if not frappe.db.exists("Generated Content", doc_name):
                    self.log_error(f"Document not found: {doc_name}")
                    return {
                        "success": False,
                        "error": f"Generated Content document '{doc_name}' not found"
                    }
                
                doc = frappe.get_doc("Generated Content", doc_name)
                output_data = {
                    "contents": [doc.as_dict()],
                    "count": 1
                }
                
            else:
                # Get list with filters
                self.log_info("Retrieving content list with filters")
                
                filters = {}
                if keyword_filter:
                    filters["keyword"] = ["like", f"%{keyword_filter}%"]
                    self.log_info(f"Filtering by keyword: {keyword_filter}")
                
                if content_type_filter:
                    filters["content_type"] = content_type_filter
                    self.log_info(f"Filtering by content type: {content_type_filter}")
                
                contents = frappe.get_all(
                    "Generated Content",
                    filters=filters,
                    fields=["name", "title", "generated_text", "keyword", "tone", "content_type", "provider", "model", "creation"],
                    order_by="creation desc",
                    limit=limit
                )
                
                output_data = {
                    "contents": contents,
                    "count": len(contents)
                }
            
            self.set_output(output_data)
            self.log_info(f"Retrieved {output_data['count']} content document(s)")
            
            return {
                "success": True,
                "data": output_data
            }
            
        except frappe.PermissionError:
            error_msg = "Permission denied. You may not have access to view Generated Content."
            self.log_error(error_msg)
            
            return {
                "success": False,
                "error": error_msg
            }
            
        except Exception as e:
            error_msg = f"Error retrieving content: {str(e)}"
            self.log_error(error_msg)
            frappe.log_error(frappe.get_traceback(), "Writer Get Content Error")
            
            return {
                "success": False,
                "error": error_msg
            }
