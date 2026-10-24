"""Concrete CPU ONNX E5 encoder. This module performs no network requests."""
from __future__ import annotations

from functools import lru_cache
import threading

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

from local_model_assets import MODEL_DIR, verify_assets
from semantic_catalogue import DIMENSIONS


class LocalModelError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def tokenizer() -> Tokenizer:
    try:
        verify_assets()
        result = Tokenizer.from_file(str(MODEL_DIR / "tokenizer.json"))
        result.no_truncation()
        result.no_padding()
        return result
    except Exception:
        raise LocalModelError("本地模型或分词器未就绪，请恢复并校验模型文件。") from None


class E5Encoder:
    def __init__(self):
        try:
            self.tokenizer = tokenizer()
            ort.disable_telemetry_events()
            options = ort.SessionOptions()
            options.intra_op_num_threads = 2
            options.inter_op_num_threads = 1
            self.session = ort.InferenceSession(
                str(MODEL_DIR / "onnx/model_quantized.onnx"), sess_options=options,
                providers=["CPUExecutionProvider"],
            )
            self.lock = threading.Lock()
            self.prefix = self.tokenizer.encode("query: ", add_special_tokens=False).ids
            self.bos = self.tokenizer.token_to_id("<s>")
            self.eos = self.tokenizer.token_to_id("</s>")
            self.pad = self.tokenizer.token_to_id("<pad>")
            if any(item is None for item in (self.bos, self.eos, self.pad)):
                raise ValueError("Required special tokens missing.")
        except LocalModelError:
            raise
        except Exception:
            raise LocalModelError("本地 ONNX 模型加载失败，请检查依赖、模型校验和及运行内存。") from None

    def encode(self, chunks: list[list[int]]) -> np.ndarray:
        if not chunks:
            raise LocalModelError("No chunks to encode.")
        pooled = []
        # Bound peak memory/CPU. The asynchronous service also rejects excess jobs.
        with self.lock:
            for start in range(0, len(chunks), 4):
                rows = [[self.bos] + self.prefix + chunk + [self.eos] for chunk in chunks[start:start + 4]]
                width = max(map(len, rows))
                if width > 512:
                    raise LocalModelError("模型单块长度超过上限；未截断输入。")
                ids = np.full((len(rows), width), self.pad, dtype=np.int64)
                mask = np.zeros_like(ids)
                for i, row in enumerate(rows):
                    ids[i, :len(row)], mask[i, :len(row)] = row, 1
                inputs = {"input_ids": ids, "attention_mask": mask, "token_type_ids": np.zeros_like(ids)}
                feed = {item.name: inputs[item.name] for item in self.session.get_inputs()}
                hidden = self.session.run(None, feed)[0]
                if hidden.shape != (len(rows), width, DIMENSIONS):
                    raise LocalModelError("Unexpected model output dimensions.")
                averaged = (hidden * mask[..., None]).sum(axis=1) / mask.sum(axis=1)[:, None]
                pooled.extend(averaged)
        return np.asarray(pooled, dtype="<f4")


@lru_cache(maxsize=1)
def encoder() -> E5Encoder:
    return E5Encoder()
