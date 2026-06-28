# GitNexus Prompts for Developer Onboarding

Welcome to the project! GitNexus is a Code Intelligence Engine that turns this codebase into a highly interconnected knowledge graph. Since you are new to the codebase, the standard text search (`grep` or `Cmd+F`) might not give you the full context you need. 

Below is a curated list of prompts you can give to your AI coding assistant (like Antigravity or OpenCode) to help you rapidly understand the backend architecture, trace execution flows, and make safe changes without breaking existing features.

---

## 1. Initial Orientation (Getting the Lay of the Land)
When you first clone the repository, use these prompts to map out how the backend is structured at a high level.

* *"I just joined this project. Use GitNexus to map out the core architectural clusters in this backend. What are the main functional domains (e.g., Auth, Payments, Users) and how do they interact?"*
* *"Identify the primary entry points for this backend using GitNexus. Where do HTTP requests or external events first enter the application? List the main routers or controller files."*
* *"Use GitNexus to find all the interfaces, base classes, or core types related to our database models. I want to understand the main data structures we are working with."*
* *"Which files or classes act as the central 'glue' for this backend? Use GitNexus to find the symbols with the highest number of incoming and outgoing dependencies."*

## 2. Tracing Data & Execution Flows
Instead of jumping from file to file manually, let GitNexus trace the exact path a request takes through the system.

* *"I need to understand the 'User Authentication' flow. Trace it using GitNexus. Start from the login endpoint and show me every function call, middleware, and database query involved in the process."*
* *"We use a specific service for 'Payment Processing'. Can you use GitNexus to query for the payment process and show me the step-by-step execution trace of how a payment is handled?"*
* *"How does the backend handle data validation? Use GitNexus to find where incoming request payloads are validated and trace how validation errors are returned to the client."*
* *"Find the main database connection setup using GitNexus. Trace its downstream dependencies to show me how database instances are injected into our repositories or services."*

## 3. Deep-Dive into Specific Symbols (The 360-Degree View)
When you are assigned a ticket to work on a specific function or class, use these prompts to get complete context before you start coding.

* *"I need to modify `UserService`. Use the GitNexus context tool to give me a 360-degree view of this class. Show me all of its callers, the services it imports, and the specific execution flows it participates in."*
* *"What exactly does the `verifySignature` function do? Use GitNexus to find it, explain its logic, and list every other function that calls it."*
* *"I am looking at the `BaseController` class. Use GitNexus to find all classes that inherit from it or implement its interface. I want to see how it is extended across the project."*

## 4. Safety & Blast Radius Analysis (Pre-Refactoring)
As a new developer, your biggest fear is likely breaking something you didn't know existed. Use GitNexus to guarantee safety.

* *"I am assigned to refactor the `processOrder` function. Before we write any code, run a GitNexus impact analysis on it and report the blast radius. What API endpoints and background workers will be affected if I change its signature?"*
* *"Run an upstream impact analysis on `database.config.ts`. If I change the connection string logic, exactly which files and execution flows will break?"*
* *"I think the `calculateDiscount` function is no longer used. Use GitNexus to verify if it has any upstream callers. Is it safe to delete this dead code?"*
* *"I need to rename the `handleData` function to `processWebhookPayload`. Use GitNexus to perform a multi-file rename so we don't miss any indirect references or imports."*

## 5. Reviewing and Detecting Changes (Pre-Commit)
Before you push your first pull request, use these prompts to ensure your changes only affect what you intended to change.

* *"I just finished my ticket. Run the GitNexus `detect_changes` tool to verify my uncommitted changes. Tell me which execution processes I have affected and if there is a high risk of breaking unintended systems."*
* *"Analyze my current git diff using GitNexus. Does my change to `AuthMiddleware` unintentionally affect the `BillingFlow` cluster?"*

---

## 6. Code Disambiguation & Framework Pattern Detection
When a repository has multiple functions with the same name or relies heavily on framework decorators, use these prompts.

* *"There are multiple `get_embeddings` functions in this repository. Use GitNexus impact analysis but disambiguate by targeting the specific one in `src/embed.py` (or use its exact `uid`)."*
* *"We use a lot of decorators (like `@Controller` or `@Get`) in this backend. Use GitNexus to map out all the API endpoints defined by these framework decorators and trace their immediate dependencies."*
* *"Find all instances of the `validateUser` function. List them out and explain how their usage differs across different modules or files."*

## 7. Generating Documentation (Code Wiki)
GitNexus can generate LLM-powered documentation by reading the graph structure.

* *"The documentation for this backend module is out of date. Can you run the `gitnexus wiki` command on this directory to generate a fresh, LLM-powered README based on the actual codebase graph?"*
* *"Run the GitNexus wiki generator on the `src/services` folder to map out how our core business logic services relate to each other in documentation format."*

## 8. Advanced Graph Exploration (Cypher Queries)
For complex architectural questions, GitNexus supports direct Cypher queries (like Neo4j) to query the embedded LadybugDB graph.

* *"I need to find all functions related to 'Authentication' that are called with a high confidence score. Can you write and execute a Cypher query against GitNexus to find these relationships?"*
* *"Write a Cypher query for GitNexus that finds all controllers that directly call the database repository layer without passing through a service layer (violating our architecture). "*

## 9. Object-Oriented Heritage & Cross-File Resolution
If you are working in an OOP language (TypeScript, Java, C#, etc.) and need to track inheritance or complex re-exports.

* *"This interface is implemented by multiple classes. Use GitNexus to find every class that `IMPLEMENTS` the `PaymentGateway` interface."*
* *"How is the `DatabaseConnection` class extended across the project? Use GitNexus to track its inheritance heritage (`EXTENDS`) down the chain."*
* *"We re-export a lot of types in our `index.ts` files. Use GitNexus to trace the named bindings of `UserAuthToken` back to its original source file definition."*

---

**💡 Pro-Tip for Agentic Coding:** 
You can combine these actions into powerful, multi-step agent workflows. 
*Example:* *"Use GitNexus to trace the `CheckoutFlow`. Once you understand it, run an impact analysis on the checkout controller, and then write a summary of how we could safely add a 'Discount Code' feature without breaking the existing graph."*
