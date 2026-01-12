# Quickstart: Context7 MCP Integration

**Feature**: 001-context7-mcp
**Date**: 2026-01-12

## Prerequisites

- GitHub repository with Claude Code Action configured
- Existing `.github/mcp-servers.json` file
- Node.js available on GitHub Actions runner (default on ubuntu-latest)

## Implementation Steps

### Step 1: Update MCP Configuration

Edit `.github/mcp-servers.json` to add the Context7 server entry:

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
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

### Step 2: (Optional) Add API Key for Higher Rate Limits

If you want higher rate limits, add a Context7 API key:

1. Get an API key from [context7.com/dashboard](https://context7.com/dashboard)
2. Add `CONTEXT7_API_KEY` to your repository secrets:
   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `CONTEXT7_API_KEY`
   - Value: Your API key

3. Update the configuration to use the secret:

```json
{
  "mcpServers": {
    "github": {...},
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "env": {
        "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
      }
    }
  }
}
```

4. Update your GitHub Action workflow to pass the secret:

```yaml
env:
  CONTEXT7_API_KEY: ${{ secrets.CONTEXT7_API_KEY }}
```

### Step 3: Test the Integration

Create a comment on an issue or PR to test:

```
@claude What are the latest Next.js 15 App Router conventions?
```

Claude should:
1. Use `resolve-library-id` to find Next.js library ID
2. Use `query-docs` to fetch relevant documentation
3. Respond with up-to-date information

### Step 4: Verify Both MCP Servers Work

Test that the existing GitHub MCP server still works:

```
@claude What are the open PRs in this repository?
```

Claude should use GitHub MCP tools to list PRs, confirming both servers coexist.

## Verification Checklist

- [ ] Context7 entry added to mcp-servers.json
- [ ] JSON syntax is valid (no trailing commas, proper quotes)
- [ ] Claude responds to library documentation questions
- [ ] GitHub MCP tools still work (list issues, PRs, etc.)
- [ ] (Optional) API key configured for production use

## Troubleshooting

### Context7 tools not appearing

1. Check JSON syntax in mcp-servers.json
2. Ensure npx is available (should be on ubuntu-latest)
3. Check GitHub Actions logs for MCP server startup errors

### Rate limiting errors

1. Consider adding a Context7 API key
2. API keys are free at context7.com/dashboard

### GitHub MCP stopped working

1. Ensure GitHub server entry is still present
2. Check that GH_TOKEN is still passed correctly
3. Verify no syntax errors broke the JSON file

## Rollback

To remove Context7 integration, simply delete the `context7` entry from mcp-servers.json:

```json
{
  "mcpServers": {
    "github": {...}
  }
}
```
