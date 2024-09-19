from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts.image import ImagePromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
import os
from typing import Optional, Any, Tuple
from utils.image_processing import encode_image, resize_suit


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
system_message = """
あなたは優れたゲームアシスタントです。プレイヤからの質問に画面を見ながら回答してください。
"""

class AIAssistant:
    def __init__(self, provider: str='openai', model: str='gpt-4o-mini', temperature=0.9):
        # OpenAI LLM 初期化 (環境変数 OPENAI_API_KEY が必要)
        if provider == 'openai':
            self.llm = ChatOpenAI(model=model, temperature=temperature, max_retries=2)
        else:
            raise ProviderNotSupported(provider)

    def set_images(self, images: Tuple[str], compression: int=400) -> bool:
        for img in images: resize_suit(img, compression)
        self.image_prompts = [ create_image_template(f'image_{i}') for i in range(len(images))]
        self.images = {}
        for i, img in enumerate(images): self.images.update({f'image_{i}': encode_image(img)})
        return True

    def ai_eval(self, question: str='this is test'):
        # のちの外部 yaml から読むようにする
        prompt_template = ChatPromptTemplate([
            ("system", system_message),
            ("human", "{question}"),
            # HumanMessagePromptTemplate.from_template(image_prompt)
            *self.image_prompts
        ])
        print(prompt_template)

        # chain = prompt_template | self.llm | StrOutputParser()
        chain = prompt_template
        # chain = image_prompt
        prompt = {"question": question} | self.images
        result = chain.invoke(prompt)
        print(prompt)
        print(type(result))
        print(result)

        return {"result": result}

class ProviderNotSupported(Exception):
    def __init__(self, arg=""):
        self.arg = arg

    def __str__(self):
        return (
            f"""Provider: {self.arg} は対応していません。
対応 Provider: [\"openai\"]
            """
        )

