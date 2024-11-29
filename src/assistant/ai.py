from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts.image import ImagePromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import LlamaCpp
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import BaseMessage
from pydantic import Field
from typing import Union, Sequence
import os
import re
from typing import Optional, Any, Tuple
from utils.image_processing import encode_image, resize_suit
from dotenv import load_dotenv


def create_image_template(variable_name: str="path"):
    return \
    (
        "human",
        [
            {
                "type": "image_url",
                # "image_url": {"url": f"data:image/jpeg;base64,{{{variable_name}}}"},
                "image_url": {"url": f"{{{variable_name}}}"},
            }
        ],
    )

# システムプロンプトの設定
default_system_message = """
相手の質問に対して、1, 2行の簡潔な文章で返答をしてください。
出力は質問に対する返答のみで会話履歴をうまく使って返答してください。
"""

class AIAssistant:
    # recommend gpt-4o-mini if openai and gemini-1.5-flash-002 if google
    def __init__(self, provider: str='openai', model: str='gpt-4o-mini', use_img: bool=False, temperature: float=0.9, system_message: str=default_system_message, max_messages: int=10):
        self.use_img = use_img
        self.system_message = system_message
        self.memory = ChatMessageHistory()
        self.store = {}
        self.max_messages = max_messages
        self.session_id = 86

        # LLM 初期化
        load_dotenv('.env')
        # OpenAI LLM 初期化 (環境変数 OPENAI_API_KEY が必要)
        if provider == 'openai':
            self.llm = ChatOpenAI(model=model, temperature=temperature, timeout=None, max_retries=2)
        # Google Gemini API 初期化（環境変数 GOOGLE_API_KEY が必要）
        elif provider == 'google':
            self.llm = ChatGoogleGenerativeAI(model=model, temperature=temperature, max_token=None, timeout=None, max_retries=2)
        elif provider == 'local':
            try:
                from huggingface_hub import hf_hub_download, HfFileSystem
                from huggingface_hub.utils import validate_repo_id
            except ImportError:
                raise ImportError(
                    "Llama.from_pretrained requires the huggingface-hub package. "
                    "You can install it with `pip install huggingface-hub`."
                )
            repo_id = "alfredplpl/gemma-2-2b-jpn-it-gguf"
            filename = "gemma-2-2b-jpn-it-IQ4_XS.gguf"
            validate_repo_id(repo_id)
            # download the file
            model_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                subfolder=None,
                local_dir=None,
                local_dir_use_symlinks='auto',
                cache_dir=None,
            )
            # self.llm = LlamaCpp(model_path="./gemma-2-2b-jpn-it-IQ4_XS.gguf", temperature=temperature, max_tokens=None, top_p=1, verbose=True,)
            self.llm = LlamaCpp(model_path=model_path, temperature=temperature, max_tokens=None, top_p=1, verbose=True,)
        else:
            raise ProviderNotSupported(provider)

    def set_system_message(message: str):
        self.system_message = message

    def set_images(self, images: Tuple[str], compression: int=400) -> bool:
        for img in images: resize_suit(img, compression)
        self.image_prompts = [ create_image_template(f'image_{i}') for i in range(len(images))]
        self.images = {}
        for i, img in enumerate(images): self.images.update({f'image_{i}': encode_image(img)})
        return True

    def set_image_from_b64(self, image: str, compression: int=400) -> bool:
        # resize_suit(image, compression)
        self.image_prompts = [ create_image_template('image_0')]
        self.images = {'image_0': image}
        return True

    def ai_eval(self, question: str='this is user prompt'):
        # のちの外部 yaml から読むようにする
        template_array = [ ("system", self.system_message), ("human", "{question}。")]
        if self.use_img:
            for image_prompt in self.image_prompts: template_array.append(image_prompt)
        prompt_template = ChatPromptTemplate(template_array)
        # prompt_template = ChatPromptTemplate([
            # ("system", self.system_message),
            # ("human", "{question}。"),
            # HumanMessagePromptTemplate.from_template(image_prompt)
            # *self.image_prompts
        # ])

        chain = prompt_template | self.llm | StrOutputParser()
        # chain = prompt_template
        # chain = image_prompt
        prompt = {"question": question}
        if self.use_img: prompt |= self.images
        print('question:', question)
        # prompt = {"question": question}
        result = chain.invoke(prompt)
        print(result)
        return {"result": result}

    # セッションIDごとの会話履歴の取得
    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            # self.store[session_id] = ChatMessageHistory()
            self.store[session_id] = LimitedChatMessageHistory(self.max_messages) # 5turn
        return self.store[session_id]

    def ai_eval_stream(self, question: str='this is user prompt'):
        # のちの外部 yaml から読むようにする
        template_array = [ ("system", self.system_message), MessagesPlaceholder(variable_name="history"), ("human", "{question}。")]
        if self.use_img:
            for image_prompt in self.image_prompts: template_array.append(image_prompt)
        prompt_template = ChatPromptTemplate(template_array)

        chain = prompt_template | self.llm | StrOutputParser()
        # chain = prompt_template | self.llm

        # RunnableWithMessageHistoryの準備
        runnable_with_history = RunnableWithMessageHistory(
            chain,
            self._get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )
        # chain = prompt_template
        prompt = {"question": question}
        if self.use_img: prompt |= self.images
        # print('question:', question)
        # prompt_check = {"question": question, "history": get_session_history(self.session_id).messages}
        # print(prompt_template.invoke(prompt_check).to_messages())
        split_char = '[、。,;\n]+'
        cache = ''
        # for chunk in chain.stream(prompt):
        for chunk in runnable_with_history.stream(prompt, config={"configurable": {"session_id": self.session_id}}):
            cache += chunk
            res = re.split(split_char, cache)
            if len(res) != 1:
                cache = cache[len(res[0])+1:]
                print('response:', f'\"{res[0]}\"', ', cache:', f'\"{cache}\"')
                yield {"result": res[0]}

        if cache != '':
            yield {"result": cache}
        print("ChatHistory:", self.store)

class ProviderNotSupported(Exception):
    def __init__(self, arg=""):
        self.arg = arg

    def __str__(self):
        return (
            f"""Provider: {self.arg} は対応していません。
対応 Provider: [\"openai\", \"google\", \"local\"]
            """
        )


class LimitedChatMessageHistory(ChatMessageHistory):
    max_messages: int = Field(default=10)

    def __init__(self, max_messages=10):
        super().__init__()
        self.max_messages = max_messages

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        super().add_messages(messages)
        self._limit_messages()

    def _limit_messages(self):
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
