from application import app, utils
from flask import render_template, url_for, request, redirect, session
import secrets
import os
from application.forms import MyForm

# OCR
import cv2 as cv
import pytesseract
from PIL import Image
import numpy as np

from gtts import gTTS

@app.route("/")
def index():
    return render_template("index.html", title = 'Homepage')


@app.route("/upload", methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        
        # sentence = ""
        
        # GET FILE NAMES
        f = request.files.get('file')
        filename, extension = f.filename.split(".")
        generated_filename = secrets.token_hex(10) + f".{extension}"
        
        # SAVE TO LOCATION
        file_location = os.path.join(app.config['UPLOADED_PATH'], generated_filename)

        f.save(file_location)
        
        # OCR PROCCESS
        pytesseract.pytesseract.tesseract_cmd = r'C:\Users\ASUS\AppData\Local\Tesseract-OCR\tesseract.exe'
        
        img = cv.imread(file_location)
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        
        img = cv.threshold(img, 100, 255, cv.THRESH_BINARY)[1]
        img = cv.GaussianBlur(img, (1, 1), 0)
        
        text = pytesseract.image_to_string(img)
        
                
        # print(text)
        
        session["text"] = text
            
        os.remove(file_location)
            
        return redirect("/decoded/")

    else:
           return render_template("upload.html", title="Home")


@app.route("/decoded", methods=['POST', 'GET'])
def decoded():
    text = session.get("text")
    
    form = MyForm()
    
    if request.method == "POST":
        
        generated_audio_filename = secrets.token_hex(10) + ".mp4"
        
        text_data = form.text_field.data
        translate_to = form.language_field.data
        
        translated_text = utils.translate_text(text_data, translate_to)
        
        form.text_field.data = translated_text
        # print(text_data)
        
        tts = gTTS(translated_text, lang=translate_to)
        
        file_location = os.path.join(app.config["AUDIO_FILE_UPLOAD"],
                                     generated_audio_filename
                                     )
        
        tts.save(file_location)
        
        return render_template("decoded.html", form=form, audio=True, file=generated_audio_filename)
    
    else:
        form.text_field.data = text
        session["text"] = ""
        return render_template("decoded.html", form = form, audio=False)
