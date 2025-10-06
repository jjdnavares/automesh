# Essential Workflow Nodes - Quick Reference

**6 High-Priority Nodes** | **Production Ready** | **2025-10-03**

---

## 🔄 Loop / For Each

**Node Types:** `loop`, `for_each`

```json
{
  "type": "loop",
  "data": {
    "params": {
      "items_path": "users",
      "item_variable_name": "user",
      "index_variable_name": "idx",
      "max_iterations": 1000
    }
  }
}
```

**Use Cases:**
- Process array of items
- Batch operations
- Data transformation loops

---

## ⚡ Parallel

**Node Type:** `parallel`

```json
{
  "type": "parallel",
  "data": {
    "params": {}
  }
}
```

**Use Cases:**
- Execute multiple API calls simultaneously
- Run independent operations
- Parallel data processing

---

## 🔀 Merge

**Node Type:** `merge`

```json
{
  "type": "merge",
  "data": {
    "params": {
      "merge_strategy": "all"  // first, last, all, object, array
    }
  }
}
```

**Strategies:**
- `first` - First non-empty input
- `last` - Last non-empty input
- `all` - Array of all inputs
- `object` - Merge objects into one
- `array` - Flatten arrays

**Use Cases:**
- Combine parallel branch results
- Aggregate data from multiple sources
- Conditional data merging

---

## 🔀 Switch

**Node Type:** `switch`

```json
{
  "type": "switch",
  "data": {
    "params": {
      "switch_value_path": "status",
      "cases": [
        {"value": "active", "label": "active_case"},
        {"value": "pending", "label": "pending_case"}
      ],
      "default_case": "default"
    }
  }
}
```

**Use Cases:**
- Route based on status/type
- Multi-way conditional logic
- Dynamic workflow paths

---

## 💾 Set Variable

**Node Type:** `set_variable`

```json
{
  "type": "set_variable",
  "data": {
    "params": {
      "variable_name": "counter",
      "variable_value": 42,
      "value_from_input": false,
      "input_path": "user.id"
    }
  }
}
```

**Use Cases:**
- Store intermediate results
- Share data between nodes
- Maintain workflow state

---

## 📥 Get Variable

**Node Type:** `get_variable`

```json
{
  "type": "get_variable",
  "data": {
    "params": {
      "variable_name": "counter",
      "default_value": 0
    }
  }
}
```

**Use Cases:**
- Retrieve stored values
- Access shared state
- Conditional logic based on variables

---

## 🧪 Testing

```bash
# Run all tests
bench --site [site] execute automesh.automesh.workflow_engine.test_essential_nodes.run_all_tests

# Test specific node
bench --site [site] execute automesh.automesh.workflow_engine.test_essential_nodes.quick_test --args "['loop']"
```

---

## 📊 Complete Node List (26 Total)

### Core (4)
- start, end, condition, delay

### HTTP (1)
- http_request

### Transform (1)
- transform

### Frappe (5)
- frappe_doc_create, frappe_doc_update, frappe_doc_get, frappe_doc_delete, frappe_doc_list

### Essential (6) ✅ NEW
- loop/for_each, parallel, merge, switch, set_variable, get_variable

### Writer AI (3)
- writer_generate_content, writer_custom_prompt, writer_get_content

### Test (6)
- test_echo, test_random, test_delay, test_math, test_error, test_transform

---

## 📚 Full Documentation

- **Implementation:** `ESSENTIAL_NODES_IMPLEMENTATION.md`
- **Checklist:** `WORKFLOW_FEATURES_CHECKLIST.md`
- **Tests:** `automesh/automesh/workflow_engine/test_essential_nodes.py`
- **Code:** `automesh/automesh/workflow_engine/node_handlers.py`
