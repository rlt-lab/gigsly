# Keyboard Shortcuts Master List

## Global Navigation

Available from any screen (unless overridden by context):

| Key | Action | Notes |
|-----|--------|-------|
| `d` | Go to Dashboard | **Conflict**: See below |
| `v` | Go to Venues | |
| `s` | Go to Shows | Context-dependent on Venues detail |
| `c` | Go to Calendar | **Conflict**: See below |
| `r` | Go to Report | |
| `?` | Help overlay | |
| `Ctrl+,` | Settings | |
| `q` | Quit / Go back | Context-sensitive |
| `Esc` | Cancel / Close modal | Not documented, but expected |

## Screen-Specific Shortcuts

### Dashboard

| Key | Action |
|-----|--------|
| `v` | Go to Venues |
| `s` | Go to Shows |
| `c` | Go to Calendar |
| `r` | Go to Full Report |
| `Enter` | Activate selected item |
| `↑`/`↓` | Navigate items |
| `Ctrl+R` | Refresh stats |

### Venues Screen

#### List View

| Key | Action |
|-----|--------|
| `n` | Add new venue |
| `Enter` | View venue details |
| `/` | Focus search |
| `↑`/`↓` | Navigate list |
| `j`/`k` | Navigate list (vim-style) |
| `f` | Open filter menu |

#### Detail View

| Key | Action | Notes |
|-----|--------|-------|
| `e` | Edit venue | |
| `d` | Delete venue | Requires confirmation |
| `c` | Log contact | **Overrides global `c`** |
| `s` | View shows at this venue | **Overrides global `s`** |
| `h` | View contact history | NEW |

### Shows Screen

#### List View

| Key | Action |
|-----|--------|
| `n` | Quick add show (existing venue) |
| `N` | Add show with new venue |
| `Enter` | View/edit show details |
| `p` | Mark as paid (on selected show) |
| `i` | Mark invoice sent |
| `d` | Delete show | Requires confirmation |
| `/` | Focus search | NEW |
| `↑`/`↓` | Navigate list |
| `j`/`k` | Navigate list (vim-style) |
| `f` | Open filter menu | NEW |

#### Detail View

| Key | Action |
|-----|--------|
| `e` | Edit show |
| `p` | Mark as paid |
| `i` | Mark invoice sent |
| `d` | Delete show |

### Calendar Screen

#### Month View

| Key | Action |
|-----|--------|
| `Tab` | Switch to agenda view |
| `a` | Switch to agenda view |
| `←`/`h` | Previous month |
| `→`/`l` | Next month |
| `t` | Jump to today |
| `n` | Add new show |
| `N` | Add show with new venue |
| `Enter` | View day detail |
| `e` | Export to ICS |

#### Agenda View

| Key | Action |
|-----|--------|
| `Tab` | Switch to month view |
| `m` | Switch to month view |
| `↑`/`↓` | Navigate shows |
| `j`/`k` | Navigate shows (vim-style) |
| `n` | Add new show |
| `N` | Add show with new venue |
| `Enter` | View show detail |
| `f` | Open filter menu |
| `e` | Export to ICS |

### Report Screen

| Key | Action |
|-----|--------|
| `Enter` | View selected item details |
| `↑`/`↓` | Navigate items |
| `j`/`k` | Navigate items (vim-style) |
| `1` | Jump to "Get Paid" section | NEW |
| `2` | Jump to "Book Shows" section | NEW |
| `3` | Jump to "Stay in Touch" section | NEW |
| `Ctrl+R` | Refresh report |

### Settings Screen

| Key | Action |
|-----|--------|
| `Tab` | Next field |
| `Shift+Tab` | Previous field |
| `Enter` | Activate button / Save |
| `Esc` | Cancel and close |

### Modal Dialogs

| Key | Action |
|-----|--------|
| `Enter` | Confirm / Primary action |
| `Esc` | Cancel / Close |
| `Tab` | Next field/button |
| `Shift+Tab` | Previous field/button |
| `↑`/`↓` | Navigate options |

---

## Conflicts & Resolutions

### `d` Key Conflict

| Context | Current Behavior | Resolution |
|---------|------------------|------------|
| Global | Go to Dashboard | Keep |
| Venues detail | Delete venue | **Override global** - deletion is rare, requires confirmation |
| Shows list/detail | Delete show | **Override global** - context-specific |

**Rule**: On screens where `d` means "delete," global navigation to Dashboard is suppressed. Use `d` from Dashboard, Calendar, or Report to return to Dashboard.

### `c` Key Conflict

| Context | Current Behavior | Resolution |
|---------|------------------|------------|
| Global | Go to Calendar | Keep |
| Venues detail | Log contact | **Override global** - contact logging is primary action |

**Rule**: On Venues detail view, `c` logs contact. Use global navigation from other screens.

### `s` Key Conflict

| Context | Current Behavior | Resolution |
|---------|------------------|------------|
| Global | Go to Shows | Keep |
| Venues detail | View shows at this venue | **Override global** - context-specific (shows for THIS venue) |

**Rule**: On Venues detail, `s` shows venue-specific shows. Both are "shows" so this is intuitive.

### Conflict Resolution Matrix

Quick reference for what each key does in each context:

| Key | Dashboard | Venues List | Venues Detail | Shows List | Shows Detail | Calendar | Report |
|-----|-----------|-------------|---------------|------------|--------------|----------|--------|
| `d` | - | Dashboard | **Delete** | **Delete** | **Delete** | Dashboard | Dashboard |
| `c` | Calendar | Calendar | **Log Contact** | Calendar | Calendar | - | Calendar |
| `s` | Shows | Shows | **Venue's Shows** | - | - | Shows | Shows |
| `v` | Venues | - | - | Venues | Venues | Venues | Venues |
| `r` | Report | Report | Report | Report | Report | Report | - |
| `n` | - | New Venue | New Contact | New Show | - | New Show | - |
| `e` | - | - | Edit Venue | - | Edit Show | Export ICS | - |
| `p` | - | - | - | Mark Paid | Mark Paid | - | - |
| `i` | - | - | - | Invoice Sent | Invoice Sent | - | - |

**Bold** = Context override of global shortcut

---

## Consistency Rules

1. **`n` always creates**: New venue, new show, new contact
2. **`N` (shift+n)**: Create with additional entity (show + new venue)
3. **`e` always edits**: Edit the current item
4. **`d` always deletes**: Delete with confirmation (dangerous actions)
5. **`Enter` always activates**: View details, confirm action
6. **`/` always searches**: Focus search input
7. **`f` always filters**: Open filter menu
8. **`q` always goes back**: Exit current view
9. **`Esc` always cancels**: Close modal, cancel edit
10. **Vim keys optional**: `j`/`k` mirror `↑`/`↓`, `h`/`l` mirror `←`/`→`

---

## Missing Functionality (To Add)

| Shortcut | Screen | Action | Status |
|----------|--------|--------|--------|
| `/` | Shows | Search shows | NEW |
| `/` | Calendar | Search/jump to date | NEW |
| `f` | Shows | Filter menu | NEW |
| `f` | Calendar Agenda | Filter menu | NEW |
| `h` | Venues detail | View contact history | NEW |
| `j`/`k` | All lists | Vim-style navigation | NEW |
| `1`/`2`/`3` | Report | Jump to sections | NEW |
| `Ctrl+R` | Dashboard, Report | Refresh | NEW |

---

## Quick Reference Card

```
GLOBAL                          LISTS
─────────────────────           ─────────────────────
d  Dashboard                    n  New item
v  Venues                       N  New with extra
s  Shows                        e  Edit
c  Calendar                     d  Delete
r  Report                       /  Search
?  Help                         f  Filter
⌃, Settings                     ↑↓ or jk Navigate
q  Back/Quit                    Enter View

CALENDAR                        PAYMENTS
─────────────────────           ─────────────────────
Tab Toggle view                 p  Mark paid
←→  Navigate months             i  Invoice sent
t   Today
e   Export ICS
```

## Help Overlay (`?` key)

Pressing `?` from any screen shows a modal with context-sensitive shortcuts:

```
┌─ Keyboard Shortcuts ──────────────────────────────────────┐
│                                                           │
│  NAVIGATION              ACTIONS                          │
│  d  Dashboard            n  New item                      │
│  v  Venues               e  Edit                          │
│  s  Shows                d  Delete                        │
│  c  Calendar             /  Search                        │
│  r  Report               f  Filter                        │
│                                                           │
│  CURRENT SCREEN: Shows                                    │
│  p  Mark as paid                                          │
│  i  Mark invoice sent                                     │
│  N  New show + new venue                                  │
│                                                           │
│                              [q] Close                    │
└───────────────────────────────────────────────────────────┘
```

The help overlay shows global shortcuts plus shortcuts specific to the current screen.
