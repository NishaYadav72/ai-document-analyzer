from langchain_community.llms import Ollama

llm = Ollama(model="gemma3:1b")

def ask_llm(prompt, context):

    message = f"""
    Use the following document content to answer the question.

    Document:
    {context}

    Question:
    {prompt}
    """

    response = llm.invoke(message)

    return response