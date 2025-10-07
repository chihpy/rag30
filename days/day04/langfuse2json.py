"""
對於retrieverQueryEngine，我們主要在意：
- VectorIndexRetriever.retrieve
- OpanAI.chat
# TODO:
自訂 span 把 retrieved 的結果丟出來
"""
import json
import zoneinfo
# .env setup and langfuse client
from dotenv import find_dotenv, load_dotenv
from langfuse import get_client
_ = load_dotenv(find_dotenv())
langfuse = get_client()

def retrieve_parser(obv):
    start_time = obv.start_time.astimezone(zoneinfo.ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S %Z")
    end_time = obv.end_time.astimezone(zoneinfo.ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S %Z")
    query_text = obv.input
    output_nodes = obv.output
    num_doc = len(output_nodes)
    
    meta_dict = obv.metadata['attributes']
    docs = []
    for idx in range(num_doc):
        rv = {
            'id': meta_dict[f'retrieval.documents.{idx}.document.id'],
            'content': meta_dict[f'retrieval.documents.{idx}.document.content'],
            'score': meta_dict[f'retrieval.documents.{idx}.document.score'],
        }
        docs.append(rv)
        
    rv = {
        'start_time': start_time,
        'end_time': end_time,
        'query': query_text,
        'output_nodes': output_nodes,
        'num_doc': num_doc,
        'docs': docs
    }
    return rv

def chat_parser(obv):
    start_time = obv.start_time.astimezone(zoneinfo.ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S %Z")
    end_time = obv.end_time.astimezone(zoneinfo.ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S %Z")
    model_name = obv.model
    num_message = len(obv.input['messages'])
    attributes = obv.metadata['attributes']
    messages = []
    for idx in range(num_message):
        rv = {
            'role': attributes[f'llm.input_messages.{idx}.message.role'],
            'content': attributes[f'llm.input_messages.{idx}.message.content'],
        }
        messages.append(rv)
    rv = {
        'start_time': start_time,
        'end_time': end_time,
        'model_name': model_name,
        'num_message': num_message,
        'messages': messages,
    }
    return rv

if __name__ == "__main__":
    # get trace id first
    #traces = langfuse.api.trace.list(limit=1)
    #trace_data = traces.data[0]
    #trace_id = trace_data.id
    trace_id = "fb8f8238ea13c59aab69612f3a4cafd1"  # get trace_detail by id
    # get trace with full details from trace_id
    TraceWithFullDetails = langfuse.api.trace.get(trace_id)
    # get observations
    observations = TraceWithFullDetails.observations
    # parser result from observations
    data = {}
    for obv in observations:
        name = obv.name
        if name == 'VectorIndexRetriever.retrieve':
            data['retrieve_parsed'] = retrieve_parser(obv)
        elif name == 'OpenAI.chat':
            data['chat_parsed'] = chat_parser(obv)
    # dump
    with open('RetrieverQueryEngine_example.json', 'w') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)


