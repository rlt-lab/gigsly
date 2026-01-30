# Gigsly Project Rules

## Working Style

### Use Sub-Agents Liberally
- Spawn sub-agents for any task that can be parallelized
- Use the `Explore` agent for codebase searches instead of manual grep/glob
- Use the `Plan` agent when designing new features or significant changes
- Use specialized review agents after completing implementation work
- When multiple independent tasks exist, launch them in parallel with a single message containing multiple Task tool calls

### Use Skills Proactively
- Check available skills before starting any significant work
- Use `superpowers:brainstorming` before implementing new features
- Use `superpowers:writing-plans` for multi-step implementation tasks
- **Always use `superpowers:test-driven-development`** - this is mandatory for all new functionality
- Use `superpowers:systematic-debugging` when encountering bugs
- Use `superpowers:verification-before-completion` before claiming work is done

### MCP Server Access
The MCP_DOCKER server provides access to multiple integrated services:
- **Browser automation** - Use for testing UI, taking screenshots, web interactions
- **File operations** - Extended file management capabilities
- **Memory/knowledge graph** - Store and retrieve project knowledge
- **Context7** - Fetch up-to-date library documentation
- **Greptile** - Code search and review capabilities

Use `ToolSearch` to discover and load MCP tools before calling them.

## Project Constants

### Documentation Location
- All design docs live in `docs/plans/features/`
- Task list is `docs/TASK_LIST.md` - update checkboxes as work completes
- Tech decisions go in `docs/TECH_STACK.md`

### Data Storage
- User data: `~/.gigsly/`
- Database: `~/.gigsly/gigsly.db`
- Config: `~/.gigsly/config.toml`

### Code Organization
```
gigsly/
├── cli.py          # Click entry points
├── app.py          # Textual application
├── db/             # Database layer
├── screens/        # TUI screens
├── widgets/        # Reusable components
└── config.py       # Settings management
```

## Rules

1. **Task List is Source of Truth** - Before implementing, check `docs/TASK_LIST.md`. Mark tasks in progress when starting, completed when done.

2. **Feature Specs are Contracts** - Implementation must match the specs in `docs/plans/features/`. If a spec needs changing, update the doc first.

3. **Keyboard-First Design** - Every action must be accessible via keyboard. Mouse is optional.

4. **Money Comes First** - In reports and UI, payment-related items always have highest priority.

5. **No Silent Failures** - All errors must surface to the user with actionable messages.

6. **Test-Driven Development** - Always write tests BEFORE implementation code:
   - Write failing tests that define expected behavior
   - Implement minimum code to make tests pass
   - Refactor while keeping tests green
   - Run `uv run pytest` before any commit

7. **Minimal Dependencies** - Only add packages that provide significant value. Prefer stdlib when reasonable.

## Commit Style

Use conventional commits:
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `refactor:` code restructuring
- `test:` adding/updating tests
- `chore:` maintenance tasks
