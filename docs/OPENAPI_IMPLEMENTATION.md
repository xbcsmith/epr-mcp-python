# EPR MCP Server - OpenAPI Implementation

## Summary

I have successfully implemented OpenAPI endpoint support for the EPR MCP Server.
This implementation provides a comprehensive API interface with automatic MCP
tool generation, interactive documentation, and schema validation.

## What Was Implemented

### 1. OpenAPI 3.0 Specification (`src/epr_mcp/openapi.yaml`)

A complete OpenAPI 3.0 specification that defines:

- **Schemas**: Event, EventReceiver, EventReceiverGroup, SearchCriteria, Error
- **Endpoints**:
  - Fetch operations: `GET /api/v1/{resource}/{id}`
  - Create operations: `POST /api/v1/{resource}`
  - Search operations: `POST /api/v1/{resource}/search`
  - Health check: `GET /health`
- **Request/Response types**: Proper typing for all operations
- **Validation rules**: Required fields, data types, constraints

### 2. OpenAPI Endpoint Support (`server.py`)

Enhanced the existing server with:

- **OpenAPI Spec Endpoints**:

  - `GET /openapi.yaml` - YAML format specification
  - `GET /openapi.json` - JSON format specification
  - `GET /docs` - Swagger UI interactive documentation

- **Improved Error Handling**: Better HTTP status codes and error messages
- **Structured Responses**: All responses now use model objects and return JSON
- **Schema Integration**: Full integration with existing Pydantic validation
  schemas

### 3. Alternative OpenAPI Server (`openapi_server.py`)

A demonstration of how to use FastMCP's native OpenAPI integration:

- **FastMCPOpenAPI Class**: Shows how to leverage FastMCP's built-in OpenAPI
  support
- **Route Mappings**: Configuration to map OpenAPI paths to MCP components
- **Handler Classes**: Structured approach for handling API operations

### 4. Enhanced Models and Schemas

- **Updated GraphQLQuery**: Fixed to support dictionary variables
- **Model Integration**: Full integration between dataclass models and API
  operations
- **Validation**: Consistent ValidationError usage throughout the codebase

### 5. Testing and Documentation

- **Comprehensive Tests** (`tests/test_openapi.py`): Validates OpenAPI spec
  structure and schemas
- **Demo Script** (`openapi_demo.py`): Interactive demonstration of capabilities
- **Updated README**: Complete documentation of OpenAPI features
- **Updated Dependencies**: Added PyYAML for OpenAPI spec handling

## Key Features

### 🔄 Automatic MCP Tool Generation

The OpenAPI specification can be used with FastMCP to automatically generate MCP
tools, eliminating manual tool definition.

### 📚 Interactive Documentation

Swagger UI provides a user-friendly interface to explore and test the API
endpoints directly in the browser.

### 🛡️ Type Safety & Validation

- Pydantic schemas for request validation
- Dataclass models for response serialization
- OpenAPI schemas for API documentation
- Consistent error handling with ValidationError

### 🔌 Flexible Architecture

- Works with existing manual MCP tool definitions
- Can be migrated to use FastMCP's OpenAPI integration
- Maintains backward compatibility
- Extensible for future enhancements

## API Endpoints Available

When the server is running on `http://localhost:8000`:

| Endpoint        | Purpose                       | Format            |
| --------------- | ----------------------------- | ----------------- |
| `/openapi.yaml` | OpenAPI specification         | YAML              |
| `/openapi.json` | OpenAPI specification         | JSON              |
| `/docs`         | Interactive API documentation | HTML (Swagger UI) |
| `/health`       | Health check                  | Plain text        |

## MCP Tools Generated

From the OpenAPI specification, these MCP tools are available:

1. **fetchEvent** - Retrieve a single event by ID
2. **fetchReceiver** - Retrieve a single event receiver by ID
3. **fetchGroup** - Retrieve a single event receiver group by ID
4. **createEvent** - Create a new event
5. **createReceiver** - Create a new event receiver
6. **createGroup** - Create a new event receiver group
7. **searchEvents** - Search for events with criteria
8. **searchReceivers** - Search for event receivers with criteria
9. **searchGroups** - Search for event receiver groups with criteria
10. **healthCheck** - Health status check

## Benefits

### For Developers

- Clear API contract with OpenAPI specification
- Interactive testing with Swagger UI
- Automatic tool generation reduces boilerplate
- Type-safe operations with proper validation

### For Users

- Consistent interface across all operations
- Self-documenting API with examples
- Better error messages and status codes
- Structured JSON responses

### For Maintenance

- Single source of truth for API definition
- Automatic validation ensures consistency
- Easy to extend with new operations
- Clear separation of concerns

## Next Steps

1. **Install Dependencies**: `pip install PyYAML fastmcp`
2. **Start Server**: Run with your EPR configuration
3. **Explore API**: Visit `http://localhost:8000/docs`
4. **Use MCP Tools**: Integrate with MCP clients
5. **Extend**: Add new operations to the OpenAPI spec

## File Structure

```text
src/epr_mcp/
├── openapi.yaml           # OpenAPI 3.0 specification
├── server.py              # Enhanced MCP server with OpenAPI endpoints
├── openapi_server.py      # Alternative FastMCP OpenAPI implementation
├── models.py              # Data models (Event, EventReceiver, etc.)
├── schemas.py             # Pydantic validation schemas
└── ...

tests/
├── test_openapi.py        # OpenAPI specification tests
└── ...

openapi_demo.py            # Interactive demonstration script
README.md                  # Updated documentation
```

This implementation provides a robust, well-documented, and extensible
foundation for the EPR MCP Server with full OpenAPI support.
