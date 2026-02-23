#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 15 18:59:51 2026

@author: hounsousamuel
"""

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch, torch.nn.functional as F
path = "./MODELS_LLM_EBD_DOCS/MODEL/phi"

conf = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
    )

model = AutoModelForCausalLM.from_pretrained(path, trust_remote_code=True, attn_implementation='eager',device_map="cpu",
    low_cpu_mem_usage=True,)# quantization_config=conf,)
tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)

input_ = "Bonjour, ça va ?"
encode = tokenizer.encode(input_, return_tensors="pt")
decode = tokenizer.decode(encode[0])
print(encode, "\n", decode, "\n", tokenizer.pad_token, "\n", tokenizer.eos_token)

with torch.no_grad():
    gen = model.generate(
        encode, 
        do_sample=True,
        use_cache=False  # ← Désactive le cache
    )
print(gen)
try:
    print(tokenizer.decode(gen[0]))
except:
    print(tokenizer.decode(gen))

def generate(model, tokenizer, prompt, max_token=50, top_k=50, top_p=0.9, temperature=1.2, seq_len=256):
    with torch.no_grad():
        encode = torch.tensor(tokenizer.encode(prompt, return_tensors="pt"))
        gen = encode.clone()
        for _ in range(max_token):
            x = gen[:, -seq_len:]
            logits = model(x)
            logits = logits[:, -1, :] / temperature
            if top_k > 0:
                values = torch.topk(logits, k=top_k)[0]
                min_ = values[:, -1]
                idx_to_remove = logits < min_
                logits[:, idx_to_remove] = float("-inf")
            
            if top_p < 1:
                sort_value, sort_idx = torch.sort(logits, descending=True)
                probs = F.softmax(sort_value, dim=-1)
                cumsum = torch.cumsum(probs, dim=-1)
                idx_to_remove = cumsum > top_p
                idx_to_remove[1:] = idx_to_remove[:-1].clone()
                idx_to_remove[0, :] = False
                idx_to_remove = sort_idx[idx_to_remove]
                logits[idx_to_remove, :] = float("-inf")
            
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            gen = torch.cat([gen, next_token], dim=-1)
            if next_token.item() == tokenizer.eos_token:
                break
        return tokenizer.decode(gen.squeeze().cpu().clone().tolist())



while True:
    try:
        prompt = input("MEssage : ").strip()
        prompt += "\nNOTE IMPORTANTE: réponds en FRANCAIS."
        out = generate(model, tokenizer, prompt)
        print(out)
    except Exception as e:
        print(e)

            
