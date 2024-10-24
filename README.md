# GameAssistant
Multi-Modal LLM による Windows 上でのリアルタイムなゲームアシスタントを実現します。

## Providers for LLMs
対応するモデルのプロバイダは以下のとおりです。（リアルタイム性のために、高速、軽量なモデルの使用を推奨します）
- OpenAI
- Google Gemini API
- llama.cpp & GGUF モデル

## Requirements
以下の外部ツールを必要とします。
- [voicevox_engine](https://github.com/VOICEVOX/voicevox_engine)
  - 音声合成を行う API サーバ
  - リアルタイム性確保のために、GPU の搭載された別のマシン上で実行することを推奨
- [GameAssistantCaptureServer](https://github.com/pacificbelt30/GameAssistantCaptureServer)
  - Windows 上のキャプチャ画像を取得するための API サーバ
  - WSL 上で実行する場合に必要

### WSL で実行する場合の確認項目
1. Windows の設定で既定のマイクとスピーカを設定する
2. Host Windows 上で画面キャプチャサーバ(GameAssistantCaptureServer)の実行

## Usage
### 画面キャプチャサーバの起動
```bash
> poetry run python3 uvicorn src.main:app --host=0.0.0.0
```

### 対話アプリの起動
以下のコマンドを実行する。（初回のみモデルのダウンロードに時間を要します）
```bash
# voicevox_engine とゲームアシスタントの実行が同じマシン上である場合
$ poetry run python3 src/main.py http://localhost:50021

# エンジンが稼働している別のサーバがある場合
$ poetry run python3 src/main.py http://{VOICEVOX_ENGINE_IP}:{VOICEVOX_ENGINE_PORT}
```

## Whisper Setup (deprecated)
現在は音声認識を [reasonspeech-k2-v2](https://huggingface.co/reazon-research/reazonspeech-k2-v2) に移行したため、非推奨です。
### Compute Capability が低い場合
Compute Capability が低い場合、Ctranslate2 のバージョンを下げる必要がある
```bash
pip install ctranslate2=3.4.4
ln -s /path/to/lib/python3.10/site-packages/ctranslate2/ /path/to/lib/python3.10/site-packages/ctranslate2
```

```bash
$ export LD_LIBRARY_PATH=/path/to/lib/python3.10/site-packages/nvidia/cublas/lib/:/path/to/lib/python3.10/site-packages/nvidia/cudnn/lib
```

