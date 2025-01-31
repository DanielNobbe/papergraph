import langgraph.graph as graph

from .state import State
from .nodes import load_document, split_text, extract_metadata, extract_key_findings, extract_methodology, generate_summary, extract_keywords


def create_graph(config: dict):
    graph_builder = graph.StateGraph(State)  # don't think we need a persistent state

    # Nodes
    graph_builder.add_node("load_document", load_document)
    graph_builder.add_node("split_text", split_text)
    graph_builder.add_node("extract_metadata", extract_metadata)
    graph_builder.add_node("extract_key_findings", extract_key_findings)
    graph_builder.add_node("extract_methodology", extract_methodology)
    graph_builder.add_node("generate_summary", generate_summary)
    graph_builder.add_node("extract_keywords", extract_keywords)

    # Define edges
    graph_builder.add_edge(graph.START, "load_document")
    graph_builder.add_edge("load_document", "split_text")

    if config['concurrent']:
        graph_builder.add_edge("split_text", "extract_metadata")
        graph_builder.add_edge("split_text", "extract_key_findings")
        graph_builder.add_edge("split_text", "extract_methodology")
        graph_builder.add_edge("split_text", "generate_summary")
        graph_builder.add_edge("split_text", "extract_keywords")
    else:
        # limit concurrent requests
        graph_builder.add_edge("split_text", "extract_metadata")
        graph_builder.add_edge("extract_metadata", "extract_key_findings")
        graph_builder.add_edge("extract_key_findings", "extract_methodology")
        graph_builder.add_edge("extract_methodology", "generate_summary")
        graph_builder.add_edge("generate_summary", "extract_keywords")

    # graph_builder.set_entry_point("load_document")
    return graph_builder.compile()

