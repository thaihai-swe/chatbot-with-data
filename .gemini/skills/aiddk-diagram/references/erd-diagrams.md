# Entity Relationship Diagrams (ERD)

ERDs are used to represent database schemas and data relationships.

## Syntax Overview

- **Declaration**: `erDiagram`.
- **Entities**: `ENTITY_NAME { type field_name "description" }`.
- **Relationships**: `ENTITY_A relationship ENTITY_B : "label"`.
- **Cardinality**:
    - `|o`: Zero or one.
    - `||`: Exactly one.
    - `}o`: Zero or many.
    - `}|`: One or many.

## Example: E-commerce Schema
```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses
    ORDER ||--|{ PRODUCT : includes
    PRODUCT ||--o{ LINE-ITEM : "ordered in"

    CUSTOMER {
        string name
        string email
        string phone
    }
    ORDER {
        int orderNumber
        string deliveryAddress
    }
    LINE-ITEM {
        string productCode
        int quantity
        float pricePerUnit
    }
    PRODUCT {
        string name
        string code
        float price
    }
```

## Key Elements
- **Entities**: Represented by rectangles.
- **Attributes**: Listed inside the entity block.
- **Relationships**: Defined by lines between entities with cardinality markers.
- **Labels**: Optional text describing the relationship.
