# Manual de Usuario - Sistema de Notificaciones por Mora

## Contenido
1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación y Configuración Inicial](#instalación-y-configuración-inicial)
4. [Estructura del Archivo Excel](#estructura-del-archivo-excel)
5. [Cómo Usar la Aplicación](#cómo-usar-la-aplicación)
6. [Entendiendo la Interfaz](#entendiendo-la-interfaz)
7. [Archivos de Salida](#archivos-de-salida)
8. [Preguntas Frecuentes](#preguntas-frecuentes)
9. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

**Sistema de Notificaciones por Mora** es una herramienta automatizada que:
- Procesa información de deudores con cuotas atrasadas
- Genera notificaciones personalizadas en PDF
- Envía correos automáticamente a deudores y fiadores
- Genera reportes de auditoría detallados
- Procesa múltiples registros en paralelo para máxima velocidad

---

## Requisitos del Sistema

### Software Necesario
- **Windows 7 o superior** (Sistema operativo)
- **Microsoft Outlook** instalado y configurado
- **Espacio en disco**: Mínimo 500 MB disponibles

### Permisos Necesarios
- Acceso a Outlook (classic) y sus cuentas
- Permiso de lectura/escritura en la carpeta de la aplicación
- Acceso a internet (para envío de correos)

---

## Instalación y Configuración Inicial

### Opción 1: Usar la Versión Ejecutable (Recomendado)

1. **Descargar la aplicación**
   - Obtén el archivo `SistemaNotificacionesMora.exe`

2. **Ejecutar la aplicación**
   - Haz doble clic en `SistemaNotificacionesMora.exe`
   - Se abrirá automáticamente la interfaz

3. **Verificar Outlook**
   - Asegúrate de tener Outlook configurado con al menos una cuenta de correo
   - La aplicación se conectará automáticamente a Outlook

---

## Estructura del Archivo Excel

### Requisitos Obligatorios

Tu archivo Excel debe contener una hoja con las siguientes **columnas exactas**:
cedula | carne | nombre | email | celular | telefono | estado | cuotas atrasado | f.inicio pago | FECHA PROX.PAGO | PRINCIPAL |	INTE. ACUMULADO	| INT.SALDOS	| TOTAL |	FIADOR 1 |	CORREO FIADOR 1 |	CELULAR |	TELÉFONO | 	FIADOR 2 |	CORREO FIADOR 2 |	CELULAR	|TELÉFONO 


*: Si faltan datos, se registrarán en el informe de errores pero no se generará el correo

### Ejemplo de Archivo Válido

```
CEDULA	CARNE	NOMBRE	EMAIL	CELULAR	TELEFONO CASA	ESTADO	CUOTAS ATRASO	F.INICIO PAGO	FECHA PROX.PAGO	PRINCIPAL	INTE. ACUMULADO	INT.SALDOS	TOTAL	FIADOR 1	CORREO FIADOR 1	CELULAR	TELÉFONO 	FIADOR 2	CORREO FIADOR 2	CELULAR	TELÉFONO 
701690425	200546450	ACUÑA BOGANTES ANIBAL	danymendezromero@gmail.com	83847344	0	NORMAL	3	1/10/2025	1/4/2026	1,622,777.05	37070,7	17,747.80	110,400.00	SANCHEZ SOLIS ELIAS ANTONIO	danymendezromero@gmail.com	0	0	GRANADOS ARAYA RODRIGO	0	0	0
604600002	2019219564	AGUILAR JIMENEZ KEVIN GERARDO	danymendezromero@gmail.com	83993776	0	NORMAL	5	1/6/2024	17/4/2026	74,969.80	0	281.15	37,300.00	AGUILAR LIZANO OLMAN GERARDO	danymendezromero@gmail.com	83468334	0	No aplica	No aplica	No aplica	No aplica
117760929	2018010491	ALFARO HARO LUIS ENRIQUE	danymendezromero@gmail.com	84120667	0	NORMAL	3	1/12/2021	1/3/2026	453,378.90	0	2,229.85	69,900.00	HARO ASMAT ROSA AMELIA	danymendezromero@gmail.com	83140199	0	No aplica	No aplica	No aplica	No aplica

```

### Notas Importantes

- ✅ Los nombres de columna deben ser **exactos** (mayúsculas/minúsculas no importa)
- ✅ No puede haber columnas en blanco intercaladas
- ✅ El archivo debe estar en formato **XLSX** o **XLS**
- ⚠️ Si falta correo o fiador, se registra pero el correo no se envía

---

## Cómo Usar la Aplicación

### Paso 1: Seleccionar Archivo Excel

1. Abre la aplicación
2. Haz clic en el botón **"Seleccionar archivo..."**
3. Navega hasta tu archivo Excel
4. Selecciona el archivo y haz clic en **"Abrir"**
5. Verás la ruta del archivo en el campo de texto

### Paso 2: Seleccionar Cuenta de Outlook

1. En la sección **"Cuenta de correo"**, abre el menú desplegable
2. Selecciona la cuenta de Outlook desde la cual enviarás los correos
3. Si no hay opciones disponibles:
   - Verifica que Outlook esté abierto y configurado
   - Reinicia la aplicación
   - Consulta **Solución de Problemas**

### Paso 3: Ejecutar el Proceso

1. Una vez seleccionados archivo y cuenta, haz clic en **"Ejecutar"**
2. Verás el progreso en el área de registro (log)
3. El proceso se divide en 3 fases:
   - **Fase 1**: Generación de PDFs (en paralelo)
   - **Fase 2**: Envío de correos (en paralelo)
   - **Fase 3**: Generación de reportes

### Paso 4: Revisar Resultados

El proceso generará:
- Archivos PDF de notificaciones
- Correos enviados automáticamente
- Auditoría completa
- Auditoría de errores (si hay problemas)
- Monitoreo del proceso

---

## Entendiendo la Interfaz

### Área Principal

```
┌─────────────────────────────────────────────┐
│  SISTEMA DE NOTIFICACIONES POR MORA        │
└─────────────────────────────────────────────┘

┌─ SELECCIONAR ARCHIVO ─────────────────────┐
│ Ruta: [Campo de texto]  [Seleccionar...]  │
└───────────────────────────────────────────┘

┌─ CUENTA DE CORREO ────────────────────────┐
│ Selecciona: [Dropdown desplegable]         │
└───────────────────────────────────────────┘

┌─ CONTROLES ───────────────────────────────┐
│ [Ejecutar]  [Cancelar]  [Limpiar Log]     │
└───────────────────────────────────────────┘

┌─ REGISTRO DE EJECUCIÓN (LOG) ─────────────┐
│ 📂 Cargando: C:\archivo.xlsx              │
│ ⏳ Fase 1: Generando PDFs en paralelo...  │
│ ✅ Juan Pérez - Procesado correctamente   │
│ ... (más registros)                       │
└───────────────────────────────────────────┘
```

### Símbolos en el Log

| Símbolo | Significado |
|---------|------------|
| ✅ | Éxito, completado correctamente |
| ❌ | Error, algo no funcionó |
| ⚠️ | Advertencia, requiere atención |
| ⏳ | Proceso en curso |
| 📂 | Información de archivo |
| 📧 | Operación de correo |
| 🛑 | Cancelación |

### Botones

- **Ejecutar**: Inicia el proceso de notificaciones
- **Cancelar**: Detiene el proceso en curso (se completarán las tareas en proceso)
- **Limpiar Log**: Limpia el área de registro de texto

---

## Archivos de Salida

### Ubicación

Todos los archivos generados se guardan en la carpeta **`Resultados/`** dentro de la carpeta de la aplicación.

### Tipos de Archivos Generados

#### 1. **PDFs de Notificación** (Carpeta: `PDFs/`)
```
PDFs/
├── NOTIFICACION_Juan_Perez_2024-06-05.pdf
├── NOTIFICACION_Ana_Garcia_2024-06-05.pdf
├── FIADOR_Maria_Gonzalez_2024-06-05.pdf
└── ...
```

#### 2. **Auditoría Completa** (`Auditoria_YYYY-MM-DD_HH-MM-SS.txt`)
Contiene información detallada de TODOS los registros procesados:
```
================================================================================
AUDITORÍA PROCESO CUOTAS ATRASADAS
Fecha generación: 2024-06-05 14:30:45
================================================================================

Persona: Juan Pérez
Estado: Casado
Cuotas atrasadas: 3
Total pendiente: 15000.50
Fecha procesamiento: 2024-06-05
PDF principal generado: Se generó el documento
Correo deudor enviado: Se envió el correo
Correo deudor: juan@email.com
Mensaje: Procesado correctamente
────────────────────────────────────────────────────────────────────────────────
```

#### 3. **Auditoría de Errores** (`Auditoria_ERRORES_YYYY-MM-DD_HH-MM-SS.txt`)
Contiene SOLO los registros con problemas:
```
================================================================================
AUDITORÍA ERRORES - CUOTAS ATRASADAS
Fecha generación: 2024-06-05 14:35:20
Total registros con error: 2
================================================================================

Persona: Carlos López
Estado: Soltero
Cuotas atrasadas: 1
Total pendiente: 5000.00
Fecha procesamiento: 2024-06-05
PDF generado: ❌ No
Correo deudor disponible: ❌ No
Error: No hay correo de deudor para enviar notificación
────────────────────────────────────────────────────────────────────────────────
```

**Los errores pueden deberse a:**
- ❌ Falta de correo del deudor
- ❌ Falta de información de fiador
- ❌ Fallo al generar el PDF
- ❌ Error en el envío del correo
- ❌ Problema de conexión con Outlook


## Preguntas Frecuentes

### ¿Puedo modificar las plantillas de PDF?

**Sí.** Las plantillas se encuentran en la carpeta `Templates/`:
- `Plantilla-1-AlDia.html` - Para deudores sin atraso
- `Plantilla-2-CUotas-Atrasadas.html` - Para deudores con cuotas atrasadas
- `Plantilla-3-Aviso-Cobro.html` - Aviso de cobro
- `Plantilla-4-Cobro-Judicial.html` - Aviso de cobro judicial
- `Plantilla-5-Fiador.html` - Notificación para fiadores

Puedes editar estas plantillas con HTML/CSS. Los cambios se aplicarán automáticamente en la próxima ejecución.

### ¿Qué pasa si cancelo el proceso?

- Las tareas que estén en proceso se completarán
- Las nuevas tareas no iniciarán
- Los resultados parciales se guardarán
- Se generarán reportes con el estado actual

### ¿Puedo ejecutar la aplicación en segundo plano?

**Recomendación**: No desactives la ventana mientras se ejecuta. La aplicación procesa en paralelo, así que es seguro trabajar con otras cosas mientras está en ejecución.

### ¿Dónde se guardan los archivos?

En la carpeta `Resultados/` dentro de la carpeta de la aplicación. Puedes hacer clic derecho en la ventana de resultados y ver los archivos.

### ¿Puedo usar otra cuenta de correo?

**No.** La aplicación solo funciona con **Microsoft Outlook (Classic)** configurado en tu equipo. Las cuentas disponibles son las que tienes configuradas en Outlook.

### ¿Cuánto tiempo tarda el proceso?

Depende de la cantidad de registros:
- 50 registros: ~2-3 minutos
- 100 registros: ~4-5 minutos
- 500 registros: ~10-15 minutos
- 1000 registros: ~15-20 minutos

El procesamiento es paralelo, así que es muy eficiente.

---

## Solución de Problemas

### Problema: "No se encuentran cuentas de Outlook"

**Soluciones:**
1. ✅ Abre Microsoft Outlook en tu equipo
2. ✅ Espera a que Outlook cargue completamente
3. ✅ Cierra la aplicación y vuelve a abrirla
4. ✅ Verifica que tengas al menos una cuenta configurada en Outlook

### Problema: "El archivo Excel no se carga"

**Causas posibles:**
- El archivo no está en formato Excel (.xlsx o .xls)
- El archivo está corrupto o no se puede acceder
- Falta alguna columna obligatoria

**Solución:**
1. Verifica que el archivo sea .xlsx o .xls
2. Abre el archivo en Excel y guárdalo nuevamente
3. Verifica que tenga todas las columnas requeridas

### Problema: "Los correos no se envían"

**Causas posibles:**
- Outlook no está abierto
- No hay conexión a internet
- La cuenta de Outlook no tiene permisos para enviar correos
- Falta correo de deudor o fiador

**Solución:**
1. ✅ Abre Outlook
2. ✅ Verifica tu conexión a internet
3. ✅ Comprueba que el archivo Excel tenga correos válidos
4. ✅ Revisa la Auditoría de Errores para más detalles

### Problema: "Se demora mucho en procesar"

**Esto es normal** si tienes muchos registros. La aplicación procesa en paralelo:
- Los PDFs se generan simultáneamente
- Los correos se envían de forma simultánea
- Esto es más rápido que hacerlo secuencialmente

### Problema: "Los PDFs se ven mal o con formato incorrecto"

**Solución:**
1. Abre la carpeta `Templates/`
2. Edita la plantilla correspondiente
3. Guarda los cambios
4. Vuelve a ejecutar el proceso

### Problema: "No encuentro los archivos generados"

**Ubicación:** Carpeta `Resultados/` dentro de la carpeta de la aplicación

**Cómo acceder:**
- Windows: Abre el Explorador de Archivos y navega a la carpeta de instalación
- O: Haz clic en el ícono de carpeta en la ventana de resultados (si está disponible)

### Problema: "Error al generar el PDF"

**Causas:**
- Problema con las plantillas HTML
- Falta de permisos de escritura en la carpeta Resultados
- Problema con Playwright (motor de conversión)

**Solución:**
1. Verifica que la carpeta Resultados exista y sea accesible
2. Revisa la Auditoría de Errores para más detalles
3. Reinicia la aplicación

---

## Consejos y Mejores Prácticas

### ✅ Antes de Ejecutar

- [ ] Verifica que Outlook esté abierto y configurado
- [ ] Revisa que el archivo Excel sea correcto y tenga todas las columnas
- [ ] Asegúrate de tener espacio en disco
- [ ] Comprueba tu conexión a internet

### ✅ Durante la Ejecución

- [ ] No desconectes la red
- [ ] No cierres Outlook
- [ ] Puedes trabajar con otras aplicaciones (el proceso es paralelo)
- [ ] Si necesitas cancelar, usa el botón "Cancelar"

### ✅ Después de Ejecutar

- [ ] Revisa los reportes de auditoría
- [ ] Verifica que se generaron los PDFs
- [ ] Comprueba que los correos se enviaron
- [ ] Guarda los reportes como respaldo

---

## Contacto y Soporte

Si tienes problemas o preguntas:
1. Revisa este manual nuevamente
2. Consulta la sección **Solución de Problemas**
3. Revisa los archivos de auditoría para obtener más detalles

---

## Historial de Cambios

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-06-05 | Versión inicial |
| 1.1 | 2026-06-05 | Se agregó auditoría de errores |

---

**Última actualización:** 5 de junio de 2026

**Documento:** Manual de Usuario - Sistema de Notificaciones por Mora

---

*Este manual está sujeto a cambios según las actualizaciones de la aplicación.*
