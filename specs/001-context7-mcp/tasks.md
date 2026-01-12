# Tasks: Context7 MCP Integration

**Input**: Design documents from `/specs/001-context7-mcp/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No tests requested - this is a configuration-only change with manual validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

This feature is a **configuration-only change**. The only modified file is:
- `.github/mcp-servers.json` - MCP server configuration

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the repository for Context7 MCP integration

- [x] T001 Review existing MCP configuration in .github/mcp-servers.json
- [x] T002 Verify JSON syntax is valid and backup current state

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Ensure MCP infrastructure supports multiple servers

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Verify mcpServers object structure in .github/mcp-servers.json supports multiple entries
- [x] T004 Confirm GitHub Actions runner has Node.js/npx available (ubuntu-latest includes this)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Library Documentation Lookup (Priority: P1) MVP

**Goal**: Enable Claude Code to access up-to-date library documentation through Context7 MCP tools

**Independent Test**: Ask Claude "@claude What are the latest Next.js 15 App Router conventions?" and verify Claude uses Context7 to fetch current documentation

### Implementation for User Story 1

- [x] T005 [US1] Add context7 server entry to mcpServers in .github/mcp-servers.json with command "npx", args ["-y", "@upstash/context7-mcp"], and empty env object
- [x] T006 [US1] Validate JSON syntax is correct after modification in .github/mcp-servers.json
- [x] T007 [US1] Verify context7 entry coexists with github entry in .github/mcp-servers.json

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Version-Specific Documentation (Priority: P2)

**Goal**: Enable Claude to retrieve documentation for specific library versions

**Independent Test**: Ask Claude "What breaking changes were introduced in React 18?" and verify the response matches official documentation

### Implementation for User Story 2

- [x] T008 [US2] (Optional) Add CONTEXT7_API_KEY environment variable reference to context7 entry in .github/mcp-servers.json for enhanced rate limits (skipped - works without API key)
- [x] T009 [US2] Document API key setup process in repository secrets (Settings -> Secrets -> CONTEXT7_API_KEY) - see quickstart.md

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validation and documentation improvements

- [ ] T010 Manual validation: Trigger Claude Code via GitHub comment with library question (post-merge)
- [ ] T011 Manual validation: Verify existing GitHub MCP tools still work (list issues, PRs) (post-merge)
- [ ] T012 Manual validation: Test graceful degradation if Context7 is unavailable (post-merge)
- [ ] T013 Run quickstart.md validation steps (post-merge)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion (builds on same config)
- **Polish (Phase 5)**: Depends on User Story 1 completion (minimum)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after User Story 1 - Builds on the same configuration file

### Within Each User Story

- Single configuration file means tasks are sequential within a story
- Each task modifies .github/mcp-servers.json
- Validate JSON syntax after each modification

### Parallel Opportunities

- T001 and T002 can run in parallel (both are read-only)
- T003 and T004 can run in parallel (verification tasks)
- T010, T011, T012 can run in parallel (independent validation tests)

---

## Parallel Example: Validation Phase

```bash
# Launch all validation tests together:
Task: "Manual validation: Trigger Claude Code via GitHub comment with library question"
Task: "Manual validation: Verify existing GitHub MCP tools still work"
Task: "Manual validation: Test graceful degradation if Context7 is unavailable"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (review existing config)
2. Complete Phase 2: Foundational (verify infrastructure)
3. Complete Phase 3: User Story 1 (add Context7 entry)
4. **STOP and VALIDATE**: Test library documentation lookup
5. Deploy/merge if ready

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add User Story 1 -> Test independently -> Deploy (MVP!)
3. Add User Story 2 (API key) -> Test independently -> Deploy
4. Each story adds value without breaking previous functionality

### Quick Implementation Path

Since this is a configuration-only change:

1. **T001-T004**: 5 minutes - Verify existing setup
2. **T005-T007**: 5 minutes - Add Context7 entry and validate
3. **T008-T009**: 5 minutes - Optional API key setup
4. **T010-T013**: 15 minutes - Manual validation

**Total estimated effort**: 30 minutes for full implementation and validation

---

## Final Configuration

After completing all tasks, `.github/mcp-servers.json` should contain:

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

---

## Notes

- [P] tasks = different files, no dependencies (limited in this config-only feature)
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each logical task group
- Stop at any checkpoint to validate story independently
- Rollback: Remove `context7` key from `mcpServers` object
