import gradio as gr

def responder(mensaje, historial):
    respuesta = f"Has dicho: {mensaje}"
    return respuesta

chat = gr.ChatInterface(
    fn=responder,
    title="Mini ChatGPT",
    description="Chat simple de prueba."
)

chat.launch()


