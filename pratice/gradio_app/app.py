import gradio as gr
import requests

API_URL = "http://localhost:8000/ask"  # FastAPI endpoint
chat_history = []


def chat_fn(message):
    chat_history.append(("You", message))

    try:
        response = requests.post(API_URL, params={"question": message})
        if response.status_code == 200:
            reply = response.json().get("answer", "🤖 No answer found.")
        else:
            reply = f"❌ Error: {response.status_code}"
    except Exception as e:
        reply = f"❌ Exception: {str(e)}"

    chat_history.append(("AI", reply))
    return [(sender, msg) for sender, msg in chat_history]


with gr.Blocks(
    theme=gr.themes.Base(
        primary_hue="indigo",
        secondary_hue="rose",
        font=["Inter", "sans-serif"]
    ),
    css="""
    #chatbox {
        height: 550px;
        overflow-y: auto;
        background: white;
        border: 2px solid #eee;
        border-radius: 10px;
        padding: 16px;
    }

    .gr-chatbot {
        font-size: 16px;
        line-height: 1.5;
    }

    .gr-textbox {
        border-radius: 10px;
    }

    button {
        border-radius: 10px !important;
    }

    @media (prefers-color-scheme: dark) {
        #chatbox {
            background: #1e1e1e;
            border-color: #444;
        }

        .gr-chatbot {
            color: #fff;
        }
    }
    """
) as demo:

    gr.Markdown(
        "<h1 style='text-align: center;'>🤖 Elegant RAG Chatbot</h1>",
    )

    chatbot = gr.Chatbot(elem_id="chatbox", label="", height=550)

    with gr.Row():
        user_input = gr.Textbox(
            show_label=False,
            placeholder="Type your question here...",
            container=True,
            scale=9
        )
        send_btn = gr.Button("Send", scale=1)

    send_btn.click(fn=chat_fn, inputs=[user_input], outputs=[chatbot])
    user_input.submit(fn=chat_fn, inputs=[user_input], outputs=[chatbot])

demo.launch()
