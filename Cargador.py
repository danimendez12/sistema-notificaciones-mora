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

def parse_decimal(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if text == "":
        return None

    text = text.replace(" ", "")
    text = text.replace("₡", "")
    text = text.replace("$", "")

    has_comma = "," in text
    has_dot = "." in text

    if has_comma and has_dot:
        last_comma = text.rfind(",")
        last_dot = text.rfind(".")
        if last_dot > last_comma:
            normalized = text.replace(",", "")
        else:
            normalized = text.replace(".", "").replace(",", ".")
    elif has_comma:
        parts = text.split(",")
        if len(parts[-1]) == 2:
            normalized = text.replace(",", ".")
        else:
            normalized = text.replace(",", "")
    elif has_dot:
        parts = text.split(".")
        if len(parts[-1]) == 2:
            normalized = text
        else:
            normalized = text.replace(".", "")
    else:
        normalized = text

    try:
        return float(normalized)
    except ValueError:
        return None
def cargar_registros(
    archivo_excel: str,
    auditoria: dict
) -> tuple[list[Model.Persona], dict[str,Any]]:

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

                estado=clean_value(fila[6]),

                cuotas_atrasadas=int(
                    clean_value(fila[7]) or 0
                ),
                total=(
                    parse_decimal(clean_value(fila[13]))
                ),

                correo_fiador=clean_value(fila[15]),

                fiador=clean_value(fila[14])
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

    return list(registros), auditoria

