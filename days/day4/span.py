"""
"""
# import
from dotenv import find_dotenv, load_dotenv
from langfuse import get_client
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from llama_index.core import Document
from llama_index.core.instrumentation import get_dispatcher
from llama_index.core.instrumentation.span_handlers import SimpleSpanHandler
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex

# env and langfuse
_ = load_dotenv(find_dotenv())
langfuse = get_client()
## Initialize LlamaIndex instrumentation
LlamaIndexInstrumentor().instrument()
# instrumentation
root_dispatcher = get_dispatcher()
simple_span_handler = SimpleSpanHandler()
root_dispatcher.add_span_handler(simple_span_handler)

# documents
text_list = [
    'Langfuse is an open source LLM engineering platform to help teams collaboratively debug, analyze and iterate on their LLM Applications. '
    'With the Langfuse integration, you can track and monitor performance, traces, and metrics of your LlamaIndex application.' 
    'Detailed traces of the context augmentation and the LLM querying processes are captured and can be inspected directly in the Langfuse UI.',
    
    'Langfuse 真香',
    
    'The instrumentation module (available in llama-index v0.10.20 and later) is meant to replace the legacy callbacks module.',
    
    'Listed below are the core classes as well as their brief description of the instrumentation module: '
    'Event — represents a single moment in time that a certain occurrence took place within the execution of the application’s code.'
    'EventHandler — listen to the occurrences of Event’s and execute code logic at these moments in time.'
    'Span — represents the execution flow of a particular part in the application’s code and thus contains Event’s.'
    'SpanHandler — is responsible for the entering, exiting, and dropping (i.e., early exiting due to error) of Span’s.'
    'Dispatcher — emits Event’s as well as signals to enter/exit/drop a Span to the appropriate handlers.',
]
documents = [Document(text=t) for t in text_list]

# query
llm = OpenAI(model="gpt-5-mini", temperature=0.0)
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine(llm=llm)

query = '什麼是 LlamaIndex 的instrumentation module?'
with langfuse.start_as_current_span(name="day4_test") as span:
    response = query_engine.query(query)
langfuse.flush()

simple_span_handler.print_trace_trees()