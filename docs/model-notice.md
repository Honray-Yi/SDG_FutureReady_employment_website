# Local embedding model notice

- Base model: [intfloat/multilingual-e5-small](https://huggingface.co/intfloat/multilingual-e5-small), model-card license: **MIT**.
- CPU ONNX conversion: [Xenova/multilingual-e5-small](https://huggingface.co/Xenova/multilingual-e5-small), pinned repository revision `761b726dd34fb83930e26aab4e9ac3899aa1fa78`.
- Quantized ONNX SHA-256: `f80102d3f2a1229f387d3c81909990d8945513e347b0eab049f7de3c6f98c193`.
- Tokenizer SHA-256: `0b44a9d7b51c3c62626640cda0e2c2f70fdacdc25bbbd68038369d14ebdf4c39`.
- Native embedding size: 384. Symmetric similarity uses `query: ` on both texts; masked mean pooling followed by normalization.
- No remote model code is loaded. Public files are provisioned once; inference is local.
- Model files in App Storage are copies of the public version-pinned assets, not user resumes.
- This general-purpose model is not trained or certified as a hiring/competency assessment tool.

## MIT license

Source: [Microsoft UniLM/E5 license](https://github.com/microsoft/unilm/blob/master/LICENSE).

Copyright (c) Microsoft Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
