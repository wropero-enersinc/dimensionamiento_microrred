import pandas as pd

def resultado(load, generacion_pv, model,generacion_diesel):
    # Realizado para unir lso datos de recurso disponible y carga (load)
    carga = pd.DataFrame([load]).T
    carga.columns = ['load']

    rescurso_pv = pd.DataFrame([generacion_pv]).T
    rescurso_pv.columns = ['recurso_pv_dis']

    recurso_diesel = pd.DataFrame([generacion_diesel]).T
    recurso_diesel.columns = ['recurso_diesel_dis']

    recurso_carga = pd.concat([carga, rescurso_pv, recurso_diesel],axis=1)

    demanda_total = sum(load.values())

    def _resultados(model, demanda_total, recurso_carga ):
        """
        Esta función obtiene todos los valores
        de la optimización excepto el valor de
        la función
        -------------------
        entrada: Modelo
        salidas: res_1 = Información por hora devuelta
                        por el optimizador para
                        cada variable.
                res_2 = Información de resultados de
                        parámetros de control (LPSP,
                        ciclos de carga y descarga).
        """

        # Listas para guardar los valores
        pv_result = []
        dg_result = []
        Ebat_c_result = []
        Ebat_d_result = []
        p_ens_result = []
        LPSP_result = []
        SOC_result = []
        n_cc_result = []
        n_dc_result = []
        B_diesel_result = []
        B_bat_d_result = []
        B_bat_c_result = []
        
        EMAX_d_result = []
        EMAX_c_result = []
        Epv_dis_result= []

        # Ciclo que obtiene el valor de cada resultado enlas iteraciones del modelo
        for v in model.var_reales.items():
            uni = v[0][0]
            if uni == 'Pv':
                pv_result.append(v[1].value)
            if uni == 'Dg':
                dg_result.append(v[1].value)
            if uni == 'Ebat_c':
                Ebat_c_result.append(v[1].value)
            if uni == 'Ebat_d':
                Ebat_d_result.append(v[1].value)
            elif uni == 'P_ens':
                p_ens_result.append(v[1].value)
            elif uni == 'n_cc':
                n_cc_result.append(v[1].value)
            elif uni == 'n_dc':
                n_dc_result.append(v[1].value)
            #elif uni == 'EMAX_c':
            #    EMAX_c_result.append(v[1].value)
            #elif uni == 'EMAX_d':
            #    EMAX_d_result.append(v[1].value)
            #elif uni == 'Epv_dis':
            #    Epv_dis_result.append(v[1].value)
            else:
                pass

        for b in model.binarias.items():
            uni = b[0][0]
            if uni == 'B_diesel':
                B_diesel_result.append(b[1].value)
            if uni == 'B_bat_d':
                B_bat_d_result.append(b[1].value)
            if uni == 'B_bat_c':
                B_bat_c_result.append(b[1].value)
            else:
                pass

        for s in model.soc_t.items():
            SOC_result.append(s[1].value)

        resultados_energia = {
            'energia_PV': pv_result,
            'energia_Dg': dg_result,
            'bin_diesel': B_diesel_result,
            'energia_carga_bateria': Ebat_c_result,
            'bin_bat_carga': B_bat_c_result,
            'energia_descarga_bateria': Ebat_d_result,
            'bin_bat_descarga': B_bat_d_result,
            'energia_ENS': p_ens_result,
            'SOC(t)_bateria': SOC_result
            #,
            #'EMAX_c': EMAX_c_result,
            #'EMAX_d': EMAX_d_result,
            #'Epv_disponible': Epv_dis_result
        }

        resultados_control = {
            'ENS': round(sum(p_ens_result), 4),
            'LPSP(%)': round(sum(p_ens_result) / demanda_total, 4) * 100,
            'ciclos_carga': n_cc_result[0],
            'ciclos_descarga': n_dc_result[0]
        }
        res_1 = pd.DataFrame(resultados_energia)
        res_1['suma_pv_dg_bat_descarga'] = res_1['energia_PV'] + res_1[
            'energia_Dg'] + res_1['energia_descarga_bateria']
        res_1 = pd.concat([res_1, recurso_carga],axis=1)
        res_2 = pd.DataFrame([resultados_control])

        return res_1, res_2

    parametros_control = _resultados(model, demanda_total, recurso_carga)[1]
    tabla_resultados = _resultados(model, demanda_total, recurso_carga)[0]

    return parametros_control, tabla_resultados