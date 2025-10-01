import os
from prod_assistant.retrieval.retrieval import Retriever
from utils.model_loader import ModelLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from prompt_library.prompts import PROMPT_REGISTRY, PromptType, PromptTemplate

retriever_obj = Retriever()
modelloader = ModelLoader()

def format_docs(docs):

    if not docs:
        return "No relevant documents"
    
    formatted_chunks =[]
    for d in docs:
        meta =d.metadata or {}
        formatted = (
            f"product_title: {meta.get('product_title','N/A')}\n",
            f"price: {meta.get('price','N/A')}\n",
            f"rating: {meta.get('rating','N/A')}\n",
            f"reviews: \n{d.page_content.strip()}\n"
        )
        formatted_chunks.append(formatted)
    return '\n\n---------------\n\n'.join(formatted_chunks)


def build_chain(query):
    retriever = retriever_obj.load_retriever()
    retrieved_docs = retriever.invoke(query)
    llm = modelloader.load_llm()

    # retrieved_context =[format_docs(docs) for docs in retrieved_docs]
    retrieved_context = [format_docs(retrieved_docs)]
    prompt = ChatPromptTemplate.from_template(
        PROMPT_REGISTRY[PromptType.PRODUCT_BOT].template
    )

    chain = (
        {'context': retriever | format_docs , 'question': RunnablePassthrough() }
        | prompt
        | llm
        | StrOutputParser()
        )
    
    # response =chain.invoke(query)
    return retrieved_context, chain


def invoke_chain(query, debug:bool =False):
    retrieved_context, chain = build_chain(query)
    if debug:
        docs = retriever_obj.load_retriever().invoke(query)
        print("\nRetrieved Documents:")
        print(format_docs(docs))
        print("\n---\n")
    response = chain.invoke(query)
    return response, retrieved_context

if __name__ == "__main__":
    try:
        answer = invoke_chain("can you tell me the price of the iPhone 15?")
        print("\n Assistant Answer:\n", answer)
    except Exception as e:
        import traceback
        print("Exception occurred:", str(e))
        traceback.print_exc()