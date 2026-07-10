import logging

logger = logging.getLogger(__name__)

try:
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    from datasets import Dataset

    class RagasEvaluator:
        def __init__(self):
            self.metrics = [faithfulness, answer_relevancy, context_precision, context_recall]
        
        def evaluate_batch(self, queries: list[str], answers: list[str], contexts: list[list[str]], ground_truths: list[str] = None) -> dict:
            """
            Evaluate a batch of RAG responses.
            
            Args:
                queries: List of user queries
                answers: List of generated answers
                contexts: List of context lists (retrieved chunks per query)
                ground_truths: Optional list of ground truth answers
            
            Returns:
                Dict with metric scores
            """
            data = {
                "question": queries,
                "answer": answers,
                "contexts": contexts,
            }
            
            if ground_truths:
                data["ground_truth"] = ground_truths
            
            dataset = Dataset.from_dict(data)
            
            results = evaluate(dataset, metrics=self.metrics)
            
            return {
                "faithfulness": results["faithfulness"],
                "answer_relevancy": results["answer_relevancy"],
                "context_precision": results["context_precision"],
                "context_recall": results.get("context_recall", None)
            }

except ImportError:
    logger.warning("ragas not installed. RagasEvaluator is a stub.")

    class RagasEvaluator:
        def __init__(self):
            logger.warning("RagasEvaluator initialized in stub mode - no evaluation available")
            self.metrics = []
        
        def evaluate_batch(self, queries: list[str], answers: list[str], contexts: list[list[str]], ground_truths: list[str] = None) -> dict:
            """
            Evaluate a batch of RAG responses (stub).
            
            Args:
                queries: List of user queries
                answers: List of generated answers
                contexts: List of context lists (retrieved chunks per query)
                ground_truths: Optional list of ground truth answers
            
            Returns:
                Dict with metric scores (stub returns None values)
            """
            logger.warning("RagasEvaluator.evaluate_batch() called but ragas not installed")
            return {
                "faithfulness": None,
                "answer_relevancy": None,
                "context_precision": None,
                "context_recall": None,
            }
