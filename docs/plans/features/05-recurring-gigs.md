# Recurring Gigs

## Overview

Recurring gigs define patterns for shows that repeat on a schedule. The system auto-generates individual show instances based on the pattern.

## Recurrence Patterns

| Pattern | Example | Fields Used |
|---------|---------|-------------|
| Weekly | Every Tuesday | day_of_week |
| Bi-weekly | Every other Wednesday | day_of_week, interval_weeks=2 |
| Monthly (date) | 15th of every month | day_of_month |
| Monthly (ordinal) | First Saturday of every month | ordinal, day_of_week |
| Custom | Every 3 weeks | interval_weeks |

## Creating a Recurring Gig

When adding a show, option to "Make this recurring":

```
┌─ New Recurring Gig ───────────────────────────────────────┐
│                                                           │
│ Venue:     The Blue Note                                  │
│ Pay:       $200                                           │
│                                                           │
│ ─── Recurrence Pattern ──────────────────────────────────│
│                                                           │
│ Repeats: [Weekly            ▼]                           │
│                                                           │
│ Every:   [Saturday          ▼]                           │
│                                                           │
│ Starting: [2025-02-01      ]                             │
│ Ending:   [No end date     ] (or specific date)          │
│                                                           │
│                        [Create]  [Cancel]                 │
└───────────────────────────────────────────────────────────┘
```

### Pattern Selection UI

**Weekly/Bi-weekly:**
```
Repeats: [Weekly ▼]
Every:   [Saturday ▼]
```

**Monthly (date):**
```
Repeats: [Monthly (same date) ▼]
On day:  [15 ▼]
```

**Monthly (ordinal):**
```
Repeats: [Monthly (same weekday) ▼]
On the:  [First ▼] [Saturday ▼]
```

**Custom:**
```
Repeats: [Custom ▼]
Every:   [3] weeks
```

## Instance Generation

- On app launch, auto-generate instances for next 3 months
- Generated shows have `recurring_gig_id` set
- Past instances are never regenerated
- Generation runs in background, non-blocking

## Editing Behavior

### Edit Single Instance

- Changes only affect that specific show
- Show retains link to recurring gig but has overridden values

### Edit Recurring Series

```
┌─ Edit Recurring Series ───────────────────────────────────┐
│                                                           │
│ Apply changes to:                                         │
│                                                           │
│ ○ This show only                                         │
│ ● This and all future shows                              │
│ ○ All shows in this series                               │
│                                                           │
│                        [Apply]  [Cancel]                  │
└───────────────────────────────────────────────────────────┘
```

## Skip/Cancel Instance

- Mark individual instance as `is_cancelled = true`
- Shows in list with strikethrough
- Not counted in stats or reports

## End a Recurring Gig

- Set `end_date` on the recurring gig record
- Future instances beyond end_date are not generated
- Existing instances remain

## Edge Cases

### Fifth Weekday Problem

For patterns like "5th Saturday of every month", some months don't have a 5th occurrence.

**Behavior**: Skip months without the specified occurrence. No show is generated for that month.

**Example**: "5th Saturday" pattern
- January 2025: Has 5th Saturday (Jan 29) → show generated
- February 2025: No 5th Saturday → no show generated
- March 2025: Has 5th Saturday (Mar 29) → show generated

### Month-End Dates

For "monthly on the 31st" pattern:
- Months with 31 days: Show on 31st
- Months with 30 days: Show on 30th
- February: Show on 28th (or 29th in leap year)

**Behavior**: Use last day of month when specified day doesn't exist.

### Year Boundary

Recurring instances continue across year boundaries. Tax reports calculate based on show date, not recurring gig creation date.

## Display in Show List

Recurring shows display with indicator:

```
Sat 8   The Blue Note  $200  pending  [↻ Weekly]
```

## Related Features

- [Data Model](./01-data-model.md)
- [Shows](./03-shows.md)
- [Calendar](./04-calendar.md)
