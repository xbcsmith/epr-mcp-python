# EPR MCP Server Input Validation Schemas

This document describes the input validation schemas implemented for the EPR MCP Server tools.

## Overview

The schema validation system uses Pydantic models to ensure that all input data to the MCP tools is properly validated before processing. This helps prevent errors, improves security, and provides clear error messages when invalid data is provided.

## Schema Components

### Base Models

- **BaseModel**: All schemas inherit from Pydantic's BaseModel
- **Field**: Used for field definitions with validation rules and descriptions
- **validator**: Custom validation decorators for complex field validation

### Search Schemas

#### EventSearchInput
Validates input for searching events:
```python
{
    "name": "optional string",
    "version": "optional string", 
    "release": "optional string",
    "platform_id": "optional string",
    "package": "optional string",
    "description": "optional string",
    "success": "optional boolean",
    "event_receiver_id": "optional string"
}
```

#### EventReceiverSearchInput
Validates input for searching event receivers:
```python
{
    "name": "optional string",
    "type": "optional string",
    "version": "optional string",
    "description": "optional string"
}
```

#### EventReceiverGroupSearchInput
Validates input for searching event receiver groups:
```python
{
    "name": "optional string",
    "type": "optional string", 
    "version": "optional string",
    "description": "optional string"
}
```

### Creation Schemas

#### EventCreateInput
Validates input for creating events (all fields required):
```python
{
    "name": "string (min_length=1)",
    "version": "string (min_length=1)",
    "release": "string (min_length=1)",
    "platform_id": "string (min_length=1)",
    "package": "string (min_length=1)",
    "description": "string (min_length=1)",
    "event_receiver_id": "string (min_length=1)",
    "success": "boolean",
    "payload": "dict (required, must be dictionary)"
}
```

#### EventReceiverCreateInput
Validates input for creating event receivers (all fields required):
```python
{
    "name": "string (min_length=1)",
    "type": "string (min_length=1)",
    "version": "string (min_length=1)",
    "description": "string (min_length=1)"
}
```

#### EventReceiverGroupCreateInput
Validates input for creating event receiver groups (all fields required):
```python
{
    "name": "string (min_length=1)",
    "type": "string (min_length=1)",
    "version": "string (min_length=1)",
    "description": "string (min_length=1)",
    "event_receiver_ids": "list of strings (min_items=1, all non-empty)"
}
```

### Fetch Schema

#### FetchInput
Validates input for fetch operations:
```python
{
    "id": "string (min_length=1, trimmed)"
}
```

## Data Wrappers

### SearchDataWrapper
Wraps search inputs in a `data` field:
```python
{
    "data": EventSearchInput | EventReceiverSearchInput | EventReceiverGroupSearchInput
}
```

### CreateDataWrapper  
Wraps creation inputs in a `data` field:
```python
{
    "data": EventCreateInput | EventReceiverCreateInput | EventReceiverGroupCreateInput
}
```

## Usage

### Validation Function

The main validation function is `validate_input(operation, input_data)`:

```python
from schemas import validate_input
from pydantic import ValidationError

try:
    validated_data = validate_input("search_events", {
        "data": {
            "name": "foo",
            "version": "1.0.0"
        }
    })
    # Use validated_data...
except (ValidationError, ValueError) as e:
    # Handle validation error
    print(f"Validation error: {e}")
```

### Operation Mapping

The system supports these operations:
- `search_events` → SearchDataWrapper
- `search_receivers` → SearchDataWrapper  
- `search_groups` → SearchDataWrapper
- `create_event` → CreateDataWrapper
- `create_receiver` → CreateDataWrapper
- `create_group` → CreateDataWrapper
- `fetch_event` → FetchInput
- `fetch_receiver` → FetchInput
- `fetch_group` → FetchInput

## Integration with MCP Tools

Each MCP tool now includes validation:

```python
@mcp.tool(title="Search Events", description="Search for events in EPR")
async def search_events(data: dict) -> str:
    try:
        validated_data = validate_input("search_events", data)
    except (ValidationError, ValueError) as e:
        return f"Validation error: {str(e)}"
    
    # Process validated_data...
```

## Benefits

1. **Type Safety**: Ensures correct data types for all fields
2. **Required Field Validation**: Prevents missing required fields
3. **Format Validation**: Validates string lengths, list contents, etc.
4. **Clear Error Messages**: Pydantic provides detailed validation errors
5. **Documentation**: Schema serves as documentation for expected input formats
6. **Security**: Prevents injection attacks and malformed data

## Testing

Run the validation tests:

```bash
cd /home/bsmith/go/src/github.com/xbcsmith/epr-workshop/11-epr-mcp-server/src
python test_schemas.py
```

## Error Handling

Validation errors are caught and returned as user-friendly error messages:
- Missing required fields
- Invalid data types
- Empty strings where content is required
- Invalid list contents
- Malformed dictionaries

## Dependencies

- `pydantic>=2.0.0`: Core validation library
- `typing`: Type hints for Python < 3.9 compatibility