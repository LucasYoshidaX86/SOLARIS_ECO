
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import math

app = Flask(__name__)
CORS(app)

def carregar_json(caminho):
    with open(caminho, encoding='utf-8') as arquivo:
        return json.load(arquivo)

def calcular_sistema(consumo_mensal, tarifa, hsp):
    perdas = 0.8
    potencia_kwp = consumo_mensal / (hsp * 30 * perdas)
    producao_anual = potencia_kwp * hsp * 365 * perdas
    potencia_modulo = 0.55
    num_modulos = math.ceil(potencia_kwp / potencia_modulo)
    potencia_ajustada = num_modulos * potencia_modulo
    area_necessaria = num_modulos * 2.1
    peso_estimado = num_modulos * 24
    return {
        "potencia_kwp": round(potencia_ajustada, 2),
        "num_modulos": num_modulos,
        "producao_anual_kwh": round(producao_anual, 0),
        "area_m2": round(area_necessaria, 2),
        "peso_kg": round(peso_estimado, 2)
    }

@app.route('/calcular', methods=['POST'])
def calcular():
    dados = request.get_json()
    estado_id = dados.get('estado_id')
    cidade_id = dados.get('cidade_id')
    distribuidora_id = dados.get('distribuidora_id')
    consumo = dados.get('consumo')
    tipo_tarifa = dados.get('tipo_tarifa')
    estados = carregar_json('estados.json')
    cidades = carregar_json('cidades.json')
    distribuidoras = carregar_json('distribuidoras.json')
    hsp_dados = carregar_json('hsp_estado.json')
    estado = next((e for e in estados if e['ID'] == str(estado_id)), None)
    cidade = next((c for c in cidades if c['ID'] == str(cidade_id)), None)
    distribuidora = next((d for d in distribuidoras if d['ID'] == distribuidora_id), None)
    hsp_info = next((h for h in hsp_dados if h['Estado'] == int(estado_id)), None)
    if not (estado and cidade and distribuidora and hsp_info):
        return jsonify({"erro": "Dados não encontrados."}), 404
    hsp = hsp_info['hsp_estado']
    tarifa = distribuidora[tipo_tarifa]
    resultado = calcular_sistema(consumo, tarifa, hsp)
    co2_reduzido = resultado['producao_anual_kwh'] * 0.001747
    arvores_equivalentes = resultado['producao_anual_kwh'] * 0.000012
    km_evitados = resultado['producao_anual_kwh'] * 0.1
    economia_mensal = consumo * tarifa
    economia_30_anos = economia_mensal * 12 * 30
    economia_acumulada = [round(economia_mensal * 12 * ano, 2) for ano in range(2, 32, 2)]
    return jsonify({
        "estado": estado['Nome'],
        "cidade": cidade['Nome'],
        "tarifa": tarifa,
        "economia_mensal": round(economia_mensal, 2),
        "economia_30_anos": round(economia_30_anos, 2),
        "co2_reduzido": round(co2_reduzido, 2),
        "arvores_equivalentes": round(arvores_equivalentes, 2),
        "km_evitados": round(km_evitados, 2),
        "economia_acumulada": economia_acumulada,
        "dados_sistema": resultado
    })

@app.route('/')
def index():
    return send_from_directory('static', 'UPXSolaris.html')

@app.route('/<path:nome_arquivo>')
def arquivos_estaticos(nome_arquivo):
    return send_from_directory('static', nome_arquivo)
