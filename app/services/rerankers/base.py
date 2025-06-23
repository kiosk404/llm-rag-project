from typing import List, Any

class BaseReranker:
    """
    Reranker 抽象基类，所有重排序器需继承本类。
    """
    def rerank(self, query: str, docs: List[Any], top_k: int = 5) -> List[Any]:
        """
        对召回的 docs 进行重排序，返回 top_k 个最相关的文档。
        :param query: 用户查询
        :param docs: 初步召回的文档列表
        :param top_k: 返回的文档数
        :return: 重排序后的文档列表
        """
        raise NotImplementedError("子类需实现该方法") 