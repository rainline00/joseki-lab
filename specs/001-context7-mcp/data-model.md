# Data Model: Context7 MCP Integration

**Feature**: 001-context7-mcp
**Date**: 2026-01-12

## Overview

This feature primarily involves configuration data rather than application entities. The data model describes the MCP server configuration structure and the Context7 tool interfaces.

---

## Entities

### 1. MCP Server Configuration

The root configuration object that defines all MCP servers available to Claude Code.

**Location**: `.github/mcp-servers.json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mcpServers` | Object | Yes | Container for all server definitions |

### 2. MCP Server Entry

Individual server definition within the `mcpServers` object.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | String | Yes | Executable to run (e.g., `npx`, `docker`) |
| `args` | String[] | Yes | Command arguments |
| `env` | Object | No | Environment variables to pass |

### 3. Context7 Server Entry

Specific configuration for the Context7 MCP server.

```json
{
  "command": "npx",
  "args": ["-y", "@upstash/context7-mcp"],
  "env": {
    "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
  }
}
```

| Field | Value | Description |
|-------|-------|-------------|
| `command` | `"npx"` | Node package executor |
| `args[0]` | `"-y"` | Auto-accept package installation |
| `args[1]` | `"@upstash/context7-mcp"` | Context7 MCP npm package |
| `env.CONTEXT7_API_KEY` | Variable reference | Optional API key for higher rate limits |

---

## Tool Interfaces

### 1. resolve-library-id Tool

Resolves a human-readable library name to a Context7-compatible library ID.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search term for the library"
    },
    "libraryName": {
      "type": "string",
      "description": "Optional specific library name"
    }
  },
  "required": ["query"]
}
```

**Output**:
```json
{
  "libraryId": "/vercel/next.js"
}
```

### 2. query-docs Tool

Retrieves documentation content for a specific library.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "libraryId": {
      "type": "string",
      "description": "Context7-compatible library ID (e.g., /mongodb/docs)"
    },
    "query": {
      "type": "string",
      "description": "Search query for documentation content"
    }
  },
  "required": ["libraryId", "query"]
}
```

**Output**:
```json
{
  "content": "Documentation content...",
  "source": "https://docs.example.com/page",
  "sections": [
    {
      "title": "Section Title",
      "content": "Section content..."
    }
  ]
}
```

---

## Relationships

```text
mcp-servers.json
└── mcpServers (Object)
    ├── github (Server Entry) - Existing
    │   ├── command: "docker"
    │   ├── args: [...]
    │   └── env: {...}
    └── context7 (Server Entry) - NEW
        ├── command: "npx"
        ├── args: ["-y", "@upstash/context7-mcp"]
        └── env: {CONTEXT7_API_KEY?: string}
```

---

## Validation Rules

### MCP Configuration Validation

1. **mcpServers must be an object** - Top-level key required
2. **Each server must have command** - String, non-empty
3. **Each server must have args** - Array of strings
4. **env is optional** - If present, must be object with string values

### Context7 Specific Validation

1. **command must be "npx"** - For Context7 server
2. **args must include package name** - `@upstash/context7-mcp`
3. **CONTEXT7_API_KEY is optional** - Server works without it (rate-limited)

---

## State Transitions

This feature involves static configuration. No runtime state transitions.

| State | Trigger | Result |
|-------|---------|--------|
| Server Unconfigured | Add `context7` entry | Server Available |
| Server Available | Claude requests docs | Tools Invoked |
| Server Available | Remove entry | Server Unconfigured |

---

## Data Migration

No data migration required. This is an additive configuration change.

**Before**:
```json
{
  "mcpServers": {
    "github": {...}
  }
}
```

**After**:
```json
{
  "mcpServers": {
    "github": {...},
    "context7": {...}
  }
}
```

**Rollback**: Remove `context7` key from `mcpServers` object.
