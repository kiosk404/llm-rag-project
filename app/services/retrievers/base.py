from typing import List, Any

class BaseRetriever:
    def retrieve(self, query: str, top_k: int = 5) -> List[Any]:
        raise NotImplementedError("子类必须实现该方法") 