# Class Diagrams

Class diagrams are used for object-oriented design and domain modeling.

## Syntax Overview

- **Declaration**: `classDiagram`.
- **Classes**: `class ClassName { +type attribute\n+method() }`.
- **Visibility**:
    - `+`: Public.
    - `-`: Private.
    - `#`: Protected.
    - `~`: Package/Internal.
- **Relationships**:
    - `<--`: Inheritance.
    - `*--`: Composition.
    - `o--`: Aggregation.
    - `-->`: Association.
    - `..>`: Dependency.
    - `..|>`: Realization/Interface implementation.

## Example: Library System
```mermaid
classDiagram
    class Book {
        +String title
        +String author
        +ISBN isbn
        +isAvailable() bool
    }
    class Member {
        +String name
        +int memberId
        +borrow(Book)
        +return(Book)
    }
    class Librarian {
        +addBook(Book)
        +removeBook(Book)
    }
    class Loan {
        +Date dueDate
        +isOverdue() bool
    }

    Member "1" -- "0..*" Loan : "has"
    Book "1" -- "0..*" Loan : "is for"
    Librarian --|> Member : "is a"
```

## Key Elements
- **Classes**: Blocks with name, attributes, and methods.
- **Interfaces**: Use `<<interface>>` stereotype.
- **Abstract Classes**: Use `<<abstract>>` stereotype.
- **Annotations**: Use `<<annotation>>`.
