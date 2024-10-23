# GameAssistant
ゲームのアシスタントを作る

## Whisper Setup
### Compute Capability が低い場合
Compute Capability が低い場合、Ctranslate2 のバージョンを下げる必要がある
```bash
pip install ctranslate2=3.4.4
ln -s /path/to/lib/python3.10/site-packages/ctranslate2/ /path/to/lib/python3.10/site-packages/ctranslate2
```

```bash
$ export LD_LIBRARY_PATH=/path/to/lib/python3.10/site-packages/nvidia/cublas/lib/:/path/to/lib/python3.10/site-packages/nvidia/cudnn/lib
```

### WSL で実行する場合
1. CUDA のバージョンを確認
2. Windows の設定で既定のマイクを確認する
