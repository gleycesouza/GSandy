import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pickle
import pickle
import plotly.express as px
import pandas as pd

def load_models_and_predict(test_type):
    # Define os caminhos baseados na seleção
    if test_type == "DSS":
        model_paths = {
            'rf': r'weights/dss/rf_model_dss.pkl',
            'svr': r'weights/dss/svr_model_dss.pkl',
            'nn': r'weights/dss/nn_model_dss.pkl',
            'scaler': r'weights/dss/scaler.pkl',
        }
    else:  # Cisalhamento Direto
        model_paths = {
            'rf': r'weights/ds/rf_model_ds.pkl',
            'svr': r'weights/ds/svr_model_ds.pkl',
            'nn': r'weights/ds/nn_model_ds.pkl',
            'scaler': r'weights/ds/scaler.pkl',
        }

    # Carregar os modelos e o escalador baseados nos caminhos
    rf_model = pickle.load(open(model_paths['rf'], 'rb'))
    svr_model = pickle.load(open(model_paths['svr'], 'rb'))
    nn_model = pickle.load(open(model_paths['nn'], 'rb'))
    scaler = pickle.load(open(model_paths['scaler'], 'rb'))
    
    # Retornar os modelos e o escalador em um dicionário
    return {'rf_model': rf_model, 'svr_model': svr_model, 'nn_model': nn_model, 'scaler': scaler}

# Função modificada para carregar o modelo a partir de um arquivo pickle
def get_predictions(test_values, model, scaler, gs, e_cisa, cr, tensao_v):
    X_previsao = np.array([[gs, e_cisa, cr, tensao_v, v] for v in test_values])
    X_previsao_scaled = scaler.transform(X_previsao)
    y_pred_previsao = model.predict(X_previsao_scaled)
    y_pred_previsao[0] = 0  # Condição de contorno
    return y_pred_previsao


def plot_predictions(test_values, models, gs, e_cisa, cr, tensao_v):
    rf_model = models['rf_model']
    svr_model = models['svr_model']
    nn_model = models['nn_model']
    scaler = models['scaler']

    # Obter previsões para cada modelo usando a função get_predictions modificada
    rf_pred = get_predictions(test_values, rf_model, scaler, gs, e_cisa, cr, tensao_v)
    svr_pred = get_predictions(test_values, svr_model, scaler, gs, e_cisa, cr, tensao_v)
    nn_pred = get_predictions(test_values, nn_model, scaler, gs, e_cisa, cr, tensao_v)
    
    return rf_pred, svr_pred, nn_pred