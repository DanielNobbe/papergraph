import langgraph.graph as graph

from .state import State
from .nodes import load_document, split_text, extract_metadata, extract_key_findings, extract_methodology, generate_summary, extract_keywords


def create_graph(config: dict):
    graph_builder = graph.StateGraph(State)  # don't think we need a persistent state

    # Nodes
    graph_builder.add_node("load_document", lambda x: load_document(x, config))
    graph_builder.add_node("split_text", lambda x: split_text(x, config))
    graph_builder.add_node("extract_metadata", lambda x: extract_metadata(x, config))
    graph_builder.add_node("extract_key_findings", lambda x: extract_key_findings(x, config))
    graph_builder.add_node("extract_methodology", lambda x: extract_methodology(x, config))
    graph_builder.add_node("generate_summary", lambda x: generate_summary(x, config))
    graph_builder.add_node("extract_keywords", lambda x: extract_keywords(x, config))

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

