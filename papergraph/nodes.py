
from langchain_community.document_loaders import PyPDFLoader, Blob
from langchain_community.document_loaders.pdf import PyPDFParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.output_parsers import DatetimeOutputParser
from langchain.schema import Document
from langchain_mistralai import ChatMistralAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from typing import List, Optional, BinaryIO
from langchain_core.exceptions import OutputParserException

from .state import State

# from langchain.parsers import PyPDFParser
from langchain.document_loaders.base import BaseLoader

linebreak = "\n"
double_linebreak = "\n\n"

class CustomPDFLoader(BaseLoader):
    def __init__(self, file: BinaryIO, extract_images: bool = False):
        self.file = file
        self.parser = PyPDFParser(extract_images=extract_images)

    def load(self) -> List[Document]:
        blob = Blob.from_data(self.file.read())
        return list(self.parser.parse(blob))

def convert_to_datetime(string: str):
    datetime_parser = DatetimeOutputParser(
        format="%Y-%m-%d",
    )
    try:
        return datetime_parser.parse(string)
    except OutputParserException:
        # in case it outputs wrong format
        return datetime_parser.parse("1970-01-01")
    


def load_document(state: State, config: dict):
    print("Loading document..")
    if state.get('path'):
        filepath = state['path']
        loader = PyPDFLoader(filepath)  # this seems to give one per page, which probably is fine
        docs = loader.load()
    elif state.get('item'):
        file = state['item']
        loader = CustomPDFLoader(file)  # this seems to give one per page, which probably is fine
        docs = loader.load()

        filepath = "upload.pdf"
    else:
        raise ValueError("No file or path provided")

    full_text = "\n".join([doc.page_content for doc in docs])

    main_doc =  Document(page_content=full_text, metadata={"source": filepath})
    state['doc'] = main_doc

    return state


def split_text(state: State, config: dict):
    print("Splitting text..")  # normally would add fastapi logging
    doc = state['doc']

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=config['chunk_size'], chunk_overlap=config['chunk_overlap'])
    split_docs = text_splitter.split_documents([doc])

    state["docs"] = split_docs

    return state


def extract_metadata(state: State, config: dict):
    print("Extracting metadata..")
    llm = ChatMistralAI(model="mistral-large-latest", temperature=0, api_key="Osq78PYUMFm97Iy5g4pWceAjz2awLzrE")

    docs = state['docs']

    response_schemas = [  # could be specified in config too
        ResponseSchema(name="author", description="The author of the paper"),
        ResponseSchema(name="date", description="The date the paper was published as YYYY-MM-DD"),
        ResponseSchema(name="title", description="The title of the paper"),
        ResponseSchema(name="abstract", description="The abstract of the paper"),
        ResponseSchema(name="institutions", description="The institutions involved in writing the paper, if mentioned"),
        ResponseSchema(name="number_of_authors", description="The number of authors in the paper as only an integer", type="integer")
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    prompt = f"Extract the following metadata:{linebreak}{format_instructions}{double_linebreak}Document:{linebreak}{docs[0].page_content}"
    
    response = llm.invoke(prompt)

    state['result']['metadata'] = output_parser.parse(response.content)

    # if it doesn't work, use 1 jan 1970
    state['result']['metadata']['date'] = convert_to_datetime(state['result']['metadata']['date'])

    return state


def extract_key_findings(state: State, config: dict):
    print("Extracting key findings..")
    docs = state['docs']

    # feels wasteful to initialise this every time, but it's just a wrapper around an API
    llm = ChatMistralAI(model=config['model'], temperature=0, api_key="Osq78PYUMFm97Iy5g4pWceAjz2awLzrE")

    # docs is only one doc if the context window is large enough, otherwise it's multiple

    # extract key points from each doc, then merge the key points
    responses = []
    for doc in docs:
        prompt = f"Extract key findings from the following research paper, formatted like ' - [title 1]: ... {double_linebreak} - [title 2]: ... {double_linebreak}':{double_linebreak}{doc.page_content}"
        responses.append(llm.invoke(prompt).content)
    # could add a request to make the sentences verbatim, but not super relevant
    # to truly ensure verbatimness, we can use RAG from a vector store instead

    if len(docs) > 1:
        final_prompt = f"Extract all unique key findings from these overviews, provided by separate experts, formatted like ' - [title 1]: ... {double_linebreak} - [title 2]: ... {double_linebreak}':{double_linebreak}{linebreak.join(responses)}"
        state['result']['key_findings'] = llm.invoke(final_prompt).content.split(double_linebreak)
    else:
        state['result']['key_findings'] = responses[0].split(double_linebreak)
    
    return state  # Returning a list of key points


def extract_methodology(state: State, config: dict):
    print("Extracting methodology..")
    docs = state['docs']

    # feels wasteful to initialise this every time, but it's just a wrapper around an API
    llm = ChatMistralAI(model=config['model'], temperature=0, api_key="Osq78PYUMFm97Iy5g4pWceAjz2awLzrE")

    # docs is only one doc if the context window is large enough, otherwise it's multiple

    # extract key points from each doc, then merge the key points
    responses = []
    for doc in docs:
        prompt = f"Extract research methodology from the following research paper:{double_linebreak}{doc.page_content}"
        responses.append(llm.invoke(prompt).content)

    if len(docs) > 1:
        # TODO: Test for shorter context windows to verify this works
        final_prompt = f"Combine the research methodology from the following overviews about a paper, provided by other experts:{double_linebreak}{'/n'.join(responses)}"
        state['result']['methodology'] = llm.invoke(final_prompt).content
    else:
        state['result']['methodology'] = responses[0]
    
    return state  # Returning a list of key points


def generate_summary(state: State, config: dict):
    print("Generating summary..")
    docs = state['docs']

    # feels wasteful to initialise this every time, but it's just a wrapper around an API
    llm = ChatMistralAI(model=config['model'], temperature=0, api_key="Osq78PYUMFm97Iy5g4pWceAjz2awLzrE")

    # docs is only one doc if the context window is large enough, otherwise it's multiple

    responses = []
    for doc in docs:
        prompt = f"Write a well-structured summary that is relevant to (ML) engineers and at most 200 words:{double_linebreak}{doc.page_content}"
        responses.append(llm.invoke(prompt).content)

    if len(docs) > 1:
        # TODO: Test for shorter context windows to verify this works
        final_prompt = f"Combine the following summaries into a well-strutured summary that is relevant to (ML) engineers and at most 200 words. The summaries are written by various experts for the same research paper:{double_linebreak}{linebreak.join(responses)}"
        state['result']['summary'] = llm.invoke(final_prompt).content
    else:
        state['result']['summary'] = responses[0]
    
    return state  # Returning a list of key points


def extract_keywords(state: State, config: dict):
    print("Extracting keywords..")
    docs = state['docs']

    # feels wasteful to initialise this every time, but it's just a wrapper around an API
    llm = ChatMistralAI(model=config['model'], temperature=0, api_key="Osq78PYUMFm97Iy5g4pWceAjz2awLzrE")

    # docs is only one doc if the context window is large enough, otherwise it's multiple

    responses = []
    for doc in docs:
        # prompt = f"Extract (at most 20) keywords, that are relevant to (ML) engineers, from the following research paper:\n\n{doc.page_content}"
        prompt = f"Extract less than 10 keywords that are relevant to (ML) engineers from the following research paper. Please format your response like 'keyword1, keyword2'. {double_linebreak}{doc.page_content}"
        responses.append(llm.invoke(prompt).content)
    
    if len(docs) > 1:
        # TODO: Test for shorter context windows to verify this works
        final_prompt = f"Extract from the following keywords a list of (less than 10) keywords that are most relevant to (ML) engineers. Please format like 'keyword1, keyword2'{double_linebreak}{linebreak.join(responses)}"
        state['result']['keywords'] = llm.invoke(final_prompt).content
    else:
        state['result']['keywords'] = responses[0]

    return state

