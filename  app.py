from unsloth import FastVisionModel
from transformers import TextIteratorStreamer
from PIL import Image
from threading import Thread
import gradio as gr
import time

use_qwen = False
ckpt = "hasibzunair/llama-3.2-vision-11b-instruct-no-enc-mm-exr"
model, tokenizer = FastVisionModel.from_pretrained(
    ckpt,
    load_in_4bit = True,
    use_gradient_checkpointing = "unsloth",
)
FastVisionModel.for_inference(model)

def bot_streaming(message, history, max_new_tokens=128):

    txt = message["text"]
    ext_buffer = f"{txt}"

    messages= []
    images = []

    # Check if current message contains an image
    has_new_image = len(message["files"]) == 1

    if not has_new_image:
        for i, msg in enumerate(history):
            if isinstance(msg[0], tuple):
                messages.append({"role": "user", "content": [{"type": "text", "text": history[i+1][0]}, {"type": "image"}]})
                messages.append({"role": "assistant", "content": [{"type": "text", "text": history[i+1][1]}]})
                images.append(Image.open(msg[0][0]).convert("RGB"))
            elif isinstance(history[i-1], tuple) and isinstance(msg[0], str):
                # messages are already handled
                pass
            elif isinstance(history[i-1][0], str) and isinstance(msg[0], str):
                messages.append({"role": "user", "content": [{"type": "text", "text": msg[0]}]})
                messages.append({"role": "assistant", "content": [{"type": "text", "text": msg[1]}]})

    # Process current message
    if has_new_image:
        if isinstance(message["files"][0], str):  # examples
            image = Image.open(message["files"][0]).convert("RGB")
        else:  # regular input
            image = Image.open(message["files"][0]["path"]).convert("RGB")
        images = [image]  # Reset images list to only contain current image
        messages = [{"role": "user", "content": [{"type": "text", "text": txt}, {"type": "image"}]}]  # Reset messages
    else:
        messages.append({"role": "user", "content": [{"type": "text", "text": txt}]})

    texts = tokenizer.apply_chat_template(messages, add_generation_prompt = True)
    inputs = tokenizer(images, texts, add_special_tokens=False, return_tensors="pt").to("cuda")


    streamer = TextIteratorStreamer(tokenizer, skip_special_tokens=True, skip_prompt=True)
    generation_kwargs = dict(**inputs, streamer=streamer, max_new_tokens=max_new_tokens, use_cache = True, temperature = 1.5, min_p = 0.1)
    generated_text = ""

    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()
    buffer = ""

    for new_text in streamer:
        buffer += new_text
        time.sleep(0.01)
        yield buffer

INTRO_TEXT = """[FitLensAI](https://github.com/hasibzunair/FitLensAI) is a multimodal large language model with multilingual (English and বাংলা) and multi-turn conversational capabilities, that helps you understand fitness workouts from images. 🤖
\n\n
Upload an image of a workout, and start chatting about it in English or বাংলা, and reach your fitness goals! 🤾‍♀️
"""

demo = gr.ChatInterface(fn=bot_streaming, title="🏋️‍♂️ FitLensAI - Snap, Ask, Understand Your Exercise",
      textbox=gr.MultimodalTextbox(placeholder="Add an image and ask FitLensAI about your exercise..."),
      cache_examples=False,
      description=INTRO_TEXT,
      stop_btn="Stop Generation",
      fill_height=True,
      multimodal=True,
      css="footer{display:none !important}")

demo.launch(server_name="0.0.0.0", 
            server_port=7860, 
            share=True
            )