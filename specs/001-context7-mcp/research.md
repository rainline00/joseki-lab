# Research: Context7 MCP Integration

**Feature**: 001-context7-mcp
**Date**: 2026-01-12
**Status**: Complete

## Research Summary

This document captures all research findings for integrating Context7 MCP server into the Claude Code GitHub Actions workflow.

---

## 1. Context7 MCP Server Configuration

### Decision: Use npx-based local server with optional API key

### Rationale
- Context7 MCP can run without an API key for basic usage (rate-limited)
- The npx command `npx -y @upstash/context7-mcp` runs the server locally
- Optional `CONTEXT7_API_KEY` environment variable enables higher rate limits
- Local server approach is consistent with existing GitHub MCP server pattern

### Alternatives Considered
- **Remote HTTP endpoint** (`https://mcp.context7.com/mcp`): Rejected because it requires OAuth 2.0 flow which adds complexity for GitHub Actions integration
- **Docker container**: No official Docker image available; npx approach is simpler and more maintainable

### Configuration Format
```json
{
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"],
    "env": {
      "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
    }
  }
}
```

Note: The `CONTEXT7_API_KEY` is optional - the server works without it but with rate limits.

---

## 2. Context7 Tools Available

### Decision: Expose two primary tools for documentation lookup

### Rationale
Context7 provides a focused, two-tool API that covers the documented use cases:

1. **resolve-library-id**: Converts human-readable library names (e.g., "Next.js", "React") to Context7's internal library IDs
   - Input: `query` (search term), `libraryName` (optional specific name)
   - Output: Library ID in format like `/vercel/next.js`

2. **query-docs** (also called `get-library-docs`): Retrieves documentation content for a specific library
   - Input: `libraryId` (from resolve step), `query` (what to search for)
   - Output: Relevant documentation snippets

### Usage Flow
```
User asks: "How do I use Next.js App Router?"
↓
Claude calls: resolve-library-id(query: "Next.js")
↓
Returns: libraryId = "/vercel/next.js"
↓
Claude calls: query-docs(libraryId: "/vercel/next.js", query: "App Router")
↓
Returns: Relevant documentation about App Router
```

---

## 3. GitHub Actions Compatibility

### Decision: Use Node.js runtime available in ubuntu-latest runner

### Rationale
- GitHub Actions `ubuntu-latest` runner includes Node.js and npm by default
- npx command works out of the box without additional setup
- No Docker build step required (unlike a custom container approach)
- Consistent with how other npm-based MCP servers are configured

### Prerequisites Verified
- Node.js 18+ is available on ubuntu-latest
- npm/npx are pre-installed
- Network access to npm registry is available

---

## 4. Coexistence with GitHub MCP Server

### Decision: Add Context7 as a sibling entry in mcp-servers.json

### Rationale
- MCP protocol supports multiple servers running simultaneously
- Each server is independent with its own tools namespace
- No conflicts between GitHub MCP tools and Context7 tools
- Existing GitHub MCP configuration remains unchanged

### Implementation
```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GH_TOKEN}" }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "env": {}
    }
  }
}
```

---

## 5. Error Handling Strategy

### Decision: Graceful degradation when Context7 is unavailable

### Rationale
- Context7 is an enhancement, not a critical dependency
- Claude should continue functioning if Context7 fails
- User should be informed when live docs lookup is unavailable

### Error Scenarios
| Scenario | Handling |
|----------|----------|
| Context7 service timeout | Claude falls back to training knowledge, informs user |
| Library not found | Claude indicates library not in Context7, uses training data |
| Network error | Claude proceeds without Context7, mentions unavailability |
| Invalid API key | Server fails to start, Claude Code action may fail |

### Recommendation
Do not make Context7 a required server - if configuration is present but server fails to start, Claude Code should still run with other MCP servers.

---

## 6. API Key Management

### Decision: Optional API key via GitHub Secrets

### Rationale
- Context7 works without API key (rate-limited)
- For production use, API key provides higher rate limits
- GitHub Secrets is the standard way to pass sensitive values to Actions

### Implementation Options
1. **No API key** (default): Works out of box, suitable for testing
2. **With API key**: User adds `CONTEXT7_API_KEY` to repository secrets

### Action Configuration
```yaml
env:
  CONTEXT7_API_KEY: ${{ secrets.CONTEXT7_API_KEY }}
```

Note: If secret is not set, env var will be empty and server runs in rate-limited mode.

---

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Does Context7 require authentication? | No, works without API key (rate-limited) |
| Is Docker required? | No, npx works directly on GitHub Actions runner |
| Will it conflict with GitHub MCP? | No, MCP supports multiple servers |
| What tools are available? | `resolve-library-id` and `query-docs` |
| How to handle failures? | Graceful degradation, inform user |

---

## References

- Context7 MCP Repository: https://github.com/upstash/context7-mcp
- Context7 Dashboard (API keys): https://context7.com/dashboard
- MCP Protocol Specification: https://modelcontextprotocol.io
