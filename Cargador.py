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
    for fila in hoja.iter_rows(min_row=2, values_only=True):
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

                fiador=clean_value( fila[14] )
            )

            registros.append(persona)
        except Exception as exc:          
            auditoria[nombre] = f"error al procesar fila {fila}: {exc}"

    return list(registros), auditoria

