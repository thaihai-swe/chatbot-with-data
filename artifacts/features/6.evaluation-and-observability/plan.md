# Plan: Evaluation and Observability

## Metadata
- Feature: Evaluation and Observability
- Related Design: `artifacts/features/6.evaluation-and-observability/design.md`

## 1. Execution Order
1. **Infrastructure:** Create `backend/test_data/eval_dataset.json` and basic schema for evaluation results.
2. **Backend (Grounding):** Enhance `GroundingService` with LLM-based groundedness scoring.
3. **Backend (Evaluation):** Implement `EvaluationService` and the `/api/chat/evaluate/sanity-check` endpoint.
4. **Frontend (Observability):** Implement "Debug Mode" toggle and "X-Ray" panel in the chat interface.
5. **Frontend (Evaluation):** Create the Evaluation screen and integrate with the backend endpoint.

## 2. Impacted Boundaries
- `backend/chat/grounding.py`: New scoring logic.
- `backend/chat/evaluation.py`: New service.
- `backend/routers/chat.py`: New endpoints.
- `frontend/src/screens/ChatScreen.jsx`: UI updates for debug info.
- `frontend/src/screens/EvaluationScreen.jsx`: New screen.

## 3. Proving Strategy
- **Unit Tests:** Test the `EvaluationService` with a mock dataset.
- **Manual Verification:**
  - Turn on Debug Mode and verify the "X-Ray" panel displays real metadata.
  - Run the Sanity Check from the UI and verify the results table matches the `eval_dataset.json` logic.

## 4. Rollback Posture
- The changes are mostly additive (new endpoints, new UI components).
- Rollback involves reverting the UI toggle and disabling the evaluation endpoint. No database migrations are required for this narrowed scope.

## 5. First Slice
- **Slice 1: Deep Observability.** Enable the frontend to display the already-existing backend traces. This provides immediate value for developers.
