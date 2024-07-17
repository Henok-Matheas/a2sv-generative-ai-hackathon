# imports
import ast
from openai import OpenAI # for calling the OpenAI API
import pandas as pd  # for storing text and embeddings data
from config import initial_config as config
from cachetools import TTLCache
import os


# models
EMBEDDING_MODEL= "text-embedding-3-small"
GPT_MODEL = "gpt-3.5-turbo"

# initial message
INITIAL_CHATBOT_MESSAGE = {"role": "system", "content": "You are A2SV 2024 AI for Africa Hackathon Helper bot that answer questions about the A2SV as well as the 2024 AI for Africa Hackathon A2SV has prepared, when replying use emojis where necessary and also provide the answers in markup, especially any links you want to show. Show links using anchor tags in HTML. Give the answer in a clear and concise manner, don't provide too much information, it is better to provide a short and clear answer and then ask if the user wants more information. We don't want to overwhelm the user with too much information at a time. If you don't know the answer to a question don't try to make up an answer, just say you don't know."}

# token counts
HISTORY_TOKEN_BUDGET = 1500
CONTEXT_TOKEN_BUDGET = 2500

# embeddings
current_dir = os.path.dirname(__file__)
embeddings_path = os.path.join(current_dir, "A2SV_AI_for_Africa_Hackathon_Comprehensive_Doc.csv")
df = pd.read_csv(embeddings_path)

# openai setup
client = OpenAI(api_key=config.OPENAI_API_KEY)

#cache
CACHE_SIZE, CACHE_TIME = 1024, 1800
message_cache = TTLCache(maxsize=CACHE_SIZE, ttl=CACHE_TIME)
context_cache = TTLCache(maxsize=CACHE_SIZE, ttl=CACHE_TIME)

# convert embeddings from CSV str type back to list type
df['embedding'] = df['embedding'].apply(ast.literal_eval)