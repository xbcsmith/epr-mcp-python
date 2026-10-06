# EPR MCP Server Documentation

Documentation for the EPR (Event Provenance Registry) MCP server, organized with
the [Diataxis](https://diataxis.fr) framework. For installation and day-to-day
use, start with the [repository README](../README.md).

## Tutorials (`docs/tutorials/`)

Learning-oriented, step by step.

| Document                          | Description                                                                                                                |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| [Workshop](./tutorials/README.md) | Build the server step by step in about two and a half hours, with checkpoints, an EPR environment, tests, and editor setup |

## How-to guides (`docs/how-tos/`)

Task-oriented recipes.

| Document                                         | Description                                                                          |
| ------------------------------------------------ | ------------------------------------------------------------------------------------ |
| [docker_compose.md](./how-tos/docker_compose.md) | Run the server with Docker or Docker Compose: build, configuration, profiles, checks |

## Reference (`docs/reference/`)

Information-oriented specifications.

| Document                                                           | Description                                                                        |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| [openapi_implementation.md](./reference/openapi_implementation.md) | The HTTP endpoints next to the MCP endpoint: health, OpenAPI documents, Swagger UI |
| [schema_validation.md](./reference/schema_validation.md)           | The input and response validation rules for every tool                             |

## Explanation (`docs/explanation/`)

Understanding-oriented discussion and implementation records.

| Document                                                                                       | Description                                                                |
| ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| [Migration to FastMCP 4 and httpx2](./explanation/fastmcp4_httpx2_migration_implementation.md) | What changed, what was found against a real EPR, and the release checklist |
| [Migration plan](./explanation/fastmcp4_httpx2_migration_implementation_plan.md)               | The phased plan the migration followed                                     |

## Demos

The [demos](../demos/README.md) are three runnable demonstrations with presenter
scripts and a rehearsal script. They are not documentation, so they live next to
the code.

## Conventions

Markdown file names are lowercase with underscores, except `README.md`. Every
markdown file passes `markdownlint --config .markdownlint.json` and
`prettier --parser markdown --prose-wrap always`.
