# Implementation Plan: Context7 MCP Integration

**Branch**: `001-context7-mcp` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-context7-mcp/spec.md`

## Summary

Enable Claude Code on GitHub Actions to access up-to-date library documentation through Context7 MCP server. The implementation adds Context7 MCP configuration to the existing `.github/mcp-servers.json` file, allowing Claude to use `resolve-library-id` and `query-docs` tools for real-time documentation lookup.

## Technical Context

**Language/Version**: JSON configuration (no application code)
**Primary Dependencies**: `@upstash/context7-mcp` npm package (run via npx)
**Storage**: N/A (stateless MCP server)
**Testing**: Manual integration testing via GitHub Actions
**Target Platform**: GitHub Actions ubuntu-latest runner (Node.js pre-installed)
**Project Type**: Configuration change (no source code structure needed)
**Performance Goals**: Documentation responses within 30 seconds (Context7 SLA)
**Constraints**: Must not break existing GitHub MCP server functionality
**Scale/Scope**: Single repository configuration

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution template has placeholder values and no specific gates defined. This feature:
- **Minimal change**: Single configuration file modification
- **No new dependencies**: Uses npx for runtime package fetch
- **Non-breaking**: Additive change to existing MCP configuration
- **Reversible**: Can be removed by deleting the `context7` entry

**Status**: ✅ Pass - No violations identified

## Project Structure

### Documentation (this feature)

```text
specs/001-context7-mcp/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 research output
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Implementation guide
├── contracts/           # Phase 1: API contracts
│   └── mcp-config.json  # MCP configuration schema
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
.github/
└── mcp-servers.json     # Modified: Add Context7 server entry
```

**Structure Decision**: Configuration-only change. No source code directories needed. The only file modification is `.github/mcp-servers.json`.

## Implementation Approach

### Phase 1: Configuration Change

1. **Modify `.github/mcp-servers.json`**
   - Add `context7` entry to `mcpServers` object
   - Use npx command: `npx -y @upstash/context7-mcp`
   - Include optional `CONTEXT7_API_KEY` environment variable

2. **Final Configuration**
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

### Phase 2: Validation

1. **Test Context7 availability**
   - Trigger Claude Code via GitHub comment
   - Ask about a library: "@claude What are the Next.js 15 App Router conventions?"
   - Verify Context7 tools are invoked

2. **Test graceful degradation**
   - Verify GitHub MCP tools still work alongside Context7
   - Test behavior when Context7 service is slow/unavailable

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Context7 npm package unavailable | Low | Medium | npx has npm registry fallback; can revert config |
| Rate limiting without API key | Medium | Low | Optional API key can be added via secrets |
| Breaking existing GitHub MCP | Low | High | Additive change only; test both servers |

## Complexity Tracking

No constitution violations requiring justification.

## Dependencies

- **External**: `@upstash/context7-mcp` npm package
- **Internal**: Existing `.github/mcp-servers.json` structure
- **Infrastructure**: GitHub Actions ubuntu-latest runner with Node.js

## Success Criteria Mapping

| Spec Criteria | Implementation Validation |
|---------------|--------------------------|
| SC-001: Claude invokes Context7 tools | Manual test: Ask library question, verify tool usage in logs |
| SC-002: Response within 30 seconds | Manual test: Time documentation responses |
| SC-003: GitHub MCP still works | Manual test: Use existing GitHub tools after change |
| SC-004: 95% accuracy for popular libs | Manual test: Query React, Next.js, Vue documentation |
