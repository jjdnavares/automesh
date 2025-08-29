# Guide to Creating Secure LLM Setting Doctypes

To securely store API keys on a per-user basis, you need to create two Doctypes: a child Doctype to hold the provider and key, and a parent Doctype linked to the user.

### Step 1: Create the `LLM Provider Setting` Doctype

This will be a child table (`Is Table`) that stores the API key for a specific LLM provider.

1.  Navigate to the **Doctype List** in your Frappe desk.
2.  Click **New**.
3.  Fill in the following details:
    *   **Name**: `LLM Provider Setting`
    *   **Module**: `Writer`
    *   Check the **Is Table** checkbox. This marks it as a child Doctype.
4.  In the **Fields** section, add the following rows:
    *   **Field 1:**
        *   **Label**: `Provider`
        *   **Field Type**: `Data`
        *   **Required**: Yes
        *   **In List View**: Yes
    *   **Field 2:**
        *   **Label**: `API Key`
        *   **Field Type**: `Password` (This encrypts the key in the database)
        *   **Required**: Yes
5.  **Save** the Doctype.

### Step 2: Create the `LLM Settings` Doctype

This Doctype will be linked to a `User` and will contain the table of provider settings.

1.  Go back to the **Doctype List** and click **New**.
2.  Fill in the following details:
    *   **Name**: `LLM Settings`
    *   **Module**: `Writer`
3.  Under the **Naming** section, set the **Naming Rule** to **Set by fieldname** and select `user` as the field. This ensures each user has a unique settings document named after their user ID.
4.  In the **Fields** section, add the following rows:
    *   **Field 1:**
        *   **Label**: `User`
        *   **Field Type**: `Link`
        *   **Options**: `User`
        *   **Required**: Yes
        *   **Unique**: Yes (Ensures one settings document per user)
    *   **Field 2:**
        *   **Label**: `Provider Settings`
        *   **Field Type**: `Table`
        *   **Options**: `LLM Provider Setting` (Link to the child Doctype)
5.  Go to the **Permission Rules** section and add the following rules:
    *   **Rule 1 (System Manager):**
        *   **Role**: `System Manager`
        *   Give all permissions (Read, Write, Create, Delete, etc.).
    *   **Rule 2 (User):**
        *   **Role**: `All`
        *   Check **If Owner**.
        *   Grant `Read`, `Write`, `Create`, and `Delete` permissions. This allows users to manage their own settings.
6.  **Save** the Doctype.

### Step 3: Apply Changes to the Database

After creating these Doctypes, you need to apply the changes to your database by running a migration.

1.  Open your terminal in the bench directory (`/home/jumes/bench-0/`).
2.  Run the following command:
    ```bash
    bench migrate
    ```

After following these steps, the database will be ready. You can then update the `set_llm_api_key` and `get_llm_api_key` methods in `writer/api.py` to use these new Doctypes for secure, per-user API key management.
