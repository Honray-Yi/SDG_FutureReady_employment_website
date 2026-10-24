"""Concrete local E5 pipeline; no external analysis calls or heuristic fallback."""
from __future__ import annotations

import asyncio
from collections import deque
from pathlib import Path
import time

import numpy as np
from local_encoder import LocalModelError, encoder, tokenizer
from local_model_assets import assets_present

from semantic_cache import InvalidCache, load_cache, save_cache, unit_rows
from semantic_catalogue import (
    MODEL, DIMENSIONS, CHUNK_TOKENS, MAX_INPUT_TOKENS, AGGREGATION,
    CATALOGUE_PATH, job_document, load_catalogue, normalize_text, sha256,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CACHE = ROOT / ".cache/futureready/local_e5_job_embeddings.npz"


class AnalysisError(Exception):
    def __init__(self, code: str, message: str, http_status: int = 503):
        super().__init__(message)
        self.code, self.message, self.http_status = code, message, http_status


def tokenize_chunks(text: str) -> tuple[list[list[int]], list[int]]:
    try:
        tokens = tokenizer().encode(normalize_text(text), add_special_tokens=False).ids
    except Exception:
        raise AnalysisError("model_unavailable", "本地模型分词器未就绪，请恢复并校验模型文件。") from None
    if not tokens:
        raise AnalysisError("empty_text", "请输入有效的经历文本。", 422)
    if len(tokens) > MAX_INPUT_TOKENS:
        raise AnalysisError(
            "too_many_tokens",
            f"文本超过 {MAX_INPUT_TOKENS} token 上限；请精简后重试，不会自动截断。", 422,
        )
    chunks = [tokens[i:i + CHUNK_TOKENS] for i in range(0, len(tokens), CHUNK_TOKENS)]
    return chunks, [len(chunk) for chunk in chunks]


def aggregate(vectors: np.ndarray, lengths: list[int]) -> np.ndarray:
    result = np.average(vectors, axis=0, weights=lengths).astype("<f4")
    norm = float(np.linalg.norm(result))
    if not np.isfinite(result).all() or norm < 1e-8:
        raise AnalysisError("invalid_embedding", "向量结果无效；未生成推荐。", 502)
    return result / norm


class SemanticMatcher:
    def __init__(self, catalogue_path: Path = CATALOGUE_PATH, cache_path: Path = DEFAULT_CACHE):
        self.jobs, self.configuration = load_catalogue(catalogue_path)
        self.cache_path = cache_path
        self.matrix: np.ndarray | None = None
        self.cache_error: str | None = None
        self.index_lock = asyncio.Lock()
        self.analysis_slots = asyncio.Semaphore(2)
        self.requests: deque[float] = deque()
        try:
            self.matrix = load_cache(self.cache_path, self.configuration)
        except InvalidCache as exc:
            self.cache_error = str(exc)

    def status(self) -> dict:
        model_ready = assets_present()
        if self.cache_error:
            state, message = "cache_invalid", self.cache_error
        elif not model_ready:
            state, message = "model_missing", "本地模型文件尚未就绪，请恢复已保存的开源模型。无需 API 密钥。"
        elif self.matrix is None:
            state, message = "awaiting_index", "首次分析会在本机生成职业向量缓存；不调用外部分析 API，无需密钥。"
        else:
            state, message = "ready", "本地多语言模型与职业向量缓存已就绪，无需 API 密钥，可以进行语义分析。"
        return {
            "mode": "local_text_embedding", "model": MODEL, "dimensions": DIMENSIONS,
            "occupation_count": len(self.jobs),
            "catalogue_hash": self.configuration["catalogue_hash"],
            "model_ready": model_ready, "cache_ready": self.matrix is not None,
            "state": state, "message": message,
            "score_semantics": "余弦相似度 [-1,1]，仅衡量文本语义接近程度；不是技能熟练度、录用概率或就业市场需求。",
            "privacy": "只接受合成资料。解析、分词和向量推理均在本应用后端完成，不发送到外部分析服务；不持久保存简历原文或向量。模型文件仅在安装或构建时下载。",
            "catalogue_basis": "用户提供的 65 职业描述 CSV；不是官方职业能力标准或实时职位空缺。",
        }

    def check_configuration(self) -> None:
        status = self.status()
        if status["state"] in ("model_missing", "cache_invalid"):
            raise AnalysisError(status["state"], status["message"])

    async def embed(self, chunks: list[list[int]]) -> np.ndarray:
        try:
            # The encoder reads version-pinned local assets only. No outbound API.
            vectors = await asyncio.to_thread(lambda: encoder().encode(chunks))
            return unit_rows(vectors, len(chunks))
        except LocalModelError:
            raise AnalysisError("model_unavailable", "本地向量模型未能完成推理，请检查模型文件与运行内存。") from None
        except (ValueError, TypeError, AttributeError):
            raise AnalysisError("invalid_embedding", "本地模型返回的向量无效；未使用该结果。", 503) from None
        except Exception:
            raise AnalysisError("local_inference_failed", "本地推理暂时无法完成，请检查运行内存或稍后重试。") from None

    async def ensure_index(self, force: bool = False) -> np.ndarray:
        if force:
            # Only called by the local, explicit --rebuild CLI, not public endpoints.
            self.cache_error = None
        self.check_configuration()
        async with self.index_lock:
            if self.matrix is not None and not force:
                return self.matrix
            chunks, spans = [], []
            for job in self.jobs:
                parts, lengths = tokenize_chunks(job_document(job))
                spans.append((len(chunks), len(chunks) + len(parts), lengths))
                chunks.extend(parts)
            # The curated catalogue is small. All 65 short documents fit one batch.
            embedded = await self.embed(chunks)
            matrix = np.stack([
                aggregate(embedded[start:end], lengths) for start, end, lengths in spans
            ]).astype("<f4")
            try:
                save_cache(self.cache_path, matrix, self.configuration)
            except OSError:
                raise AnalysisError("cache_write_failed", "无法写入职业缓存，请检查服务目录权限；未缓存简历。") from None
            self.matrix, self.cache_error = matrix, None
            return matrix

    async def match(self, text: str, top_k: int = 65) -> dict:
        self.check_configuration()
        normalized = normalize_text(text)
        if len(normalized) < 20:
            raise AnalysisError("short_text", "请提供至少 20 个字符的合成经历描述。", 422)
        # Small per-process safety limit, not production-grade authentication/quota.
        now = time.monotonic()
        while self.requests and self.requests[0] < now - 3600:
            self.requests.popleft()
        try:
            await asyncio.wait_for(self.analysis_slots.acquire(), timeout=0.05)
        except TimeoutError:
            raise AnalysisError("busy", "已有分析正在进行，请稍后重试。", 429) from None
        try:
            if len(self.requests) >= 30:
                raise AnalysisError("analysis_limit", "本服务每小时最多接受 30 次分析，请稍后重试。", 429)
            self.requests.append(now)
            chunks, lengths = await asyncio.to_thread(tokenize_chunks, normalized)
            matrix = await self.ensure_index()
            resume = aggregate(await self.embed(chunks), lengths)
            similarities = np.clip(matrix @ resume, -1, 1)
            order = sorted(range(len(self.jobs)), key=lambda i: (-float(similarities[i]), self.jobs[i]["job_id"]))
            best = float(similarities[order[0]])
            return {
                "rankings": [
                    {**self.jobs[i], "rank": rank + 1,
                     "similarity": round(float(similarities[i]), 6),
                     "relative_difference": round(best - float(similarities[i]), 6)}
                    for rank, i in enumerate(order[:top_k])
                ],
                "status": self.status(), "input_sha256": sha256(normalized),
                "input_tokens": sum(lengths), "chunk_count": len(chunks),
                "aggregation": AGGREGATION,
                "catalogue_hash": self.configuration["catalogue_hash"],
            }
        finally:
            self.analysis_slots.release()
