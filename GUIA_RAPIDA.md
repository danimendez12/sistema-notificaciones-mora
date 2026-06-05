# Guía Rápida de Inicio

## ⚠️ Requisitos Importantes

✅ **Tener Outlook (classic) abierto y configurado**
✅ **Conexión a internet**
✅ **Archivo Excel con las columnas exactas**
✅ **Permisos de escritura en la carpeta de la app**

---


## En 3 Pasos

### 1️⃣ Prepara tu archivo Excel

Asegúrate de que tu archivo Excel tenga estas columnas:
```
cedula | carne | nombre | email | celular | telefono | estado | cuotas atrasado | f.inicio pago | FECHA PROX.PAGO | PRINCIPAL |	INTE. ACUMULADO	| INT.SALDOS	| TOTAL |	FIADOR 1 |	CORREO FIADOR 1 |	CELULAR |	TELÉFONO | 	FIADOR 2 |	CORREO FIADOR 2 |	CELULAR	|TELÉFONO 

```

### 2️⃣ Abre la aplicación

- Ejecuta `SistemaNotificacionesMora.exe`
- Haz clic en **"Seleccionar archivo..."** y elige tu Excel
- Selecciona la cuenta de correo rprestamos@itcr.ac.cr en el dropdown

### 3️⃣ Ejecuta el proceso

- Haz clic en **"Ejecutar"**
- ¡Espera a que termine!
- Los archivos se guardan en `Resultados/`

---

## Archivos Generados

```
Resultados/
├── Auditoria_FECHA_HORA.txt           ← Reporte completo
├── Auditoria_ERRORES_FECHA_HORA.txt   ← Solo errores
└── PDFs/
    ├── NOTIFICACION_Juan_Perez.pdf
    ├── NOTIFICACION_Ana_Garcia.pdf
    └── ...
```

---


## Problemas Comunes

| Problema | Solución |
|----------|----------|
| No aparecen cuentas de Outlook | Abre Outlook, espera a que cargue, reinicia la app |
| El archivo no se carga | Verifica que sea .xlsx o .xls |
| Los correos no se envían | Verifica que haya correos en el Excel y que Outlook esté abierto |
| No encuentro los PDFs | Están en la carpeta `Resultados/` |

---

## 📖 Documentación Completa

Para más detalles, consulta `MANUAL_DE_USUARIO.pdf`

---

**¡Listo para usar!** 
