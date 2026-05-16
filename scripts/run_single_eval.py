import os
import sys
import json
from unittest.mock import MagicMock

# Add backend to path
sys.path.append(os.path.abspath("backend"))

from chat.evaluation import EvaluationService
from chat.service import ChatService
from chat.judge import JudgeService
from schemas.evaluation import EvaluationDataset, EvaluationCase, JudgeMetric
from schemas.chat import AdvancedRetrievalConfig, ChatTurnResponse

def run_test():
    # 1. Setup mocks
    mock_chat = MagicMock(spec=ChatService)
    mock_judge = MagicMock(spec=JudgeService)
    
    # Mock chat response
    mock_chat.process_turn.return_value = ChatTurnResponse(
        id="turn-1",
        session_id="session-1",
        query_text="What is RAG?",
        answer_text="RAG is Retrieval-Augmented Generation.",
        retrieved_chunks_json='[{"document_id": "doc-1", "text": "...", "id": "chunk-1"}]',
        context_used_json='{}',
        status="completed",
        error_message=None,
        created_at="now",
        updated_at="now"
    )
    
    # Mock judge response
    mock_judge.evaluate_groundedness.return_value = JudgeMetric(score=1.0, reason="Grounded")
    mock_judge.evaluate_relevance.return_value = JudgeMetric(score=1.0, reason="Relevant")
    
    service = EvaluationService(mock_chat, mock_judge)
    
    # 2. Create a test dataset
    dataset = EvaluationDataset(
        id="test_ds",
        name="Test Dataset",
        cases=[
            EvaluationCase(
                id="case-1",
                question="What is RAG?",
                expected_answer="RAG stands for Retrieval-Augmented Generation",
                expected_document_ids=["doc-1"]
            )
        ]
    )
    service.save_dataset(dataset)
    print(f"Dataset saved to backend/data/eval/datasets/test_ds.json")
    
    # 3. Run evaluation
    run_id = service.run_evaluation("test_ds", AdvancedRetrievalConfig())
    print(f"Triggered run: {run_id}")
    
    # 4. Execute (sync for test)
    service.execute_run(run_id)
    print(f"Execution complete.")
    
    # 5. Verify run file
    run_path = os.path.join("backend/data/eval/runs", f"{run_id}.json")
    if os.path.exists(run_path):
        with open(run_path, "r") as f:
            run_data = json.load(f)
            print(f"Run data found. Status: {run_data['status']}")
            print(f"Summary: {json.dumps(run_data['metrics_summary'], indent=2)}")
            print("SUCCESS")
    else:
        print(f"ERROR: Run file {run_path} not found")

if __name__ == "__main__":
    run_test()
