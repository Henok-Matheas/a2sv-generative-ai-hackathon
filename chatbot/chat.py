# imports
from typing import List  # for converting embeddings saved as strings back to arrays
import pandas as pd  # for storing text and embeddings data
import tiktoken  # for counting tokens
from scipy import spatial  # for calculating vector similarities for search
from cachetools import cached
from utils.logger import logging
from chatbot.constants import (CONTEXT_TOKEN_BUDGET, HISTORY_TOKEN_BUDGET, INITIAL_CHATBOT_MESSAGE, client, EMBEDDING_MODEL, GPT_MODEL, df, message_cache, context_cache)

# search function
def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 1
) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response.data[0].embedding
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embedding"]))
        for _, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def query_context(query: str, df: pd.DataFrame, model: str, token_budget: int) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    strings, _ = strings_ranked_by_relatedness(query, df, top_n=2)

    contexts = []
    for string in strings:
        next_article = f'\n\A2SV section:\n"""\n{string}\n"""'
        if (
            num_tokens(next_article, model=model)
            > token_budget
        ):
            break
        else:
            contexts.append(next_article)
    return contexts

@cached(message_cache)
def get_messages(chat_id: int) -> List:
    messages = []
    return messages

@cached(context_cache)
def get_contexts(chat_id: int) -> List:
    contexts = []
    return contexts


def validate_messages_token_count(messages: List, budget: int) -> None:
    """Check if the token count is within the limit."""
    token_count = 0
    for message in messages:
        token_count += num_tokens(message["content"] + message["role"])

    while token_count > budget and messages:
        token_count -= num_tokens(message["content"] + message["role"])
        messages.pop()


def validate_context_token_count(contexts: List, budget: int) -> None:
    """Check if the token count is within the limit."""
    token_count = 0
    for context in contexts:
        token_count += num_tokens(context)

    while token_count > budget and contexts:
        token_count -= num_tokens(context)
        contexts.pop()

def ask(chat_id: int, query: str, df: pd.DataFrame = df, model: str = GPT_MODEL, token_budget: int = 4096 - 500, print_message: bool = False,) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""

    messages = get_messages(chat_id=chat_id)
    validate_messages_token_count(messages, HISTORY_TOKEN_BUDGET)

    # logging.info(f"cache messages: {messages}")

    contexts = get_contexts(chat_id=chat_id)
    current_contexts = query_context(query, df, model=model, token_budget=token_budget)
    validate_context_token_count(contexts, CONTEXT_TOKEN_BUDGET - num_tokens("\n".join(current_contexts)))
    contexts.extend(current_contexts)

    content = """
                Use the below texts about A2SV and the Hackathon as well as conversation history as context for answering questions. If the answer cannot be found in the articles, write "I could not find an answer."

                Articles about A2SV and the Hackathon it has prepared:
                {contexts}

                Question: {query}
            """.format(contexts="\n".join(contexts), query=query)
    
    message = {"role": "user", "content": content}
    if print_message:
        print(content)

    try:
        response = client.chat.completions.create(
            model=model,
            messages= [INITIAL_CHATBOT_MESSAGE] + messages + [message],
            temperature=0
        )
        response_message = response.choices[0].message.content

        messages.append({"role": "user", "content": query})
        messages.append({"role": "system", "content": response_message})

        return response_message
    except Exception as e:
        logging.info(e)
        raise Exception("Couldn't generate response, please try again!")