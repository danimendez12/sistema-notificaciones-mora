# cargador.py
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass, field
import os
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
    auditoria: dict,
) -> tuple[list[Model.Persona], dict[str,Any]]:


    nombre = os.path.splitext(
        os.path.basename(archivo_excel)
    )[0]

    wb = openpyxl.load_workbook(archivo_excel)


    hoja = wb.active
    registros: list[Model.Persona] = []
    for index, fila in enumerate(hoja.iter_rows(min_row=2, values_only=True), start=2):
        try:

            persona = Model.Persona(

                nombre=clean_value(fila[2]),

                email=clean_value(fila[3]),

                estado=clean_value(fila[6]),

                cuotas_atrasadas=int(
                    clean_value(fila[7]) or 0
                ),

                fecha_proximo_pago=str(
                    clean_value(fila[9])
                ) if clean_value(fila[9]) else None,

                total=(
                    str(float(
                        str(clean_value(fila[13]))
                        .replace(".", "")
                        .replace(",", ".")
                    ))
                    if clean_value(fila[13])
                    else None
                ),

                correo_fiador=clean_value(fila[15]),

                fiador=clean_value(fila[14])
            )

            registros.append(persona)
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

    return list(registros), auditoria

