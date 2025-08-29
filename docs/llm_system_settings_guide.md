# Setting Up LLM System Settings DocType

This guide provides instructions for setting up the LLM System Settings DocType, which enables system administrators to configure default API keys for LLM providers that can be used as fallbacks when user-specific keys are not available.

## Overview

The LLM System Settings DocType is a single-instance DocType that stores system-level API keys for various LLM providers. These keys serve as fallbacks when users have not configured their personal API keys.

## DocType Creation Steps

Follow these steps to create the LLM System Settings DocType:

### 1. Create the DocType

1. Go to **DocType List** and click on **New**.
2. Enter the following basic information:
   - **DocType Name**: `LLM System Settings`
   - **Module**: `Writer`
   - Check **Is Single** (this creates a single-instance DocType)

### 2. Add Fields to the DocType

Add the following fields in the specified order:

#### Section Break

1. Field Type: **Section Break**
   - Label: `LLM Provider System Settings`
   - Fieldname: `system_provider_settings_section`

#### Provider Settings Table

2. Field Type: **Table**
   - Label: `LLM Provider Settings`
   - Fieldname: `system_provider_settings`
   - Options: `LLM Provider Setting` (this should reference the same child table used in the user-level LLM Settings)
   - Mandatory: No

### 3. Configure Permissions

Set the following permissions:
- Give **System Manager** role full permissions (Read, Write, Create, Delete, etc.)

### 4. Save the DocType

Click **Save** to create the DocType.

## Code Integration

After creating the DocType, you'll need to update the API key retrieval functions to check for system-level keys when user-level keys aren't available:

### Modify `get_llm_api_key` function in `api.py`

```python
@frappe.whitelist()
def get_llm_api_key(provider: str):
    """Get LLM API key for the specified provider
    
    First checks for user-specific API key, then falls back to system-level API key
    
    Args:
        provider (str): The LLM provider name (e.g., 'openai', 'anthropic')
        
    Returns:
        dict: Dictionary with 'api_key' if found, empty dict otherwise
        
    Note:
        Returns a dict with 'api_key' key to maintain API compatibility
    """
    # Normalize provider name for consistency in lookups
    provider_normalized = provider.lower()
    
    # First try to get user-specific API key
    user = frappe.session.user
    llm_settings_name = frappe.db.exists("LLM Settings", {"user": user})

    if llm_settings_name:
        doc = frappe.get_doc("LLM Settings", llm_settings_name)
        for setting in doc.provider_settings:
            if setting.provider.lower() == provider_normalized:
                api_key = setting.get_password("api_key")
                if api_key:
                    return {"api_key": api_key}

    # If no user-specific key is found, check system settings
    try:
        if frappe.db.exists("DocType", "LLM System Settings"):
            system_settings = frappe.get_single("LLM System Settings")
            for setting in system_settings.system_provider_settings:
                if setting.provider.lower() == provider_normalized:
                    api_key = setting.get_password("api_key")
                    if api_key:
                        return {"api_key": api_key}
    except Exception as e:
        frappe.log_error(f"Error accessing system LLM settings: {str(e)}", "LLM API Key Error")

    # No API key found
    return {}
```

## System Administration

### Setting System-Level API Keys

System administrators can configure default API keys by:

1. Go to **LLM System Settings** in the Desk
2. Add entries to the `LLM Provider Settings` table
3. For each provider:
   - Enter the provider name exactly as it appears in the code (e.g., `OpenAI`, `Anthropic`, etc.)
   - Enter the API key
   - Click **Save**

### Security Considerations

- System-level API keys should be managed carefully as they will be used by all users who don't have personal API keys
- Consider implementing usage limits or monitoring to prevent excessive use
- Regularly audit and rotate API keys following security best practices

## Troubleshooting

If system-level API keys aren't being recognized:

1. Check that the DocType name is exactly `LLM System Settings`
2. Verify that provider names match exactly (case-sensitive) with what's being used in the code
3. Check the error logs for any issues accessing the system settings

## Best Practices

1. Document which providers have system-level API keys for your users
2. Encourage users to set up personal API keys when possible
3. Update error messages to guide users when neither personal nor system keys are available
