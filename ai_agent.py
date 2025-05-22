from pydantic import Field
from typing_extensions import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage,SystemMessage
from langgraph.graph import START,END,StateGraph,add_messages
load_dotenv()

llm=ChatGoogleGenerativeAI(model='gemini-1.5-flash')


class State(TypedDict):
    user_query:str
    research_info:str
    casual_response:str
    formal_response:str


def research_agent(state:State):
    user_query=state['user_query']
    response=llm.invoke([HumanMessage(content=user_query),
                         SystemMessage(content="""
You are an expert research assistant with access to vast knowledge and web data. 
Your task is to extract, summarize, and explain the **most relevant, up-to-date, and comprehensive** information from the internet on the given topic.
For any query provided by the user, search deeply, gather multiple viewpoints or sources, and provide:
- A clear and detailed explanation.
- Important facts, data, or statistics.
- Relevant recent updates (if any).
- Contrasting views or debates if they exist.
- Real-world examples or case studies if applicable.
Only output useful, factual, and non-redundant content. Be accurate and exhaustive.
Minimum:10000 words of data.
""")])
    return {"research_info":response.content}

def formal_agent(state:State):
    research_info=state['research_info']
    response=llm.invoke([HumanMessage(content=f"Here is the researched data:{research_info} \n using this data present this data in a formal ressearch paper style"),
                         SystemMessage(content="""
You are a professional academic researcher and scientific writer. 
Your task is to take the given information on the given topic and re write it and present it in the style of a formal research paper.
Structure your response clearly using academic tone and formatting. Include the following sections(follow this scritly):
1. **Title**: A concise, academic-style title.
2. **Abstract**: A brief summary of the core findings or arguments.
3. **Introduction**: Explain the background, relevance, and purpose of the topic.
4. **Main Body** (with optional subsections): Present findings, explanations, data, and various perspectives in a well-structured and logically flowing manner.
5. **Discussion/Analysis**: Critically analyze the information, highlight implications, and compare viewpoints.
6. **Conclusion**: Summarize key takeaways and possible future directions.
7. **References**: Mention known or hypothetical sources as examples if exact links are not available.

Use formal academic language. Maintain objectivity and clarity. Avoid conversational tone or repetition. Be professional and polished.
""")])
    return {"formal_response":response.content}

def casual_agent(state:State):
    formal_response=state['formal_response']
    response=llm.invoke([HumanMessage(content=f"Summarize this:{formal_response} \n Don-t mention that you are summarizing."),
                         SystemMessage(content="""
You are a creative storyteller and educator. 
Your task is to read the given research paper and summarize it in a **casual, engaging, and easy-to-understand** way for a general audience.
Your output should:
- Capture the **main insights** and **key takeaways** from the paper.
- Use **friendly language** and a **conversational tone**.
- Include **analogies**, **examples**, or even light humor if appropriate.
- Avoid technical jargon unless you explain it simply.
- Keep it concise but insightful — like a blog, newsletter, or social media post.

Imagine you're explaining it to an interested friend or reader who’s smart but not an expert.

Be creative, clear, and human.
Your response should be maximum 500-1000 words.
""")])
    return {"casual_response":response.content}

graph_builder=StateGraph(State)

graph_builder.add_node("research_agent",research_agent)
graph_builder.add_node("formal_agent",formal_agent)
graph_builder.add_node("casual_agent",casual_agent)

graph_builder.add_edge(START,"research_agent")
graph_builder.add_edge("research_agent","formal_agent")
graph_builder.add_edge("formal_agent","casual_agent")
graph_builder.add_edge("casual_agent",END)

graph=graph_builder.compile()

def run_agent(user_query):
    state={"user_query":user_query,"research_info":"","casual_response":"","formal_response":""}
    state=graph.invoke(state)
    return state




