from rag.base import RetrievalChain
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Annotated
from rag.utils import format_docs


class PDFRetrievalChain(RetrievalChain):
    def __init__(
        self,
        source_uri: Annotated[str, "Source URI"],
        model_name="gpt-4o-mini",
        k: int = 6,
    ):
        self.source_uri = source_uri
        self.k = k
        self.model_name = model_name

    def load_documents(self, source_uris: List[str]):
        docs = []
        for source_uri in source_uris:
            loader = PDFPlumberLoader(source_uri)
            docs.extend(loader.load())

        return docs

    def format_docs(self, docs):
        return format_docs(docs)

    def create_text_splitter(self):
        return RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
