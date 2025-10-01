from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph.message import add_messages
from utils.model_loader import ModelLoader
from utils.config_loader import load_config
from prod_assistant.retrieval.retrieval import Retriever
from langchain_core.messages import BaseMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompt_library.prompts import PROMPT_REGISTRY, PromptType
from langgraph.graph import StateGraph, START, END
from retrieval.websearch import WebSearch 
from langgraph.checkpoint.memory import MemorySaver
class AgenticRag:

    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], add_messages]

    def __init__(self):
        self.llm = ModelLoader().load_llm()
        self.config = load_config()
        self.retriever = Retriever()
        self.webSearch =WebSearch()
        self.checkpointer = MemorySaver()
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=self.checkpointer)

    def _format_docs(self, docs) -> str:
        if not docs:
            return "No relevant documents found."
        formatted_chunks =[]
        for d in docs:
            meta = d.metadata() or {}
            formatted = (
                f"Title: {meta.get('product_title','N/A')}\n",
                f"Ratings: {meta.get('ratings','N/A')}\n",
                f"Price: {meta.get('price','N/A')}\n",
                f"Reviews: \n{meta.get('reviews','N/A')}\n"
            )

            formatted_chunks.append(formatted)
        return '\n\n------\n\n'.join(formatted_chunks)
    
    def _ai_assistant(self,state:AgentState):
        messages = state['messages']
        last_message = messages[-1].content 

        if any(word in last_message.lower() for word in ['price', 'review', 'product']):
            return {"messages":HumanMessage(content='TOOL: retriever')}
        elif any(word in last_message.lower() for word in ['latest', 'new', 'update']):
            return {"messages": HumanMessage(content='TOOL: websearch')}
        else:
            prompt = ChatPromptTemplate.from_template(
                "You are an helpful assistant. Answer the user directly.\n\n Question: {question}\nAnswer:"
            )

            chain = prompt|self.llm| StrOutputParser()
            response = chain.invoke({'question': last_message})
            return {'messages': [HumanMessage(content=response)]}

    def _vector_retriever(self,state:AgentState):
        message = state['messages']
        query = message[-1].content
        retriever = self.retriever.load_retriever()
        docs = retriever.invoke(query)
        context = self._format_docs(docs)
        return {'messages':[HumanMessage(content=context)]}
    

    def _grade_docs(self,state:AgentState)->Literal['generator', 'rewriter']:
        question = state['messages'][0].content
        context = state['messages'][-1].content

        prompt = PromptTemplate(
            """You are a grader. Question: {question}\n Docs: {context}\n
             Are docs relevant to question? Answer yes or No.
            """,
            input_variables=['question','context']
        )
        chain = prompt | self.llm | StrOutputParser()
        score = chain.invoke({'question':question,'context':context})
        return 'generator' if 'yes' in score.lower() else 'rewriter' 

    def _rewriter(self,state:AgentState):
        question = state['messages'][0].content

        new_question = self.llm.invoke([HumanMessage(content=f"rewrite the query clearer: 'question': {question}")])
        return {'messages':[HumanMessage(content=new_question.content)]}

    def _generator(self,state:AgentState):
        question = state['messages'][0].content
        docs = state['messages'][-1].content

        prompt = PromptTemplate.from_template(
            PROMPT_REGISTRY[PromptType.PRODUCT_BOT].template
        )

        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke({'question':question, 'context':docs})
        return {'messages':[HumanMessage(content=response)]}
    
    def _websearch(self, state:AgentState):
        question = state['messages'][0].content
        results = self.webSearch.search(question)
        return {'messages':[HumanMessage(content=results)]}

    def _build_workflow(self):
        workflow=StateGraph(self.AgentState)
        workflow.add_node('Assistant',self._ai_assistant)
        workflow.add_node('retriever',self._vector_retriever)
        workflow.add_node('websearch', self._websearch)
        workflow.add_node('generator',self._generator)
        workflow.add_node('rewriter',self._rewriter)
        workflow.add_conditional_edges('Assistant', lambda state: 'websearch' if 'TOOL' in state['messages'][-1].content 
                                       else 'retriever' if 'TOOL' in state['messages'][-1].content 
                                       else END,
                                       {'websearch': 'websearch','retriever': 'retriever', END: END})
        # workflow.add_conditional_edges('Assistant',lambda state: 'retriever' if 'TOOL' in state['messages'][-1].content else END,
        #                                {'retriever':'retriever', END: END},
        #                                )
        workflow.add_conditional_edges(
            'retriever',
            self._grade_docs,
            ['generator', 'rewriter']
        )
        workflow.add_edge('websearch', 'generator')
        workflow.add_edge('retriever','Assistant')
        workflow.add_edge('generator',END)

        return workflow
    

    def run(self, query: str,thread_id: str = "default_thread") -> str:
        """Run the workflow for a given query and return the final answer."""
        result = self.app.invoke({"messages": [HumanMessage(content=query)]},
                                 config={"configurable": {"thread_id": thread_id}})
        return result["messages"][-1].content
    
     


if __name__ == "__main__":
    rag_agent = AgenticRag()
    answer = rag_agent.run("What is the price of iPhone 15?")
    print("\nFinal Answer:\n", answer)
