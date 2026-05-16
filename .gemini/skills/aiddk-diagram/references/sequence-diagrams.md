# Sequence Diagrams

Sequence diagrams are used to represent the interactions between multiple actors or systems over time.

## Syntax Overview

- **Declaration**: `sequenceDiagram`.
- **Participants**:
    - `participant Alice`: Standard participant.
    - `actor Bob`: Actor icon.
- **Messages**:
    - `A -> B`: Solid line without arrow.
    - `A ->> B`: Solid line with arrowhead.
    - `A -->> B`: Dashed line with arrowhead.
    - `A -x B`: Solid line with cross.
    - `A --x B`: Dashed line with cross.
- **Activations**:
    - `activate Alice` / `deactivate Alice`.
    - `A ->>+ B`: Arrow with activation of B.
    - `A -->>- B`: Arrow with deactivation of B.
- **Notes**:
    - `Note right of Alice: Text`.
    - `Note left of Bob: Text`.
    - `Note over Alice, Bob: Text`.
- **Loops and Logic**:
    - `loop Description ... end`.
    - `alt Case A ... else Case B ... end`.
    - `opt Optional Case ... end`.
    - `parallel Parallel Action ... end`.

## Examples

### OAuth2 Authorization Code Flow
```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant App
    participant AuthServer

    User ->> Browser: Visit App
    Browser ->> App: Request Home Page
    App -->> Browser: Redirect to AuthServer
    Browser ->> AuthServer: GET /authorize
    AuthServer -->> User: Login Page
    User ->> AuthServer: Credentials
    AuthServer -->> Browser: Redirect to App with Code
    Browser ->> App: GET /callback?code=123
    App ->> AuthServer: POST /token (code=123)
    AuthServer -->> App: Access Token
    App -->> Browser: Authenticated Session
```

### Microservice Interaction
```mermaid
sequenceDiagram
    participant Gateway
    participant OrderSvc
    participant InventorySvc
    participant PaymentSvc

    Gateway ->>+ OrderSvc: Create Order
    OrderSvc ->>+ InventorySvc: Check Stock
    InventorySvc -->>- OrderSvc: In Stock
    OrderSvc ->>+ PaymentSvc: Process Payment
    alt Payment Success
        PaymentSvc -->> OrderSvc: Success
        OrderSvc -->> Gateway: Order Confirmed
    else Payment Failed
        PaymentSvc -->>- OrderSvc: Failed
        OrderSvc -->>- Gateway: Order Rejected
    end
```

## Advanced Features

### Autonumbering
```mermaid
sequenceDiagram
    autonumber
    Alice->>Bob: Hello Bob, how are you?
    loop Healthcheck
        Bob->>Alice: Better now; thanks for asking!
    end
```

### Styling
```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    rect rgb(191, 223, 255)
    note right of Alice: Alice calls Bob.
    Alice->>Bob: Hello Bob, how are you?
    end
```
