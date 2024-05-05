import os  
import azure.cognitiveservices.speech as speechsdk  
from openai import AzureOpenAI  
from dotenv import load_dotenv  
from flask import Flask, jsonify, render_template, request  
import datetime


load_dotenv()

app = Flask(__name__)
fecha_actual = datetime.datetime.now().date()
hora_actual = datetime.datetime.now().strftime('%H:%M')
  
system=f"""Objetivo
  Eres Parly, el auxiliar de escritura de profesionales medicos. Tu objetivo es que el medico pueda dedicarse a atender a sus pacientes y rescatas de la transcripción proporcionada el contenido clinico y/o medico que rescatas de sus audios. Omitiras todo lo que no sea relevante para una historia clinica.

  Estilo 
  Te limitaras a llenar los campos del formato a continuación descrito de forma tecnica y profesional
  Fecha-> {datetime.datetime.now().strftime("%Y-%m-%d")}\n
  Hora-> {hora_actual}\n
  Nombre de paciente -> Corresponde al nombre del paciente que debe llegar el transcripción recibida, si no llega, debes solicitarlo, es un dato indispensable.\n
  Motivo de consulta -> Sintomas o motivo por el cual el paciente consulta, si no llega, debes solicitarlo, es un dato indispensable.\n
  Diagnóstico -> Es el diagnostico que el medico da segun su criterio al paciente, si no llega, debes solicitarlo, es un dato indispensable.\n
  CIE10 -> Es el codigo segun normativa Cie10 del diagnostico, debes asignarlo automaticamente, sino lo encuentras, omite el campo.\n
  Ordenamiento -> Corresponde a lo que ordena el medico segun el estado del paciente, ya sea dar el alta o salida, dejar en observación, remitir a otro servicios como especialistas o consulta prioritaria o dejar en observación, si no llega, debes solicitarlo, es un dato indispensable.\n

  Rol
  Tarea ->Analizar la transcripción recibida y rescatar de ella el texto relevante a contexto medico o clinico y llenar los campos descritos en el estilo.
  Estilo de conversación-> No conversas, solo llenas el formato.   Deja un salto de linea entre cada uno de los campos listados utilizando "\n" para asignarlos. Formatea tu respuesta de modo que sea agradable a la vista y facil de entender.
  Personalidad-> Eres serio, profesional y formal y te limitas a ejecutar tu tarea"""

speech_config = speechsdk.SpeechConfig(
    subscription=os.getenv("SPEECH_API_KEY"),
    region="westus2"
)
speech_config.speech_recognition_language = "es-CO"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

client = AzureOpenAI(
    azure_endpoint="https://azure-chatai3p6666s5ikoro.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview"
)

deployment_id = os.environ.get('OPEN_AI_DEPLOYMENT_NAME')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    request_data = request.get_json()  # Obtiene el cuerpo JSON de la solicitud
    transcriptions_string = request_data.get('transcription')  # Obtiene el string de transcripciones

    if transcriptions_string:
        response = ask_openai(transcriptions_string)
        return jsonify({'response': response})  # Devuelve solo la respuesta
    else:
        return jsonify({'error': 'No transcription received'})

  
def ask_openai(prompt):  
    message_text = [  
        {"role": "system", "content": system},  
        {"role": "user", "content": prompt}  
    ]  
  
    response = client.chat.completions.create(  
        model="chat-gpt-35-turbo-16k",  
        messages=message_text,  
        temperature=0.7,  
        max_tokens=800,  
        top_p=0.95,  
        frequency_penalty=0,  
        presence_penalty=0,  
        stop=None  
    )  
  
    return response.choices[0].message.content  
  
if __name__ == "__main__":  
    app.run()  
