# UI Panel Restructure — Mockup

## Layout: Three-Panel Workspace

```
┌──────────────────────────────────────────────────────────────────┐
│  TOP HEADER (sticky, 64px)                                       │
│  [K] KnowledgeBaseLab    [Library] [Chat] [Playground] [Eval] ☀️│
├──────────┬───────────────────────────────────┬───────────────────┤
│          │                                   │                   │
│  📄 ◀    │                                   │  🎨 ◀            │
│  SOURCES │          CHAT PANEL               │  STUDIO           │
│  PANEL   │                                   │  PANEL            │
│          │                                   │                   │
│  ======= │  ┌─────────────────────────────┐  │  ┌─────────────┐  │
│  📁 Q3   │  │  📝 Q: Summarize Q3 trends  │  │  │✨ Study Guide│  │
│  Reports │  │  A: [streaming response...] │  │  │📋 Briefing   │  │
│          │  │  [Source 1] [Source 2]      │  │  │❓ FAQ        │  │
│  ☑ Rev.  │  │                             │  │  │📅 Timeline   │  │
│    .pdf  │  │  ──── conflict warning ──── │  │  │📖 Glossary   │  │
│  ☑ Q3    │  │  ⚠️ Sources contradict...   │  │  │🃏 Flashcards  │  │
│  .xls    │  │                             │  │  └─────────────┘  │
│  ☐ Notes │  │  🦅 [Pipeline X-Ray]        │  │                   │
│    .md   │  │                             │  │  ┌─ History ───┐ │
│          │  │  ┌─ composer ─────────────┐ │  │  │Study Guide  │ │
│          │  │  │ [+ Generate ▼] Ask...  │ │  │  │ 12:30pm     │ │
│          │  │  └────────────────────────┘ │  │  │FAQ          │ │
│          │  │                             │  │  │ 12:15pm     │ │
│          │  │  ➕ generate a message:     │  │  └─────────────┘ │
│          │  │  ┌──────────────────────┐  │  │                   │
│          │  │  │✨ **Study Guide**    │  │  │                   │
│          │  │  │Key concepts from Q3  │  │  │                   │
│          │  │  │Reports...            │  │  │                   │
│          │  │  └──────────────────────┘  │  │                   │
├──────────┴───────────────────────────────────┴───────────────────┤
│  status bar (optional)                                           │
└──────────────────────────────────────────────────────────────────┘
```

## Panel Behaviors

### Sources Panel (Left)
| State | Behavior |
|-------|----------|
| **Default (collapsed)** | 📄 icon strip visible. Chat fills full width. |
| **Expanded (~320px)** | Collection picker (dropdown). Documents listed with checkboxes (all checked by default). "View" opens SourceBrowser inline. Upload button at top. |
| **No collection selected** | Prompt: "Select a collection to start." Chat input and generate buttons disabled/hidden. |
| **Collection selected** | Documents appear with checkboxes. Chat enables. |

### Chat Panel (Center)
| State | Behavior |
|-------|----------|
| **No collection** | Empty state: "Select a collection from Sources to begin." Input disabled. |
| **Collection selected** | Input enabled. Session list accessible. Standard chat interactions (SSE, citations, hover, X-Ray, conflict warnings). |
| **Generate button** | `[+ Generate ▼]` dropdown in composer toolbar. Options: Study Guide, Briefing Doc, FAQ, Timeline, Glossary, Flashcards. Inserts assistant message with result. |
| **Generated product in chat** | Renders as assistant message. Text products = formatted markdown. Flashcards = Q&A list. |

### Studio Panel (Right)
| State | Behavior |
|-------|----------|
| **Default (collapsed)** | 🎨 icon strip visible. |
| **Expanded (~300px)** | Generate buttons (6 types). Product history list (scrollable, newest first). Click a history item to scroll to/reopen that product in chat. |
| **Generation in progress** | Loading spinner on the button. Disabled until complete. |

## States & Transitions

### Empty State (No Collection Selected)
```
┌──────────────────────────────────────┐
│  📄  │                               │  🎨
│      │    ┌─────────────────────┐    │
│      │    │                     │    │
│      │    │   Select a          │    │
│      │    │   collection from   │    │
│      │    │   Sources to begin  │    │
│      │    │                     │    │
│      │    │   (input disabled)  │    │
│      │    └─────────────────────┘    │
└──────────────────────────────────────┘
```

### Full Workspace (Collection Selected, Panels Expanded)
```
┌──────────────────────────────────────────────┐
│  📄 Q3 Reports ▼  │  Chatting with Q3... │ 🎨│
│  ☑ Annual Rev.pdf │  [messages]          │   │
│  ☑ Q3 Breakdown   │  [+ Generate ▼] Ask  │   │
│  ☐ Notes.md       │                      │   │
└──────────────────────────────────────────────┘
```

### Mobile (≤768px)
Bottom tab bar with 3 icons: [📄 Sources] [💬 Chat] [🎨 Studio]. One panel visible at a time. Tab switches panel.
