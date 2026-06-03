# cargador.py
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass, field
import os
from time import perf_counter
from typing import Any
import Model

import openpyxl


def clean_value(value):

    if value is None:
        return None

    if isinstance(value, str):

        value = value.strip()

        if value == "":
            return None

    return value

def cargar_registros(
    archivo_excel: str,
<<<<<<< HEAD
    auditoria: dict,
    monitoreo: dict,
) -> tuple[list[Model.Persona], dict[str,Any], dict[str,Any]]:
=======
    auditoria: dict
) -> tuple[list[Model.Persona], dict[str,Any]]:
>>>>>>> 0d3387d1f5c69ec7c8feb435764e9bf2f92eec91

    inicio = perf_counter()
    nombre = os.path.splitext(
        os.path.basename(archivo_excel)
    )[0]

    wb = openpyxl.load_workbook(archivo_excel)


    hoja = wb.active
    registros: list[Model.Persona] = []
    filas_validas = 0
    filas_invalidas = 0
    for index, fila in enumerate(hoja.iter_rows(min_row=2, values_only=True), start=2):
        try:

            persona = Model.Persona(

                nombre=clean_value(fila[2]),

                email=clean_value(fila[3]),

                estado=clean_value(fila[4]),

                cuotas_atrasadas=int(
                    clean_value(fila[5]) or 0
                ),
                total=(
                    float(
                        str(clean_value(fila[6]))
                        .replace(".", "")
                        .replace(",", ".")
                    )
                    if clean_value(fila[6])
                    else None
                ),

                correo_fiador=clean_value(fila[8]),

                fiador=clean_value(fila[7])
            )

            registros.append(persona)
            filas_validas += 1
        except Exception as exc:
            nombre_error = clean_value(fila[2]) or f"Fila {index}"
            auditoria[nombre_error] = {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": None,
                "cuotas_atrasadas": 0,
                "total": None,
                "notificacion_generada": False,
                "notificacion_fiador_generada": False,
                "correo_fiador": False,
                "correo_deudor_enviado": False,
                "correo_fiador_enviado": False,
                "error_envio": "",
                "mensaje": f"Error al procesar fila {index}: {exc}",
            }
            filas_invalidas += 1
<<<<<<< HEAD
    monitoreo["cargador"] = {
        "tiempo_segundos": round(perf_counter() - inicio, 4),
        "registros_leidos": filas_validas + filas_invalidas,
        "registros_validos": filas_validas,
        "registros_invalidos": filas_invalidas,
    }
=======
    
>>>>>>> 0d3387d1f5c69ec7c8feb435764e9bf2f92eec91

    return list(registros), auditoria

