import os
import requests
import dashscope
import gradio as gr
# Required packages: dashscope, gradio


# Retrieve API key from environment variable
def get_api_key():
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise EnvironmentError("DASHSCOPE_API_KEY environment variable not set.")
    return api_key


# Synthesize speech using Qwen-TTS API
# Parameters:
#   text: Text content to synthesize
#   voice: Voice type selection
#   model: TTS model version
# Returns: URL of the generated audio file
def synthesize_speech(text, voice="Dylan", model="qwen-tts-latest"):
    api_key = get_api_key()
    try:
        response = dashscope.audio.qwen_tts.SpeechSynthesizer.call(
            model=model,
            api_key=api_key,
            text=text,
            voice=voice,
        )
        
        # Validate API response
        if response is None:
            raise RuntimeError("API call returned None response")
        
        if response.output is None:
            raise RuntimeError("API call failed: response.output is None")
        
        if not hasattr(response.output, 'audio') or response.output.audio is None:
            raise RuntimeError("API call failed: response.output.audio is None or missing")
        
        audio_url = response.output.audio["url"]
        return audio_url
    except Exception as e:
        raise RuntimeError(f"Speech synthesis failed: {e}")


# Download audio from URL and save to local file
# Parameters:
#   audio_url: URL of the audio file to download
#   save_path: Local path to save the audio file
def download_audio(audio_url, save_path):
    try:
        resp = requests.get(audio_url, timeout=10)
        resp.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(resp.content)
        print(f"Audio file saved to: {save_path}")
    except Exception as e:
        raise RuntimeError(f"Download failed: {e}")


# Original command-line main function
def main():
    text = (
        """Hello, I am a Qwen-TTS. How can I help you today?"""
    )
    save_path = "downloaded_audio.wav"
    try:
        audio_url = synthesize_speech(text)
        download_audio(audio_url, save_path)
    except Exception as e:
        print(e)


# Available voice options: (display_name, voice_id)
voice_options = [
    ("Chelsie (female)", "Chelsie"),
    ("Cherry (female)", "Cherry"),
    ("Ethan (male)", "Ethan"),
    ("Serena (female)", "Serena"),
    ("Dylan (Beijing dialect - Male)", "Dylan"),
    ("Jada (Shanghainese - Female)", "Jada"),
    ("Sunny (Sichuan dialect - Female)", "Sunny"),
]

# Gradio interface handler function
def tts_interface(text, save_path, voice):
    try:
        audio_url = synthesize_speech(text, voice=voice)
        download_audio(audio_url, save_path)
        return f"The audio has been saved to: {save_path}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Launch Gradio web interface
def launch_gui():
    with gr.Blocks(title="Qwen-TTS WebUI") as demo:
        # Main title
        gr.Markdown("<center><h1 style=\"font-size: 36px; font-weight: bold\">Qwen-TTS WebUI</h1></center>")
        
        # Create layout with input and output sections
        with gr.Row():
            with gr.Column():
                # Text input component
                text_input = gr.Textbox(label="Input text", lines=5, placeholder="please input text here...")
                # Save path input component
                save_path_input = gr.Textbox(label="save path", value="audio.wav", placeholder="please input save path here..., eg.audio.wav")
                # Voice selection dropdown
                voice_dropdown = gr.Dropdown(choices=voice_options, label="Select voice", value="Dylan")
                # Generate button
                submit_btn = gr.Button("Generate Voice")
            with gr.Column():
                # Output status display
                output_text = gr.Textbox(label="Result", interactive=False)
        
        # Set up button click action
        submit_btn.click(
            fn=tts_interface,
            inputs=[text_input, save_path_input, voice_dropdown],
            outputs=output_text
        )
    
    # Launch the web interface
    demo.launch()

# Run the GUI when the script is executed directly
if __name__ == "__main__":
    launch_gui()
