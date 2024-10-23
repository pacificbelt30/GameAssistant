from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts.image import ImagePromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import LlamaCpp
import os
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
                "image_url": {"url": f"data:image/jpeg;base64,{{{variable_name}}}"},
            }
        ],
    )

# システムプロンプトの設定
default_system_message = """
あなたは優れたゲームアシスタントです。プレイヤからの質問に画面を見ながら回答してください。
"""

class AIAssistant:
    # recommend gpt-4o-mini if openai and gemini-1.5-flash-002 if google
    def __init__(self, provider: str='openai', model: str='gpt-4o-mini', temperature: int=0.9, system_message: str=default_system_message):
        self.system_message = system_message

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

    def ai_eval(self, question: str='this is user prompt'):
        # のちの外部 yaml から読むようにする
        prompt_template = ChatPromptTemplate([
            ("system", self.system_message),
            ("human", "{question}"),
            # HumanMessagePromptTemplate.from_template(image_prompt)
            # *self.image_prompts
        ])
        # print(prompt_template)

        chain = prompt_template | self.llm | StrOutputParser()
        # chain = prompt_template
        # chain = image_prompt
        # prompt = {"question": question} | self.images
        print('question:', question)
        prompt = {"question": question}
        result = chain.invoke(prompt)
        # print(prompt)
        # print(type(result))
        print(result)

        return {"result": result}

class ProviderNotSupported(Exception):
    def __init__(self, arg=""):
        self.arg = arg

    def __str__(self):
        return (
            f"""Provider: {self.arg} は対応していません。
対応 Provider: [\"openai\", \"google\"]
            """
        )

