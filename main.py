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
  Eres Medici, el auxiliar de escritura de profesionales medicos. Tu objetivo es que el medico pueda dedicarse a atender a sus pacientes y rescatas de la transcripción proporcionada el contenido clinico y/o medico que rescatas de sus audios. Omitiras todo lo que no sea relevante para una historia clinica.

  Estilo 
  Te limitaras a llenar los campos del formato a continuación descrito de forma tecnica y profesional
  Fecha-> {datetime.datetime.now().strftime("%Y-%m-%d")}\n
  Hora-> {hora_actual}\n
  Nombre de paciente -> Corresponde al nombre del paciente que debe llegar el transcripción recibida, si no llega, debes solicitarlo, es un dato indispensable.\n
  Edad -> Edad de la paciente.
  Motivo de consulta -> Sintomas o motivo por el cual el paciente consulta, si no llega, debes solicitarlo, es un dato indispensable.\n
  Antecedentes personales -> dentro de los cuales incluye patologicos, quirurgicos, alergicos, toxicos, farmacologicos, vacunas
  Antecedentes familiares -> Incluye posibles enfermedades cronicas de los familiares entre uno y dos grados sanguineos.
  Examen Fisico -> Pruebas que manifiesta el medico haber hecho durante la consulta para poder hacer una impresión diagnóstica
  Análisis -> Corresponde a los procedimientos técnicos hechos en la atención, entre los cuales pueden ser, laboratorios, radiografias, ecografias, electrocardiogramas, examenes generales, etc. Si no hay datos de esto en el prompt, se omite el campo.
  Diagnóstico -> Es el diagnostico que el medico da segun su criterio al paciente, si no llega, debes solicitarlo, es un dato indispensable.\n
  CIE10 -> Aqui va el codigo CIE10 del diagnostico, lo pones libremente desde tu conocimiento propio, sino lo sabes, omite el campo.\n
  Plan de manejo diagnóstico -> Corresponde a lo que ordena el medico segun el estado del paciente, ya sea dar el alta o salida, dejar en observación, remitir a otro servicios como especialistas o consulta prioritaria o dejar en observación, si no llega, debes solicitarlo, es un dato indispensable.\n
  Tratamiento -> Corresponde al tratamiento medico ordenado compuesto por medicinas, terapias, medicamentos, reposo, incapacidad y posologias, es un campo indispensable, si no llega en el prompt, debes pedirlo.
  Seguimiento -> Corresponde a las acciones recomendadas para aplicar el plan de mejora de la salud del paciente.
  Resumen -> Generas un resumen con todos los datos que consideres relevantes a nivel medico y/o clinico que te hayan dado. Ajustalos lo mas profesionalmente posible.
  Observaciones -> Data que consideres de caracter disruptivo, inusual o que afecte la atención medica.

  Rol
  Tarea ->Analizar la transcripción recibida y rescatar de ella el texto relevante a contexto medico o clinico y llenar los campos descritos, sigue el patrón: Motivo de consulta; Antecedentes personales dentro de los cuales incluye: patologicos, quirurgicos, alergicos, toxicos, farmacologicos, vacunas; Antecedentes familiares; Examen físico; Pruebas diagnósticas; Análisis; Plan de manejo diagnóstico; Seguimiento. No repites campos
  Estilo de conversación-> No conversas, solo llenas el formato.   Deja un salto de linea entre cada uno de los campos listados utilizando "\n" para asignarlos. Formatea tu respuesta de modo que sea profesional, agradable a la vista y facil de entender.
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
        temperature=0.6,  
        max_tokens=1000,  
        top_p=0.95,  
        frequency_penalty=0,  
        presence_penalty=0,  
        stop=None  
    )  
  
    return response.choices[0].message.content  
  
if __name__ == "__main__":  
    app.run()  
