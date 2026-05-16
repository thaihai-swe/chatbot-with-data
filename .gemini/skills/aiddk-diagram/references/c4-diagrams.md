# C4 Model Diagrams

The C4 model is a lean graphical notation technique for modelling the architecture of software systems.

## 1. System Context Diagram
Shows the system in scope and its relationship with users and other systems.

```mermaid
C4Context
  title System Context diagram for Internet Banking System
  Person(customer, "Banking Customer", "A customer of the bank, with personal bank accounts.")
  System(banking_system, "Internet Banking System", "Allows customers to view information about their bank accounts, and make payments.")

  System_Ext(mail_system, "E-mail system", "The internal Microsoft Exchange e-mail system.")
  System_Ext(mainframe, "Mainframe Banking System", "Stores all of the core banking information about customers, accounts, transactions, etc.")

  Rel(customer, banking_system, "Uses")
  Rel_Back(customer, mail_system, "Sends e-mails to")
  Rel(banking_system, mail_system, "Sends e-mail using")
  Rel(banking_system, mainframe, "Uses")
```

## 2. Container Diagram
Zooms into the system in scope, showing the high-level technical building blocks.

```mermaid
C4Container
  title Container diagram for Internet Banking System
  Person(customer, "Customer", "A customer of the bank, with personal bank accounts.")
  System_Boundary(c1, "Internet Banking") {
    Container(web_app, "Web Application", "Java and Spring MVC", "Delivers the static content and the internet banking single page application.")
    Container(spa, "Single-Page Application", "JavaScript and Angular", "Provides all of the internet banking functionality to customers via their web browser.")
    Container(mobile_app, "Mobile App", "Xamarin", "Provides a limited subset of the internet banking functionality to customers via their mobile device.")
    ContainerDb(database, "Database", "Relational Database Schema", "Stores user registration information, hashed authentication credentials, access logs, etc.")
    Container(api, "API Application", "Java and Spring MVC", "Provides internet banking functionality via a JSON/HTTPS API.")
  }
  System_Ext(mail_system, "E-mail system", "The internal Microsoft Exchange e-mail system.")
  System_Ext(mainframe, "Mainframe Banking System", "Stores all of the core banking information about customers, accounts, transactions, etc.")

  Rel(customer, web_app, "Uses", "HTTPS")
  Rel(customer, spa, "Uses", "HTTPS")
  Rel(customer, mobile_app, "Uses")
  Rel(web_app, spa, "Delivers")
  Rel(spa, api, "Uses", "JSON/HTTPS")
  Rel(mobile_app, api, "Uses", "JSON/HTTPS")
  Rel_L(api, database, "Reads from and writes to")
  Rel(api, mail_system, "Sends e-mails using")
  Rel(api, mainframe, "Uses")
```

## 3. Component Diagram
Zooms into an individual container to show the components inside it.

```mermaid
C4Component
  title Component diagram for API Application
  Container_Boundary(api, "API Application") {
    Component(sign_in_controller, "Sign In Controller", "Spring MVC Rest Controller", "Allows users to sign in to the internet banking system.")
    Component(security_component, "Security Component", "Spring Bean", "Provides functionality related to signing in, changing passwords, etc.")
    Component(mfa_component, "MFA Component", "Spring Bean", "Provides functionality related to multi-factor authentication.")
  }
  ContainerDb(database, "Database", "Relational Database Schema", "Stores user registration information, hashed authentication credentials, access logs, etc.")

  Rel(sign_in_controller, security_component, "Uses")
  Rel(security_component, database, "Reads from and writes to")
  Rel(security_component, mfa_component, "Uses")
```

## Key Elements
- `Person(alias, label, [descr], [sprite], [tags])`
- `System(alias, label, [descr], [sprite], [tags])`
- `System_Ext(alias, label, [descr], [sprite], [tags])`
- `Container(alias, label, [techn], [descr], [sprite], [tags])`
- `ContainerDb(alias, label, [techn], [descr], [sprite], [tags])`
- `Component(alias, label, [techn], [descr], [sprite], [tags])`
- `Rel(from, to, label, [techn], [descr], [sprite], [tags])`
- `System_Boundary(alias, label)`
- `Container_Boundary(alias, label)`
