# Writer Nodes for AutoMesh - Setup & Usage Guide

**Status:** ✅ Phase 1.1 Implemented
**Date:** 2025-10-01
**Nodes:** 3 (Generate Content, Custom Prompt, Get Content)

---

## 📋 Prerequisites

### 1. Writer App Must Be Installed
```bash
cd ~/frappe-bench
bench get-app https://github.com/your-repo/writer
bench --site your-site install-app writer
```

### 2. Configure LLM API Keys

You need to set up API keys for at least one LLM provider. You can do this in two ways:

#### **Option A: User-Level API Keys (Recommended for testing)**
1. Go to Writer app in your Frappe site
2. Navigate to LLM Settings
3. Add your API key for your chosen provider (e.g., OpenAI)

#### **Option B: System-Level API Keys (Recommended for production)**
1. Go to LLM System Settings (requires System Manager role)
2. Add API keys for providers that all users can access

**Supported Providers:**
- OpenAI (requires: `pip install openai`)
- Anthropic (requires: `pip install anthropic`)
- Google (requires: `pip install google-generativeai`)
- Groq, Mistral, Together, OpenRouter (use OpenAI SDK)
- Ollama (self-hosted, no API key needed)
- Cohere, Perplexity (HTTP-based, no extra packages)
- Amazon Bedrock (requires: `pip install boto3`)

---

## 🚀 Installation Steps

### Step 1: Register Writer Nodes

Open Frappe console:
```bash
cd ~/frappe-bench
bench --site your-site console
```

Run the setup script:
```python
from automesh.workflow_engine.setup_writer_nodes import setup_writer_nodes
setup_writer_nodes()
```

Expected output:
```
✓ Created Writer node type: Writer: Generate Content
✓ Created Writer node type: Writer: Custom Prompt
✓ Created Writer node type: Writer: Get Content

============================================================
Writer Nodes Setup Complete!
Created: 3 | Updated: 0
============================================================
```

### Step 2: Verify Installation

Check that nodes are registered:
```python
import frappe
nodes = frappe.get_all("Automesh Node Type", 
    filters={"category": "ai"}, 
    fields=["name", "label", "is_enabled"])
print(nodes)
```

You should see the 3 Writer nodes listed.

### Step 3: Test the Nodes (Optional)

Run the test suite:
```python
from automesh.workflow_engine.test_writer_nodes import test_writer_nodes
test_writer_nodes()
```

---

## 📖 Node Documentation

### Node 1: Writer Generate Content

**Type:** `writer_generate_content`
**Category:** AI/Content
**Icon:** 📄 file-text
**Color:** Purple (#8b5cf6)

**Description:**
Generates content using Writer app's LLM providers with predefined templates and automatic humanization.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| keyword | string | ✅ Yes | - | Main keyword or topic for content generation |
| content_type | select | ✅ Yes | "Blog Post" | Type of content (Blog Post, Article, Product Description, etc.) |
| tone | select | ✅ Yes | "Professional" | Tone of content (Professional, Casual, Friendly, etc.) |
| provider | select | ✅ Yes | "openai" | LLM provider to use |
| model | string | ✅ Yes | "gpt-4" | Model name (e.g., "gpt-4", "claude-3-opus") |

**Outputs:**

| Output | Type | Description |
|--------|------|-------------|
| generated_text | string | The generated content text |
| title | string | Title of the generated content |
| doc_name | string | Name of the saved document in Generated Content |
| prompt_used | string | The prompt that was used |
| keyword | string | The keyword used |
| content_type | string | Type of content generated |
| provider | string | LLM provider used |
| model | string | Model used |

**Example Usage:**
```json
{
  "keyword": "Artificial Intelligence in Healthcare",
  "content_type": "Blog Post",
  "tone": "Professional",
  "provider": "openai",
  "model": "gpt-4"
}
```

**Content Types Available:**
- Blog Post
- Article
- Product Description
- Landing Page
- SEO Meta Description
- Social Media Post
- Blog Outline

**Tones Available:**
- Professional
- Casual
- Friendly
- Formal
- Humorous
- Technical

---

### Node 2: Writer Custom Prompt

**Type:** `writer_custom_prompt`
**Category:** AI/Content
**Icon:** ✏️ edit
**Color:** Purple (#8b5cf6)

**Description:**
Generates content with a custom prompt without using predefined templates. Provides maximum flexibility for specialized use cases.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| prompt | text | ✅ Yes | - | Custom prompt text. Use {variable} for placeholders |
| provider | select | ✅ Yes | "openai" | LLM provider to use |
| model | string | ✅ Yes | "gpt-4" | Model name |

**Outputs:**

| Output | Type | Description |
|--------|------|-------------|
| generated_text | string | The generated response |
| prompt_used | string | The final prompt that was used |
| provider | string | LLM provider used |
| model | string | Model used |

**Example Usage:**
```json
{
  "prompt": "Write a compelling product description for an eco-friendly water bottle that keeps drinks cold for 24 hours.",
  "provider": "anthropic",
  "model": "claude-3-opus-20240229"
}
```

**Advanced: Using Placeholders**

If this node receives input from a previous node, you can use placeholders in your prompt:

```json
{
  "prompt": "Rewrite the following text in a {tone} tone:\n\n{text}",
  "provider": "openai",
  "model": "gpt-4"
}
```

The node will automatically fill `{tone}` and `{text}` from the input data.

---

### Node 3: Writer Get Content

**Type:** `writer_get_content`
**Category:** AI/Content
**Icon:** 🗄️ database
**Color:** Purple (#8b5cf6)

**Description:**
Retrieves previously generated content from the Writer app's database.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| doc_name | string | ❌ No | - | Specific document name to retrieve |
| limit | number | ❌ No | 10 | Maximum number of documents to retrieve |
| keyword_filter | string | ❌ No | - | Filter by keyword (partial match) |
| content_type_filter | select | ❌ No | - | Filter by content type |

**Outputs:**

| Output | Type | Description |
|--------|------|-------------|
| contents | array | List of generated content documents |
| count | number | Total number of documents retrieved |

**Example Usage 1: Get Specific Document**
```json
{
  "doc_name": "GC-00001"
}
```

**Example Usage 2: Get Latest 5 Blog Posts**
```json
{
  "limit": 5,
  "content_type_filter": "Blog Post"
}
```

**Example Usage 3: Search by Keyword**
```json
{
  "limit": 10,
  "keyword_filter": "healthcare"
}
```

---

## 🔧 Workflow Examples

### Example 1: Simple Content Generation

```
[Start Node]
    ↓
[Writer: Generate Content]
  - keyword: "AI in Healthcare"
  - content_type: "Blog Post"
  - tone: "Professional"
  - provider: "openai"
  - model: "gpt-4"
    ↓
[End Node]
```

**Result:** Generates a professional blog post about AI in Healthcare and saves it to the database.

---

### Example 2: Content Generation Pipeline

```
[Start Node]
    ↓
[Writer: Generate Content]
  - keyword: "Sustainable Fashion"
  - content_type: "Article"
  - tone: "Friendly"
    ↓
[Writer: Custom Prompt]
  - prompt: "Extract 5 key takeaways from: {generated_text}"
    ↓
[Frappe Doc Create]
  - doctype: "Blog Post"
  - content: {generated_text}
    ↓
[End Node]
```

**Result:** Generates an article, extracts key takeaways, and creates a Blog Post document in Frappe.

---

### Example 3: Batch Content Retrieval & Processing

```
[Start Node]
    ↓
[Writer: Get Content]
  - limit: 10
  - content_type_filter: "Blog Post"
    ↓
[Loop Node] (for each content)
    ↓
[Writer: Custom Prompt]
  - prompt: "Generate SEO meta description for: {generated_text}"
    ↓
[Frappe Doc Update]
  - Update the blog post with meta description
    ↓
[End Node]
```

**Result:** Retrieves 10 blog posts and generates SEO meta descriptions for each.

---

### Example 4: Multi-Provider Comparison

```
[Start Node]
    ↓
[Parallel Node]
    ├─→ [Writer: Generate Content] (OpenAI GPT-4)
    ├─→ [Writer: Generate Content] (Anthropic Claude)
    └─→ [Writer: Generate Content] (Google Gemini)
    ↓
[Merge Node]
    ↓
[Writer: Custom Prompt]
  - prompt: "Compare these 3 versions and pick the best one"
    ↓
[End Node]
```

**Result:** Generates content using 3 different providers and compares them.

---

## 🔐 Security & Best Practices

### API Key Management

1. **Never hardcode API keys** in workflow parameters
2. **Use Writer's API key management** (user or system level)
3. **Rotate keys regularly** for security
4. **Use different keys** for development and production

### Cost Management

1. **Monitor token usage** - LLM calls can be expensive
2. **Set reasonable limits** on batch operations
3. **Use cheaper models** for testing (e.g., gpt-3.5-turbo instead of gpt-4)
4. **Cache results** when possible using Writer: Get Content

### Error Handling

All Writer nodes handle these errors gracefully:
- ✅ Missing API keys
- ✅ Invalid provider/model
- ✅ Rate limiting
- ✅ Network errors
- ✅ Permission errors

Check the workflow execution logs for detailed error messages.

---

## 🐛 Troubleshooting

### Issue: "Writer app is not installed"

**Solution:**
```bash
bench --site your-site install-app writer
```

### Issue: "API key for 'openai' is not set"

**Solution:**
1. Go to Writer app → LLM Settings
2. Add your OpenAI API key
3. Or ask admin to set system-level API key

### Issue: "The OpenAI package is not installed"

**Solution:**
```bash
cd ~/frappe-bench
./env/bin/pip install openai
bench restart
```

### Issue: Node not appearing in workflow editor

**Solution:**
1. Clear cache: `bench --site your-site clear-cache`
2. Restart bench: `bench restart`
3. Refresh browser
4. Re-run setup script if needed

### Issue: "Permission denied"

**Solution:**
- Ensure you have access to Writer app
- Check DocType permissions for "Generated Content"
- Contact system administrator

---

## 📊 Performance Tips

1. **Use appropriate models:**
   - Fast & cheap: `gpt-3.5-turbo`, `claude-instant`
   - Balanced: `gpt-4`, `claude-3-sonnet`
   - Best quality: `gpt-4-turbo`, `claude-3-opus`

2. **Batch operations:**
   - Add delays between requests to avoid rate limits
   - Use the delay node between batch operations

3. **Content reuse:**
   - Use Writer: Get Content to retrieve existing content
   - Avoid regenerating the same content multiple times

---

## 🔄 Updating Nodes

If you make changes to the node handlers, update the node types:

```bash
bench --site your-site console
```

```python
from automesh.workflow_engine.setup_writer_nodes import setup_writer_nodes
setup_writer_nodes()  # This will update existing nodes
```

---

## 📝 Next Steps

### Phase 2: Advanced Nodes (Coming Soon)
- Writer: Batch Generate
- Writer: Rewrite Content
- Writer: Summarize
- Writer: Translate
- Writer: Extract Keywords

### Phase 3: Utility Nodes (Coming Soon)
- Writer: Set API Key
- Writer: Get Providers

---

## 🆘 Support

- **Documentation:** See `WRITER_NODES_IMPLEMENTATION.md`
- **Issues:** Report bugs in the AutoMesh repository
- **Writer App:** Check Writer app documentation for LLM setup

---

**Last Updated:** 2025-10-01
**Version:** 1.0.0 (Phase 1.1)
**Status:** ✅ Production Ready
