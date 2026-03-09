from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama
from langchain_classic.chains.retrieval_qa.base import RetrievalQA



# Load document
loader = TextLoader("ai_billy/sample.csv")
documents = loader.load()

# Split documents
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)

# Print chunks
# for i, chunk in enumerate(chunks):
#     print(f"Chunk {i+1}:\n{chunk.page_content}\n")

# Use Ollama to generate embeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Store in ChromaDB locally
db = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")



# Initialize Gemma model
llm = Ollama(model="gemma3:latest")

# Create retriever
retriever = db.as_retriever(search_kwargs={"k": 3})

# Create the chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)

query = "How is the performance of merchant id M-9921?"
response = qa_chain.invoke(query)
print(response['result'])



