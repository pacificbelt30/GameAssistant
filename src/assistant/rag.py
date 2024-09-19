from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS

class VectorStore:
    def __init__(self, model='text-embedding-3-small'):
        self.embedding = OpenAIEmbeddings(model=model)
        self.temp_dir = './temp/'

    def embedding(self, input: str='raw_text.txt'):
        # Load the document, split it into chunks, embed each chunk and load it into the vector store.
        raw_documents = TextLoader(raw_text).load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        documents = text_splitter.split_documents(raw_documents)
        print(documents)
        self.db = FAISS.from_documents(documents, self.embedding)

    def save(self, output: str='vector_store'):
        self.db.save_local(output)

    def load(self, input: str='vector_store'):
        self.db = FAISS.load_local('testvectorstore', self.embedding, allow_dangerous_deserialization=True)

    def query(self, query: str='How are you?'):
        docs = self.db.similarity_search(query)
        print(docs[0].page_content)

    def query_by_vector(self, query: str='How are you?'):
        embedding_vector = self.embedding.embed_query(query)
        docs = db.similarity_search_by_vector(embedding_vector)
        print(docs[0].page_content)
