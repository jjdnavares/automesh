# Data & Integration Nodes - Quick Reference

**10 Nodes** | **Production Ready** | **2025-10-05**

---

## 📄 JSON Nodes

### json_parse
```json
{
  "type": "json_parse",
  "data": {
    "params": {
      "json_string_path": "json_string",
      "strict": true
    }
  }
}
```
**Use:** Parse JSON strings to objects/arrays

### json_stringify
```json
{
  "type": "json_stringify",
  "data": {
    "params": {
      "indent": 2,
      "sort_keys": false
    }
  }
}
```
**Use:** Convert objects to JSON strings

---

## 📋 XML Nodes

### xml_parse
```json
{
  "type": "xml_parse",
  "data": {
    "params": {
      "xml_string_path": "xml_string"
    }
  }
}
```
**Use:** Parse XML strings to dict

### xml_build
```json
{
  "type": "xml_build",
  "data": {
    "params": {
      "root_tag": "root",
      "pretty_print": true
    }
  }
}
```
**Use:** Build XML from dict

---

## 📊 CSV Nodes

### csv_parse
```json
{
  "type": "csv_parse",
  "data": {
    "params": {
      "delimiter": ",",
      "has_header": true,
      "skip_empty_rows": true
    }
  }
}
```
**Use:** Parse CSV to arrays

### csv_build
```json
{
  "type": "csv_build",
  "data": {
    "params": {
      "delimiter": ",",
      "include_header": true
    }
  }
}
```
**Use:** Build CSV from arrays

---

## 📝 Template Node

### template
```json
{
  "type": "template",
  "data": {
    "params": {
      "template_string": "Hello {{ name }}!"
    }
  }
}
```
**Use:** Render Jinja2 templates  
**Syntax:** Full Jinja2 support (loops, conditionals, filters)

---

## 🔍 Regex Node

### regex
```json
{
  "type": "regex",
  "data": {
    "params": {
      "pattern": "\\w+@\\w+\\.\\w+",
      "operation": "search",  // match, search, findall, replace
      "replacement": "",
      "text_path": "text"
    }
  }
}
```
**Operations:**
- `match` - Match from start
- `search` - Search anywhere
- `findall` - Find all matches
- `replace` - Replace matches

---

## 💻 Code Node

### code
```json
{
  "type": "code",
  "data": {
    "params": {
      "code_string": "output = sum(input['numbers'])"
    }
  }
}
```
**Use:** Execute safe Python code  
**Available:** input, variables, output  
**Builtins:** len, str, int, float, list, dict, sum, min, max, etc.

---

## 🔄 Function Node

### function
```json
{
  "type": "function",
  "data": {
    "params": {
      "workflow_name": "My Sub Workflow"
    }
  }
}
```
**Use:** Call sub-workflows as functions

---

## 🧪 Testing

```bash
# Run all tests
bench --site [site] execute automesh.automesh.workflow_engine.test_data_nodes.run_all_tests

# Test specific node
bench --site [site] execute automesh.automesh.workflow_engine.test_data_nodes.quick_test --args "['json_parse']"
```

---

## 📊 Complete Node List (36 Total)

### Core (4)
- start, end, condition, delay

### HTTP (1)
- http_request

### Transform (1)
- transform

### Frappe (5)
- frappe_doc_create, frappe_doc_update, frappe_doc_get, frappe_doc_delete, frappe_doc_list

### Essential (6)
- loop/for_each, parallel, merge, switch, set_variable, get_variable

### Data & Integration (10) ✅ NEW
- json_parse, json_stringify, xml_parse, xml_build, csv_parse, csv_build, template, regex, code, function

### Writer AI (3)
- writer_generate_content, writer_custom_prompt, writer_get_content

### Test (6)
- test_echo, test_random, test_delay, test_math, test_error, test_transform

---

## 📚 Full Documentation

- **Implementation:** `DATA_NODES_IMPLEMENTATION.md`
- **Checklist:** `WORKFLOW_FEATURES_CHECKLIST.md`
- **Tests:** `automesh/automesh/workflow_engine/test_data_nodes.py`
- **Code:** `automesh/automesh/workflow_engine/node_handlers.py` (lines 1350-2250)
