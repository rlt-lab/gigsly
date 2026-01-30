# Tech Stack

## Core Technologies

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.14 | Latest version, excellent ecosystem |
| Package Manager | UV | Fast, modern Python tooling |
| TUI Framework | Textual | Modern async TUI with CSS styling, rich widgets |
| Database | SQLite | Single-file, portable, no server required |
| ORM | SQLAlchemy | Type-safe queries, migrations support |
| CLI | Click | Clean argument parsing, integrates with Textual |
| Config | TOML | Human-readable, standard Python config format |
| Validation | Pydantic | Data validation and settings management |
| Calendar | icalendar | ICS file parsing and generation |

## Dependencies

```toml
[project]
dependencies = [
    "textual>=0.50.0",
    "sqlalchemy>=2.0.0",
    "click>=8.1.0",
    "pydantic>=2.0.0",
    "icalendar>=5.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
]
```

## Data Storage

- **Database location**: `~/.gigsly/gigsly.db`
- **Config location**: `~/.gigsly/config.toml`
- **Backup format**: JSON export

## Design Decisions

### Why Textual over alternatives?

- **vs Rich + prompt_toolkit**: Textual provides complete widget system, less manual work
- **vs Urwid**: Textual has modern async architecture, CSS-like styling
- **vs Web UI**: TUI offers keyboard efficiency, terminal aesthetic, SSH portability

### Why SQLite over alternatives?

- **vs JSON files**: Better query performance, ACID transactions, handles growth
- **vs PostgreSQL**: No server setup, single file for easy backup/portability
- **vs Cloud DB**: Works offline, no account required, data stays local

### Why Click over argparse?

- Cleaner decorator-based syntax
- Built-in help generation
- Plays well with Textual's async architecture
