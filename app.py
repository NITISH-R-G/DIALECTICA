import gradio as gr


def echo_message(message: str) -> str:
    message = (message or "").strip()
    if not message:
        return "Please type a message."
    return message


with gr.Blocks(title="DIALECTICA") as demo:
    gr.Markdown(
        """
        # DIALECTICA

        Live demo (Gradio). Type something and the app will echo it back.
        """
    )

    with gr.Row():
        inp = gr.Textbox(label="Message", placeholder="Hello, DIALECTICA!")
    out = gr.Textbox(label="Echo")
    btn = gr.Button("Echo")

    btn.click(fn=echo_message, inputs=inp, outputs=out)
    inp.submit(fn=echo_message, inputs=inp, outputs=out)


if __name__ == "__main__":
    demo.launch()

