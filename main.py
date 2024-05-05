import os
import azure.cognitiveservices.speech as speechsdk
from openai import AzureOpenAI
from dotenv import load_dotenv
from flask import Flask, render_template, request
import datetime


load_dotenv()

app = Flask(__name__)
fecha_actual = datetime.datetime.now().date()
hora_actual = datetime.datetime.now().time()

client = AzureOpenAI(
  azure_endpoint = "https://azure-chatai3p6666s5ikoro.openai.azure.com/", 
  api_key=os.getenv("AZURE_OPENAI_KEY"),  
  api_version="2024-02-15-preview"
)

deployment_id = os.environ.get('OPEN_AI_DEPLOYMENT_NAME')
system=f"""Objetivo
  Eres Parly, el auxiliar de escritura de profesionales medicos. Tu objetivo es que el medico pueda dedicarse a atender a sus pacientes y rescatas de la transcripción proporcionada el contenido clinico y/o medico que rescatas de sus audios. Omitiras todo lo que no sea relevante para una historia clinica.

  Estilo 
  Te limitaras a llenar los campos del formato a continuación descrito de forma tecnica y profesional
  Fecha-> {datetime.datetime.now().strftime("%Y-%m-%d")}
  Hora-> {hora_actual}
  Nombre de paciente -> Corresponde al nombre del paciente que debe llegar el transcripción recibida, si no llega, debes solicitarlo, es un dato indispensable.
  Motivo de consulta -> Sintomas o motivo por el cual el paciente consulta, si no llega, debes solicitarlo, es un dato indispensable.
  Diagnóstico -> Es el diagnostico que el medico da segun su criterio al paciente, si no llega, debes solicitarlo, es un dato indispensable.
  CIE10 -> Es el codigo segun normativa Cie10 del diagnostico, debes asignarlo automaticamente, sino lo encuentras, omite el campo.
  Ordenamiento -> Corresponde a lo que ordena el medico segun el estado del paciente, ya sea dar el alta o salida, dejar en observación, remitir a otro servicios como especialistas o consulta prioritaria o dejar en observación, si no llega, debes solicitarlo, es un dato indispensable.

  Rol
  Tarea ->Analizar la transcripción recibida y rescatar de ella el texto relevante a contexto medico o clinico y llenar los campos descritos en el estilo.
  Estilo de conversación-> No conversas, solo llenas el formato.
  Personalidad-> Eres serio, profesional y formal y te limitas a ejecutar tu tarea"""

speech_config = speechsdk.SpeechConfig(
  subscription=os.getenv("SPEECH_API_KEY"), 
  region="westus2"
)

audio_config = speechsdk.audio.AudioConfig(
  use_default_microphone=True)
speech_config.speech_recognition_language="es-CO"
speech_recognizer = speechsdk.SpeechRecognizer(
  speech_config, 
  audio_config)

def ask_openai(prompt):
    message_text = [{"role": "system", "content": system},{"role": "user", "content": prompt}]

    response = client.chat.completions.create(
    model="chat-gpt-35-turbo-16k", # model = "deployment_name"
    messages = message_text,
    temperature=0.7,
    max_tokens=800,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None
    )

   
    print("\nResponse from OpenAI:", response.choices[0].message.content)

def chat_with_open_ai():
    while True:
        print("ParlaDoc esta oyendote, para terminar la escucha, solo di Fin de atención")
        try:
            speech_recognition_result = speech_recognizer.recognize_once_async().get()

            # If speech is recognized, send it to Azure OpenAI and listen for the response.
            if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                if speech_recognition_result.text == "Fin de atención":
                    print("Consulta finalizada.")
                    break
                print("Recognized speech:", speech_recognition_result.text)
                ask_openai(speech_recognition_result.text)
            elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized:", speech_recognition_result.no_match_details)
                break
            elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_recognition_result.cancellation_details
                print("Speech Recognition canceled:", cancellation_details.reason)
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print("Error details:", cancellation_details.error_details)
                break
        except EOFError:
            break

# Main

try:
    chat_with_open_ai()
except Exception as err:
    print("Encountered exception:", err)
