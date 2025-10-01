# Writer App Integration - Custom Node Implementation Plan

**Project:** AutoMesh + Writer Integration
**Purpose:** Create workflow nodes that leverage Writer app's LLM capabilities
**Last Updated:** 2025-10-01

---

## 📋 Overview

The **Writer** app is a content generation tool that supports multiple LLM providers (OpenAI, Anthropic, Google, Groq, Mistral, Ollama, etc.). This document outlines the plan to create custom AutoMesh workflow nodes that integrate with Writer's functionality.

---

## 🔍 Writer App Analysis

### **Existing Capabilities**

#### **1. LLM Providers Supported (11 providers)**
- ✅ OpenAI (GPT-4, GPT-3.5)
- ✅ Anthropic (Claude)
- ✅ Google (Gemini)
- ✅ Cohere
- ✅ Groq
- ✅ Mistral
- ✅ Ollama (self-hosted)
- ✅ Perplexity
- ✅ Together AI
- ✅ Amazon Bedrock
- ✅ OpenRouter

#### **2. Content Types Supported**
- Blog Post
- Article
- Product Description
- Landing Page
- SEO Meta Description
- Social Media Post
- Blog Outline

#### **3. Key Features**
- Multi-provider LLM API abstraction
- User-level and system-level API key management
- Content humanization (two-pass generation)
- Prompt templating system
- Generated content storage (DocType: `Generated Content`)

#### **4. API Endpoints**
- `generate_content(keyword, content_type, tone, provider, model)` - Main generation
- `get_generated_contents()` - List all generated content
- `delete_content(name)` - Delete content
- `get_content_prompts()` - Get available prompts
- `set_llm_api_key(provider, api_key)` - Set API keys
- `get_llm_api_key(provider)` - Get API keys
- `_call_llm(prompt, provider, model)` - Core LLM caller

---

## 🎯 Implementation Plan

### **Phase 1: Core Writer Nodes (High Priority)**

#### **Node 1: Writer Generate Content**
**Type:** `writer_generate_content`
**Category:** AI/Content
**Description:** Generate content using Writer app's LLM providers

**Inputs:**
- `keyword` (string, required) - Main keyword/topic
- `content_type` (select, required) - Type of content to generate
  - Options: Blog Post, Article, Product Description, Landing Page, SEO Meta Description, Social Media Post, Blog Outline
- `tone` (select, required) - Tone of content
  - Options: Professional, Casual, Friendly, Formal, Humorous, Technical
- `provider` (select, required) - LLM provider
  - Options: OpenAI, Anthropic, Google, Groq, Mistral, Ollama, etc.
- `model` (string, required) - Model name (e.g., "gpt-4", "claude-3-opus")
- `save_to_db` (boolean, default: true) - Save to Generated Content DocType

**Outputs:**
- `generated_text` (string) - The generated content
- `title` (string) - Generated title
- `doc_name` (string) - Name of saved document (if saved)
- `prompt_used` (string) - The prompt that was used

**Implementation File:** `automesh/automesh/workflow_engine/writer_nodes.py`

**Handler Code:**
```python
@NodeHandlerRegistry.register("writer_generate_content")
class WriterGenerateContentNodeHandler(BaseNodeHandler):
    """Generate content using Writer app"""
    
    def execute(self):
        # Get parameters
        keyword = self.get_param("keyword", "")
        content_type = self.get_param("content_type", "Blog Post")
        tone = self.get_param("tone", "Professional")
        provider = self.get_param("provider", "openai")
        model = self.get_param("model", "gpt-4")
        save_to_db = self.get_param("save_to_db", True)
        
        if not keyword:
            self.log_error("Keyword is required")
            return {"success": False, "error": "Keyword is required"}
        
        try:
            self.log_info(f"Generating {content_type} for keyword: {keyword}")
            
            # Call Writer's generate_content API
            result = frappe.call(
                "writer.api.generate_content",
                keyword=keyword,
                content_type=content_type,
                tone=tone,
                provider=provider,
                model=model
            )
            
            output_data = {
                "generated_text": result.get("generated_text"),
                "title": result.get("title"),
                "doc_name": result.get("name") if save_to_db else None,
                "prompt_used": result.get("prompt"),
                "keyword": keyword,
                "content_type": content_type,
                "tone": tone,
                "provider": provider,
                "model": model
            }
            
            self.set_output(output_data)
            self.log_info(f"Content generated successfully")
            
            return {"success": True, "data": output_data}
            
        except Exception as e:
            self.log_error(f"Error generating content: {str(e)}")
            return {"success": False, "error": str(e)}
```

---

#### **Node 2: Writer Custom Prompt**
**Type:** `writer_custom_prompt`
**Category:** AI/Content
**Description:** Generate content with a custom prompt (no template)

**Inputs:**
- `prompt` (text, required) - Custom prompt text
- `provider` (select, required) - LLM provider
- `model` (string, required) - Model name
- `system_message` (text, optional) - System message for the LLM
- `max_tokens` (number, default: 2000) - Maximum tokens to generate
- `temperature` (number, default: 0.7) - Temperature (0-1)

**Outputs:**
- `generated_text` (string) - The generated response
- `prompt_used` (string) - The prompt that was used

**Handler Code:**
```python
@NodeHandlerRegistry.register("writer_custom_prompt")
class WriterCustomPromptNodeHandler(BaseNodeHandler):
    """Generate content with custom prompt using Writer's LLM"""
    
    def execute(self):
        prompt = self.get_param("prompt", "")
        provider = self.get_param("provider", "openai")
        model = self.get_param("model", "gpt-4")
        
        if not prompt:
            self.log_error("Prompt is required")
            return {"success": False, "error": "Prompt is required"}
        
        try:
            self.log_info(f"Calling {provider} with custom prompt")
            
            # Call Writer's _call_llm directly
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
            
            return {"success": True, "data": output_data}
            
        except Exception as e:
            self.log_error(f"Error generating content: {str(e)}")
            return {"success": False, "error": str(e)}
```

---

#### **Node 3: Writer Get Content**
**Type:** `writer_get_content`
**Category:** AI/Content
**Description:** Retrieve previously generated content from Writer

**Inputs:**
- `doc_name` (string, optional) - Specific document name to retrieve
- `limit` (number, default: 10) - Number of documents to retrieve
- `keyword_filter` (string, optional) - Filter by keyword
- `content_type_filter` (select, optional) - Filter by content type

**Outputs:**
- `contents` (array) - List of generated content documents
- `count` (number) - Total count

**Handler Code:**
```python
@NodeHandlerRegistry.register("writer_get_content")
class WriterGetContentNodeHandler(BaseNodeHandler):
    """Retrieve generated content from Writer"""
    
    def execute(self):
        doc_name = self.get_param("doc_name")
        limit = self.get_param("limit", 10)
        keyword_filter = self.get_param("keyword_filter")
        content_type_filter = self.get_param("content_type_filter")
        
        try:
            if doc_name:
                # Get specific document
                doc = frappe.get_doc("Generated Content", doc_name)
                output_data = {
                    "contents": [doc.as_dict()],
                    "count": 1
                }
            else:
                # Get list with filters
                filters = {}
                if keyword_filter:
                    filters["keyword"] = ["like", f"%{keyword_filter}%"]
                if content_type_filter:
                    filters["content_type"] = content_type_filter
                
                contents = frappe.get_all(
                    "Generated Content",
                    filters=filters,
                    fields=["name", "title", "generated_text", "keyword", "tone", "content_type", "creation"],
                    order_by="creation desc",
                    limit=limit
                )
                
                output_data = {
                    "contents": contents,
                    "count": len(contents)
                }
            
            self.set_output(output_data)
            self.log_info(f"Retrieved {output_data['count']} content(s)")
            
            return {"success": True, "data": output_data}
            
        except Exception as e:
            self.log_error(f"Error retrieving content: {str(e)}")
            return {"success": False, "error": str(e)}
```

---

### **Phase 2: Advanced Writer Nodes (Medium Priority)**

#### **Node 4: Writer Batch Generate**
**Type:** `writer_batch_generate`
**Category:** AI/Content
**Description:** Generate multiple pieces of content from a list of keywords

**Inputs:**
- `keywords` (array, required) - List of keywords
- `content_type` (select, required) - Type of content
- `tone` (select, required) - Tone
- `provider` (select, required) - LLM provider
- `model` (string, required) - Model name
- `delay_between` (number, default: 2) - Delay between requests (seconds)

**Outputs:**
- `results` (array) - Array of generated content
- `success_count` (number) - Number of successful generations
- `failed_count` (number) - Number of failed generations

---

#### **Node 5: Writer Rewrite Content**
**Type:** `writer_rewrite_content`
**Category:** AI/Content
**Description:** Rewrite existing content with a different tone or style

**Inputs:**
- `original_content` (text, required) - Content to rewrite
- `target_tone` (select, required) - Target tone
- `rewrite_instructions` (text, optional) - Specific instructions
- `provider` (select, required) - LLM provider
- `model` (string, required) - Model name

**Outputs:**
- `rewritten_content` (string) - The rewritten content
- `original_content` (string) - Original content for comparison

---

#### **Node 6: Writer Summarize**
**Type:** `writer_summarize`
**Category:** AI/Content
**Description:** Summarize long content into shorter form

**Inputs:**
- `content` (text, required) - Content to summarize
- `summary_length` (select, required) - short/medium/long
- `format` (select, required) - paragraph/bullet-points/key-points
- `provider` (select, required) - LLM provider
- `model` (string, required) - Model name

**Outputs:**
- `summary` (string) - The summarized content
- `original_length` (number) - Original character count
- `summary_length` (number) - Summary character count
- `compression_ratio` (number) - Percentage reduction

---

#### **Node 7: Writer Translate**
**Type:** `writer_translate`
**Category:** AI/Content
**Description:** Translate content to another language

**Inputs:**
- `content` (text, required) - Content to translate
- `source_language` (string, default: "auto") - Source language
- `target_language` (select, required) - Target language
- `provider` (select, required) - LLM provider
- `model` (string, required) - Model name

**Outputs:**
- `translated_content` (string) - Translated content
- `source_language` (string) - Detected/specified source language
- `target_language` (string) - Target language

---

#### **Node 8: Writer Extract Keywords**
**Type:** `writer_extract_keywords`
**Category:** AI/Content
**Description:** Extract keywords and key phrases from content

**Inputs:**
- `content` (text, required) - Content to analyze
- `max_keywords` (number, default: 10) - Maximum keywords to extract
- `provider` (select, required) - LLM provider
- `model` (string, required) - Model name

**Outputs:**
- `keywords` (array) - List of extracted keywords
- `keyword_count` (number) - Number of keywords found

---

### **Phase 3: Utility & Management Nodes (Low Priority)**

#### **Node 9: Writer Set API Key**
**Type:** `writer_set_api_key`
**Category:** AI/Config
**Description:** Set or update LLM provider API key

**Inputs:**
- `provider` (select, required) - LLM provider
- `api_key` (string, required) - API key value

**Outputs:**
- `success` (boolean) - Whether key was set successfully
- `provider` (string) - Provider name

---

#### **Node 10: Writer Get Providers**
**Type:** `writer_get_providers`
**Category:** AI/Config
**Description:** Get list of available LLM providers and their status

**Outputs:**
- `providers` (array) - List of providers with status
- `configured_count` (number) - Number of configured providers

---

## 📁 File Structure

```
automesh/
├── automesh/
│   └── workflow_engine/
│       ├── node_handlers.py (existing)
│       ├── test_node_types.py (existing)
│       └── writer_nodes.py (NEW - Writer integration nodes)
│
└── automesh/
    └── doctype/
        └── automesh_node_type/
            └── (Node type definitions will be created via setup script)
```

---

## 🔧 Implementation Steps

### **Step 1: Create Writer Nodes Module**
**File:** `automesh/automesh/workflow_engine/writer_nodes.py`

- [ ] Create new Python file
- [ ] Import required dependencies (frappe, NodeHandlerRegistry, BaseNodeHandler)
- [ ] Import Writer API functions
- [ ] Implement Phase 1 nodes (3 nodes)
- [ ] Add error handling and logging
- [ ] Add docstrings and comments

**Estimated Time:** 4-5 hours

---

### **Step 2: Create Node Type Definitions**
**File:** `automesh/automesh/workflow_engine/setup_writer_nodes.py`

Create a setup script similar to `test_node_types.py`:

```python
import frappe
import json
from .writer_nodes import NodeHandlerRegistry

def create_writer_node_types():
    """Create Writer integration node types in the database"""
    
    writer_node_types = [
        {
            "name": "writer_generate_content",
            "type": "writer_generate_content",
            "label": "Writer: Generate Content",
            "description": "Generate content using Writer app's LLM providers",
            "icon": "file-text",
            "color": "#8b5cf6",
            "category": "ai",
            "is_system": 1,
            "is_enabled": 1,
            "handler_module": "automesh.workflow_engine.writer_nodes",
            "handler_function": "WriterGenerateContentNodeHandler",
            "inputs": json.dumps([
                {
                    "name": "keyword",
                    "label": "Keyword/Topic",
                    "type": "string",
                    "required": True
                },
                {
                    "name": "content_type",
                    "label": "Content Type",
                    "type": "select",
                    "options": ["Blog Post", "Article", "Product Description", "Landing Page", "SEO Meta Description", "Social Media Post", "Blog Outline"],
                    "default": "Blog Post",
                    "required": True
                },
                {
                    "name": "tone",
                    "label": "Tone",
                    "type": "select",
                    "options": ["Professional", "Casual", "Friendly", "Formal", "Humorous", "Technical"],
                    "default": "Professional",
                    "required": True
                },
                {
                    "name": "provider",
                    "label": "LLM Provider",
                    "type": "select",
                    "options": ["openai", "anthropic", "google", "groq", "mistral", "ollama", "cohere", "perplexity", "together", "amazon_bedrock", "open_router"],
                    "default": "openai",
                    "required": True
                },
                {
                    "name": "model",
                    "label": "Model",
                    "type": "string",
                    "default": "gpt-4",
                    "required": True
                },
                {
                    "name": "save_to_db",
                    "label": "Save to Database",
                    "type": "boolean",
                    "default": True
                }
            ]),
            "outputs": json.dumps([
                {
                    "name": "generated_text",
                    "label": "Generated Text",
                    "type": "string"
                },
                {
                    "name": "title",
                    "label": "Title",
                    "type": "string"
                },
                {
                    "name": "doc_name",
                    "label": "Document Name",
                    "type": "string"
                }
            ])
        },
        # Add other node types here...
    ]
    
    for node_type in writer_node_types:
        if not frappe.db.exists("Automesh Node Type", node_type["name"]):
            doc = frappe.new_doc("Automesh Node Type")
            for key, value in node_type.items():
                doc.set(key, value)
            doc.insert()
            print(f"Created Writer node type: {node_type['name']}")
        else:
            doc = frappe.get_doc("Automesh Node Type", node_type["name"])
            for key, value in node_type.items():
                doc.set(key, value)
            doc.save()
            print(f"Updated Writer node type: {node_type['name']}")

if __name__ == "__main__":
    create_writer_node_types()
```

- [ ] Create setup script
- [ ] Define all Phase 1 node types
- [ ] Add proper field configurations
- [ ] Test node type creation

**Estimated Time:** 2-3 hours

---

### **Step 3: Update Frontend Node Types**
**File:** `frontend/src/components/workflow/nodes/NodeTypes.tsx`

- [ ] Add Writer node type definitions
- [ ] Add Writer category icon and color
- [ ] Add node templates for drag-and-drop
- [ ] Update node palette to show Writer nodes

**Estimated Time:** 2-3 hours

---

### **Step 4: Testing**

- [ ] Test Writer node creation in workflow editor
- [ ] Test node execution with different providers
- [ ] Test error handling (missing API keys, invalid params)
- [ ] Test integration with existing workflow nodes
- [ ] Test batch operations
- [ ] Create sample workflows using Writer nodes

**Estimated Time:** 3-4 hours

---

### **Step 5: Documentation**

- [ ] Document Writer node usage
- [ ] Create example workflows
- [ ] Document API key setup process
- [ ] Add troubleshooting guide

**Estimated Time:** 2 hours

---

## 📊 Implementation Summary

### **Phase 1: Core Nodes (High Priority)**
- **Nodes:** 3 (Generate Content, Custom Prompt, Get Content)
- **Estimated Time:** 11-13 hours
- **Dependencies:** Writer app must be installed

### **Phase 2: Advanced Nodes (Medium Priority)**
- **Nodes:** 5 (Batch Generate, Rewrite, Summarize, Translate, Extract Keywords)
- **Estimated Time:** 10-12 hours

### **Phase 3: Utility Nodes (Low Priority)**
- **Nodes:** 2 (Set API Key, Get Providers)
- **Estimated Time:** 3-4 hours

### **Total Estimated Time:** 24-29 hours (~3-4 working days)

---

## 🔐 Security Considerations

1. **API Key Storage**
   - API keys are stored encrypted in Frappe
   - Use Writer's existing API key management
   - Never log API keys

2. **Permission Checks**
   - Verify user has access to Writer app
   - Check permissions before executing nodes
   - Validate all inputs

3. **Rate Limiting**
   - Respect LLM provider rate limits
   - Add delays between batch requests
   - Handle rate limit errors gracefully

---

## 🧪 Testing Checklist

### **Unit Tests**
- [ ] Test each node handler independently
- [ ] Test with valid inputs
- [ ] Test with invalid inputs
- [ ] Test error handling

### **Integration Tests**
- [ ] Test Writer API connectivity
- [ ] Test with multiple providers
- [ ] Test workflow execution
- [ ] Test node chaining

### **End-to-End Tests**
- [ ] Create workflow with Writer nodes
- [ ] Execute workflow
- [ ] Verify outputs
- [ ] Test error recovery

---

## 📝 Usage Examples

### **Example 1: Simple Content Generation**
```
[Start] → [Writer Generate Content] → [End]

Parameters:
- keyword: "AI in Healthcare"
- content_type: "Blog Post"
- tone: "Professional"
- provider: "openai"
- model: "gpt-4"
```

### **Example 2: Content Pipeline**
```
[Start] 
  → [Writer Generate Content] (Generate draft)
  → [Writer Rewrite Content] (Humanize)
  → [Writer Extract Keywords] (SEO)
  → [Frappe Doc Create] (Save to CMS)
  → [End]
```

### **Example 3: Multi-Language Content**
```
[Start]
  → [Writer Generate Content] (English)
  → [Writer Translate] (Spanish)
  → [Writer Translate] (French)
  → [Merge] (Combine all versions)
  → [End]
```

---

## 🚀 Future Enhancements

1. **Streaming Support** - Stream LLM responses in real-time
2. **Cost Tracking** - Track token usage and costs per execution
3. **A/B Testing** - Generate multiple versions and compare
4. **Content Scheduling** - Schedule content generation
5. **Template Management** - Custom prompt templates
6. **Fine-tuning Integration** - Use fine-tuned models
7. **Content Versioning** - Track content revisions
8. **Quality Scoring** - Automatically score generated content

---

## 📞 Support & Resources

- **Writer App Repo:** `/home/jumes/bench-0/apps/writer`
- **AutoMesh Repo:** `/home/jumes/bench-0/apps/automesh`
- **Writer API:** `writer/api.py`
- **Node Handlers:** `automesh/workflow_engine/node_handlers.py`

---

**Last Updated:** 2025-10-01
**Status:** Planning Phase
**Next Step:** Begin Step 1 - Create Writer Nodes Module
