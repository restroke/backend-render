from flask import Flask, request
from flask_cors import CORS
import yagmail
import os
import time
import random
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/api/enviar-documentos', methods=['POST'])
def enviar_documentos():
    tipos_esperados = ["rg", "cpf", "comprovante"]
    arquivos = {}

    for tipo in tipos_esperados:
        file = request.files.get(tipo)
        if file is None:
            return { "error": f"Arquivo '{tipo}' não enviado" }, 400
        arquivos[tipo] = file

    try:
        nome = request.form.get("nome", "").upper()
        sobrenome = request.form.get("sobrenome", "").upper()
        contrato = request.form.get("contrato", "")
        email = request.form.get("email", "")

        caminhos = []

        for tipo, file in arquivos.items():
            rotulo = tipo.upper()
            timestamp = int(time.time())
            aleatorio = random.randint(100, 999)
            novo_nome = f"{rotulo}_{nome}_{sobrenome}_{timestamp}_{aleatorio}.pdf".replace(" ", "_")

            file.save(novo_nome)
            caminhos.append(novo_nome)

        assunto = f"DOCUMENTOS - {nome} {sobrenome} - CONTRATO {contrato}"

        yag = yagmail.SMTP(user=os.getenv("EMAIL_USER"), password=os.getenv("EMAIL_PASS"))
        yag.send(
            to=os.getenv("EMAIL_DESTINO"),
            subject=assunto,
            contents=f"Documentos enviados por: {nome} {sobrenome}\nEmail: {email}\nContrato: {contrato}",
            attachments=caminhos
        )

        for caminho in caminhos:
            os.remove(caminho)

        return { "success": True }, 200

    except Exception as e:
        print("Erro ao enviar e-mail:", e)
        return { "error": "Falha ao enviar e-mail" }, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
