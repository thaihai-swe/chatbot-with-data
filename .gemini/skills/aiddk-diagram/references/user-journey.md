# User Journey Diagrams

User Journey diagrams describe the steps a user takes to complete a task, capturing their emotional state and the friction points along the way.

## Syntax Overview

- **Title:** `journey` followed by `title: Name`
- **Sections:** `section Section Name`
- **Tasks:** `Task Name: score: Actor1, Actor2`
    - Score is 0-5 (0 is lowest/most friction).

## Examples

### Product Checkout
```mermaid
journey
    title User Buying a Product
    section Discovery
      Search for item: 5: User
      Browse results: 3: User
    section Selection
      Read reviews: 4: User
      Add to cart: 5: User
    section Checkout
      Enter shipping: 2: User
      Process payment: 1: User, System
      Confirmation: 5: User
```

### Onboarding Flow
```mermaid
journey
    title First-Time User Experience
    section Landing
      Visit home page: 4: Guest
      Click Sign Up: 5: Guest
    section Registration
      Enter email: 3: Guest
      Verify email: 1: Guest, System
    section Welcome
      Set profile: 4: User
      Take tour: 5: User
```

## Best Practices
- **Actor Clarity:** Clearly define who is performing the task (User vs. System).
- **Friction Identification:** Use low scores (1 or 2) to highlight where the implementation needs the most focus.
- **Goal Oriented:** Every journey should have a clear start and end goal.
