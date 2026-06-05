# 📋 Sistema de Notificaciones por Mora

**Herramienta automatizada para notificar deudores con cuotas atrasadas**

## ✨ Características Principales

- 📧 **Envío automatizado de correos** a deudores y fiadores
- 📄 **Generación de PDFs personalizados** con información de cada deudor
- ⚡ **Procesamiento paralelo** para máxima velocidad
- 📊 **Reportes detallados de auditoría** con información completa
- ⚠️ **Auditoría de errores** para identificar problemas rápidamente
- 🎛️ **Interfaz gráfica fácil de usar** sin necesidad de conocimientos técnicos
- 🛑 **Cancelación en cualquier momento** sin perder los resultados parciales

---

## 🚀 Inicio Rápido

### Requisitos Previos
- Windows 7 o superior
- Microsoft Outlook configurado
- Archivo Excel con información de deudores

### Pasos Rápidos

1. **Ejecuta la aplicación**
   ```
   SistemaNotificacionesMora.exe
   ```

2. **Selecciona tu archivo Excel**
   - Haz clic en "Seleccionar archivo..."
   - Elige tu archivo con la información de deudores

3. **Elige cuenta de Outlook**
   - Selecciona la cuenta desde la que enviarás los correos

4. **Haz clic en "Ejecutar"**
   - ¡La aplicación se encargará del resto!

---

## 📖 Documentación

- 📘 **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** - Inicio en 3 pasos
- 📕 **[MANUAL_DE_USUARIO.md](MANUAL_DE_USUARIO.md)** - Documentación completa y detallada

---

## 📋 Formato del Archivo Excel Requerido

Tu archivo Excel debe tener estas columnas:

| Columna | Obligatorio | Descripción |
|---------|------------|------------|
| **nombre** | ✅ Sí | Nombre del deudor |
| **documento** | ✅ Sí | DNI/Cédula |
| **direccion** | ✅ Sí | Domicilio |
| **estado** | ✅ Sí | Estado civil |
| **cuotas_atrasadas** | ✅ Sí | Cantidad de cuotas adeudadas |
| **total** | ✅ Sí | Monto total adeudado |
| **correo_deudor** | ⚠️ Recomendado | Email del deudor |
| **nombre_fiador** | ⚠️ Recomendado | Nombre del fiador |
| **correo_fiador** | ⚠️ Recomendado | Email del fiador |

### Ejemplo:
```
| nombre      | documento | direccion    | estado  | cuotas_atrasadas | total    | correo_deudor   | nombre_fiador | correo_fiador   |
|-------------|-----------|--------------|---------|-----------------|----------|-----------------|---------------|-----------------|
| Juan Pérez  | 12345678  | Calle 123    | Casado  | 3              | 15000.50 | juan@email.com  | María López   | maria@email.com |
| Ana García  | 87654321  | Avenida 456  | Soltera | 2              | 8500.00  | ana@email.com   | Carlos Ruiz   | carlos@email.com|
```

---

## 📁 Estructura de Carpetas

```
sistema-notificaciones-mora/
├── main.py                          # Interfaz principal (GUI)
├── Cargador.py                      # Carga datos del Excel
├── Converter.py                     # Genera PDFs
├── EmailSender.py                   # Envía correos
├── Auditoria.py                     # Genera reportes
├── Monitoreo.py                     # Estadísticas
├── requirements.txt                 # Dependencias
├── MANUAL_DE_USUARIO.md             # Documentación completa
├── GUIA_RAPIDA.md                   # Guía de inicio rápido
├── README.md                        # Este archivo
│
├── Templates/                       # Plantillas de PDFs
│   ├── Plantilla-1-AlDia.html
│   ├── Plantilla-2-CUotas-Atrasadas.html
│   ├── Plantilla-3-Aviso-Cobro.html
│   ├── Plantilla-4-Cobro-Judicial.html
│   ├── Plantilla-5-Fiador.html
│   └── assets/                      # Estilos CSS
│
├── Resultados/                      # Archivos generados
│   ├── Auditoria_*.txt
│   ├── Auditoria_ERRORES_*.txt
│   ├── Monitoreo_*.txt
│   └── PDFs/                        # Documentos generados
│
└── Output/                          # Resultados adicionales
```

---

## 🎯 Flujo de Procesamiento

```
Excel → Cargador → Genera PDFs → Envía Correos → Auditoría
  ↓         ↓           ↓            ↓            ↓
 Datos   Validación  Converter   EmailSender   Reporte
```

### Fase 1: Generación de PDFs
- Se procesan en **paralelo** para máxima velocidad
- Se generan notificaciones para deudores y fiadores

### Fase 2: Envío de Correos
- Se envían en **paralelo** desde Outlook
- Se registra si se envió correctamente o hubo error

### Fase 3: Generación de Reportes
- **Auditoría completa**: Todos los registros procesados
- **Auditoría de errores**: Solo los que tuvieron problemas
- **Monitoreo**: Estadísticas generales

---

## 📊 Archivos Generados

Todos los archivos se guardan en la carpeta `Resultados/`:

### 1. Auditoría Completa (`Auditoria_*.txt`)
Información detallada de TODOS los registros procesados con estado de PDF y correo.

### 2. Auditoría de Errores (`Auditoria_ERRORES_*.txt`)
Solo los registros con problemas:
- Falta correo del deudor
- Falta información de fiador
- PDF no se generó
- Correo no se envió
- Errores detectados

### 3. PDFs Generados (`PDFs/`)
- `NOTIFICACION_*.pdf` - Notificaciones para deudores
- `FIADOR_*.pdf` - Notificaciones para fiadores

### 4. Monitoreo (`Monitoreo_*.txt`)
Estadísticas del proceso:
- Total de registros
- Éxitos y errores
- Tiempo de ejecución
- PDFs generados
- Correos enviados

---

## ⚙️ Características Técnicas

- **Lenguaje**: Python 3.8+
- **Interfaz**: Tkinter (GUI)
- **Generación de PDFs**: Playwright
- **Correo**: Win32COM (Outlook)
- **Lectura Excel**: OpenPyXL
- **Plantillas**: Jinja2
- **Procesamiento**: ThreadPoolExecutor (paralelo)

---

## ❓ Preguntas Frecuentes

### ¿Necesito conocimientos técnicos?
**No.** La aplicación tiene una interfaz gráfica intuitiva. Solo necesitas tu archivo Excel y Outlook configurado.

### ¿Es seguro? ¿Se guardan las contraseñas?
**Sí, es seguro.** La aplicación usa Outlook que ya está configurado en tu equipo. No almacena contraseñas.

### ¿Puedo personalizar los PDFs?
**Sí.** Las plantillas HTML están en la carpeta `Templates/`. Puedes editarlas con cualquier editor de texto.

### ¿Qué pasa si se corta la conexión?
El proceso se detendrá de forma segura. Puedes reintentar sin perder los resultados parciales (revisar auditoría).

### ¿Cuánto tarda?
- 50 registros: ~2-3 minutos
- 100 registros: ~4-5 minutos
- 500 registros: ~15-20 minutos

(Varía según la velocidad de tu conexión y equipo)

---

## 🔧 Solución de Problemas

### Outlook no aparece
1. Abre Microsoft Outlook
2. Espera a que cargue completamente
3. Cierra y abre nuevamente la aplicación

### El archivo Excel no se carga
1. Verifica que sea .xlsx o .xls
2. Abre en Excel y guarda nuevamente
3. Comprueba que tenga todas las columnas requeridas

### Los correos no se envían
1. Verifica que Outlook esté abierto
2. Comprueba que el archivo tenga correos
3. Revisa la Auditoría de Errores para detalles

---

## 📞 Soporte

Para más información:
1. Lee la **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** para inicio rápido
2. Consulta **[MANUAL_DE_USUARIO.md](MANUAL_DE_USUARIO.md)** para documentación completa
3. Revisa los archivos de auditoría para diagnosticar problemas
4. Contacta al administrador del sistema

---

## 📝 Licencia y Disclaimer

Este software se proporciona "TAL CUAL" sin garantía. Úsalo bajo tu responsabilidad. Siempre mantén respaldos de tus datos.

---

## 📋 Historial de Cambios

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2024-06-05 | Versión inicial |
| 1.1 | 2024-06-05 | Se agregó auditoría de errores |

---

**Versión Actual:** 1.1  
**Última Actualización:** 5 de junio de 2024

---

🎉 **¡Gracias por usar Sistema de Notificaciones por Mora!**
