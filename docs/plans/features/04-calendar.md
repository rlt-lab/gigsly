# Calendar

## Overview

Calendar provides two views of your shows: a traditional month grid and a chronological agenda list.

## Month View

```
┌─ Calendar: February 2025 ─────────────────────────────────┐
│                                                           │
│ ◀ January          February 2025          March ▶        │
│                                                           │
│  Sun   Mon   Tue   Wed   Thu   Fri   Sat                 │
│ ─────────────────────────────────────────────────────────│
│                                    1*                     │
│                               Blue Note                   │
│                                                           │
│   2     3     4     5     6     7     8*                  │
│                                       Ryman               │
│                                                           │
│   9    10    11    12    13    14*   15                   │
│                               3rd&L                       │
│                                                           │
│  16    17    18    19    20    21    22                   │
│                                                           │
│  23    24    25    26    27    28                         │
│                                                           │
│ [Tab] Agenda  [←→] Navigate  [n] New Show  [Enter] Day   │
└───────────────────────────────────────────────────────────┘
```

### Color Coding

- **Blue**: Upcoming shows
- **Yellow**: Past shows, unpaid
- **Green**: Past shows, paid
- **Gray**: Past shows (default, paid)

### Day Detail (on Enter)

When pressing Enter on a date with shows:

```
┌─ February 1, 2025 ────────────────────────────────────────┐
│                                                           │
│ Shows:                                                    │
│  • The Blue Note - $200 (pending)                        │
│                                                           │
│ [n] Add show  [Enter] View show  [q] Close               │
└───────────────────────────────────────────────────────────┘
```

## Agenda View

```
┌─ Agenda ──────────────────────────────────────────────────┐
│ [Filter: Upcoming ▼]                                      │
│                                                           │
│ FEBRUARY 2025                                             │
│ ─────────────────────────────────────────────────────────│
│ Sat 1   The Blue Note           $200    pending          │
│ Sat 8   Ryman Auditorium        $350    pending          │
│ Fri 14  3rd & Lindsley          $175    pending          │
│                                                           │
│ MARCH 2025                                                │
│ ─────────────────────────────────────────────────────────│
│ Sat 1   The Blue Note           $200    pending          │
│ Sat 8   Exit/In                 $150    pending          │
│                                                           │
│ [Tab] Month  [n] New Show  [Enter] View  [q] Back        │
└───────────────────────────────────────────────────────────┘
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Toggle month/agenda view |
| `m` | Switch to month view |
| `a` | Switch to agenda view |
| `←` | Previous month (month view) |
| `→` | Next month (month view) |
| `t` | Jump to today |
| `n` | Add new show |
| `N` | Add show with new venue |
| `Enter` | View day detail (month) or show detail (agenda) |
| `q` | Go back |

## Filter Options (Agenda View)

- Upcoming (default)
- Past
- All
- This month
- Next 3 months

## Empty & Loading States

**Loading**: Show spinner in center of calendar grid.

**Empty (no shows in visible range)**:
- Month view: Calendar displays normally with no show markers
- Agenda view:
```
No shows in this time range.
Press [n] to add a show.
```

## Related Features

- [Shows](./03-shows.md)
- [Recurring Gigs](./05-recurring-gigs.md)
