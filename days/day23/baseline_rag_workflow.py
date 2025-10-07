"""reference: https://github.com/run-llama/llama_index/blob/main/docs/examples/workflow/rag.ipynb
"""
import os
from llama_index.core.workflow import (
    Context,
    Workflow,
    StartEvent,
    StopEvent,
    step,
)

from llama_index.core.workflow import Event
from llama_index.core.schema import NodeWithScore

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

import faiss  # pip install faiss-cpu
from llama_index.core import StorageContext
from llama_index.core import load_index_from_storage
from llama_index.vector_stores.faiss import FaissVectorStore  # pip install llama-index-vector-stores-faiss 
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

from llama_index.core.postprocessor.llm_rerank import LLMRerank

from llama_index.core.response_synthesizers import CompactAndRefine

SIM_TOP_K = 3

class RetrieverEvent(Event):
    """Result of running retrieval"""

    nodes: list[NodeWithScore]


class RerankEvent(Event):
    """Result of running reranking on retrieved nodes"""

    nodes: list[NodeWithScore]

class RAGWorkflow(Workflow):
    @step
    async def ingest(self, ctx: Context, ev: StartEvent) -> StopEvent | None:
        """document_dir, index_dir"""
        document_dir = ev.get("document_dir")
        index_dir = ev.get("index_dir")
        if not index_dir:
            # 如果沒有 index_dir 這條路就會直接走不通
            # 所以 query 的時候預設是不用給 index_dir 的
            return None
        if not os.path.isdir(index_dir):
            print(f'create index_dir: {index_dir}')
            os.makedirs(index_dir)
        if document_dir:

            documents = SimpleDirectoryReader(document_dir).load_data()
            d = 1536
            faiss_index = faiss.IndexFlatL2(d)
            vector_store = FaissVectorStore(faiss_index=faiss_index)
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store
            )
            index = VectorStoreIndex.from_documents(
                documents=documents,
                embed_model=OpenAIEmbedding(model_name="text-embedding-3-small"),
                storage_context=storage_context,
            )
            index.storage_context.persist(persist_dir=index_dir)
            print("Index built and persisted to:", index_dir)
        else:
            print(f"load index from: {index_dir}")
            # load index from disk
            vector_store = FaissVectorStore.from_persist_dir(index_dir)
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store, persist_dir=index_dir
            )
            index = load_index_from_storage(storage_context=storage_context)
        return StopEvent(result=index)

    @step
    async def retrieve(
        self, ctx: Context, ev: StartEvent
    ) -> RetrieverEvent | None:
        "Entry point for RAG, triggered by a StartEvent with `query`."
        query = ev.get("query")
        index = ev.get("index")

        if not query:
            return None

        print(f"Query the database with: {query}")

        # store the query in the global context
        await ctx.store.set("query", query)

        # get the index from the global context
        if index is None:
            print("Index is empty, load some documents before querying!")
            return None

        retriever = index.as_retriever(similarity_top_k=SIM_TOP_K)
        nodes = await retriever.aretrieve(query)
        print(f"Retrieved {len(nodes)} nodes.")
        
        retrieved_nodes = []
        for node in nodes:
            rv = {
                'id': node.id_,
                'text': node.text,
                'score': node.score
            }
            retrieved_nodes.append(rv)
        await ctx.store.set("retrieved_nodes", retrieved_nodes)
        return RetrieverEvent(nodes=nodes)

    @step
    async def rerank(self, ctx: Context, ev: RetrieverEvent) -> RerankEvent:
        # Rerank the nodes
        ranker = LLMRerank(
            choice_batch_size=5, top_n=3, llm=OpenAI(model="gpt-4o-mini")
        )
        print(await ctx.store.get("query", default=None), flush=True)
        new_nodes = ranker.postprocess_nodes(
            ev.nodes, query_str=await ctx.store.get("query", default=None)
        )
        print(f"Reranked nodes to {len(new_nodes)}")
        reranked_nodes = []
        for node in new_nodes:
            rv = {
                'id': node.id_,
                'text': node.text,
                'score': node.score
            }
            reranked_nodes.append(rv)
        await ctx.store.set("reranked_nodes", reranked_nodes)
        return RerankEvent(nodes=new_nodes)

    @step
    async def synthesize(self, ctx: Context, ev: RerankEvent) -> StopEvent:
        """Return a streaming response using reranked nodes."""
        llm = OpenAI(model="gpt-4o-mini")
        summarizer = CompactAndRefine(llm=llm, streaming=False, verbose=True)
        query = await ctx.store.get("query", default=None)
        response = await summarizer.asynthesize(query, nodes=ev.nodes)
        retrieved_nodes = await ctx.store.get("retrieved_nodes", default=None)
        reranked_nodes = await ctx.store.get("reranked_nodes", default=None)
        rv = {
            'query': query,
            'response': response.response,
            'retrieved_nodes': retrieved_nodes,
            'reranked_nodes': reranked_nodes,
        }
        return StopEvent(result=rv)