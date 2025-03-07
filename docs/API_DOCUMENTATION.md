# Code Review Assistant API Documentation

## Descripción general

El servicio de Code Review Assistant proporciona APIs para analizar código fuente y obtener recomendaciones, problemas y métricas de calidad. La API soporta tanto análisis síncronos como asíncronos.

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Análisis Síncrono

**Endpoint:** `POST /analyze`

**Descripción:** Analiza código de forma síncrona y devuelve los resultados inmediatamente. Recomendado solo para archivos pequeños o cuando se necesita una respuesta inmediata.

**Request:**

```json
{
  "project_id": "mi-proyecto",
  "code_data": {
    "code": "def suma(a, b):\n    return a + b",
    "filename": "utils.py",
    "file_extension": "py"
  }
}
```

O usando el formato DFF (Diff Format):

```json
{
  "project_id": "mi-proyecto",
  "dff_data": {
    "summary": {
      "totalFiles": 1,
      "added": 0,
      "modified": 1,
      "deleted": 0
    },
    "files": [
      {
        "fileName": "utils.py",
        "status": "MODIFIED",
        "codeContext": {
          "before": [
            "def suma(a, b):",
            "    result = a + b",
            "    return result"
          ],
          "after": [
            "def suma(a, b):",
            "    return a + b"
          ]
        }
      }
    ]
  }
}
```

**Response (200 OK):**

```json
{
  "analysis_id": "f14800d1-40cf-48cf-a21a-7a188f976e84",
  "status": "completed",
  "result": {
    "format": "dff",
    "files_analyzed": 1,
    "average_score": 8.5,
    "total_issues": 0,
    "results": [
      {
        "score": 8.5,
        "issues": [],
        "details": {
          "code_analyzer": {
            "tool_name": "code_analyzer",
            "score": 9.2,
            "summary": "El código está bien estructurado y es fácil de entender.",
            "issues": []
          },
          "best_practices_checker": {
            "tool_name": "best_practices_checker",
            "score": 8.0,
            "issues": [],
            "summary": "Se encontraron 3 buenas prácticas y 0 problemas."
          }
        },
        "summary": "No se encontraron problemas",
        "filename": "utils.py",
        "status": "MODIFIED"
      }
    ],
    "summary": "Se analizó 1 archivo con una puntuación promedio de 8.5 y no se encontraron problemas."
  },
  "created_at": "2025-03-02T17:04:06.138180",
  "completed_at": "2025-03-02T17:04:08.621632",
  "project_id": "mi-proyecto"
}
```

### 2. Análisis Asíncrono

**Endpoint:** `POST /analyze/async`

**Descripción:** Inicia un análisis de código en segundo plano y devuelve inmediatamente un ID para consultar el estado posteriormente. Recomendado para archivos grandes o múltiples archivos.

**Request:** Igual que para el endpoint síncrono.

**Response (200 OK):**

```json
{
  "analysis_id": "fe1f13e0-c933-45f5-96e6-936799ec1e1e",
  "status": "pending",
  "message": "Análisis iniciado en segundo plano",
  "created_at": "2025-03-02T17:20:58.475894",
  "project_id": "mi-proyecto"
}
```

### 3. Consulta de Estado de Análisis

**Endpoint:** `GET /analysis/{analysis_id}`

**Descripción:** Obtiene el estado actual y los resultados (si están disponibles) de un análisis específico.

**Parámetros de ruta:**
- `analysis_id`: ID del análisis a consultar

**Response (200 OK) - Análisis en proceso:**

```json
{
  "analysis_id": "fe1f13e0-c933-45f5-96e6-936799ec1e1e",
  "status": "processing",
  "message": "El análisis está en progreso",
  "created_at": "2025-03-02T17:20:58.475894",
  "project_id": "mi-proyecto"
}
```

**Response (200 OK) - Análisis completado:**

```json
{
  "analysis_id": "fe1f13e0-c933-45f5-96e6-936799ec1e1e",
  "status": "completed",
  "result": {
    "format": "dff",
    "files_analyzed": 1,
    "average_score": 6.5,
    "total_issues": 1,
    "results": [
      {
        "score": 6.5,
        "issues": [
          {
            "type": "input_validation",
            "message": "El código no realiza una validación adecuada del parámetro 'data'",
            "line": 1,
            "severity": "medium",
            "suggestion": "Validar los datos de entrada para asegurar que solo contengan valores esperados",
            "cwe_id": "CWE-20"
          }
        ],
        "details": {
          "code_analyzer": {
            "tool_name": "code_analyzer",
            "score": 9.2,
            "summary": "El código está bien estructurado",
            "issues": []
          },
          "security_scanner": {
            "tool_name": "security_scanner",
            "score": 8.5,
            "summary": "El código tiene buenas prácticas de seguridad pero carece de validación de entrada",
            "issues": [
              {
                "type": "input_validation",
                "message": "El código no realiza una validación adecuada del parámetro 'data'",
                "line": 1,
                "severity": "medium",
                "suggestion": "Validar los datos de entrada",
                "cwe_id": "CWE-20"
              }
            ]
          }
        },
        "summary": "Se encontró 1 problema (0 críticos, 1 medio, 0 bajo)",
        "filename": "utils.py",
        "status": "MODIFIED"
      }
    ],
    "summary": "Se analizó 1 archivo con una puntuación promedio de 6.5 y se encontró 1 problema."
  },
  "created_at": "2025-03-02T17:20:58.475894",
  "completed_at": "2025-03-02T17:21:06.156536",
  "project_id": "mi-proyecto"
}
```

**Response (200 OK) - Error en el análisis:**

```json
{
  "analysis_id": "fe1f13e0-c933-45f5-96e6-936799ec1e1e",
  "status": "error",
  "message": "Error durante el análisis: El archivo contiene sintaxis inválida",
  "created_at": "2025-03-02T17:20:58.475894",
  "project_id": "mi-proyecto"
}
```

### 4. Listar Análisis

**Endpoint:** `GET /analyses`

**Descripción:** Obtiene una lista de análisis realizados, con opciones de filtrado.

**Parámetros de consulta:**
- `project_id` (opcional): Filtrar por ID de proyecto
- `status` (opcional): Filtrar por estado ("pending", "processing", "completed", "error")
- `limit` (opcional, default=10): Número máximo de resultados a devolver

**Response (200 OK):**

```json
[
  {
    "analysis_id": "fe1f13e0-c933-45f5-96e6-936799ec1e1e",
    "status": "completed",
    "created_at": "2025-03-02T17:20:58.475894",
    "completed_at": "2025-03-02T17:21:06.156536",
    "project_id": "mi-proyecto"
  },
  {
    "analysis_id": "c8cd56da-caab-47be-aa2e-8ff94ee46cee",
    "status": "pending",
    "message": "El análisis está en progreso",
    "created_at": "2025-03-02T17:30:00.000000",
    "project_id": "mi-proyecto"
  }
]
```

## Estructura de datos

### Modelos de entrada

#### CodeData

```json
{
  "code": "string",         // Código fuente a analizar
  "filename": "string",     // Nombre del archivo
  "file_extension": "string" // Extensión del archivo (opcional)
}
```

#### DFFData (Diff Format)

```json
{
  "summary": {
    "totalFiles": "integer",  // Número total de archivos
    "added": "integer",       // Archivos añadidos
    "modified": "integer",    // Archivos modificados
    "deleted": "integer"      // Archivos eliminados
  },
  "files": [
    {
      "fileName": "string",   // Nombre del archivo
      "status": "string",     // Estado: "ADDED", "MODIFIED", "DELETED"
      "codeContext": {
        "before": ["string"], // Líneas de código antes del cambio
        "after": ["string"]   // Líneas de código después del cambio
      }
    }
  ]
}
```

### Modelos de respuesta

#### AnalysisResponse

```json
{
  "analysis_id": "string",           // ID único del análisis
  "status": "string",                // Estado: "pending", "processing", "completed", "error"
  "message": "string",               // Mensaje informativo (opcional)
  "result": "object",                // Resultados del análisis (solo si status="completed")
  "created_at": "string",            // Fecha/hora de creación
  "completed_at": "string",          // Fecha/hora de finalización (opcional)
  "project_id": "string"             // ID del proyecto (opcional)
}
```

## Flujo de integración recomendado

### Para archivos pequeños (análisis síncrono):

1. Enviar solicitud POST a `/analyze`
2. Mostrar resultados directamente

### Para archivos grandes o múltiples (análisis asíncrono):

1. Enviar solicitud POST a `/analyze/async`
2. Obtener el `analysis_id` de la respuesta
3. Mostrar indicador de progreso
4. Consultar periódicamente GET `/analysis/{analysis_id}` (por ejemplo, cada 2-3 segundos)
5. Actualizar la UI según el estado:
   - Si `status` es "pending" o "processing": mostrar progreso
   - Si `status` es "completed": mostrar resultados
   - Si `status` es "error": mostrar mensaje de error

## Códigos de estado HTTP

- **200 OK**: La solicitud se procesó correctamente
- **400 Bad Request**: Solicitud inválida (datos faltantes o incorrectos)
- **404 Not Found**: Análisis no encontrado
- **422 Unprocessable Entity**: Error de validación en los datos de entrada
- **500 Internal Server Error**: Error del servidor

## Ejemplos de integración

### JavaScript/Fetch API

```javascript
// Ejemplo de análisis asíncrono
async function analyzeCodeAsync(code, filename) {
  // 1. Iniciar análisis
  const response = await fetch('http://localhost:8000/analyze/async', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      project_id: 'mi-proyecto',
      code_data: {
        code: code,
        filename: filename
      }
    }),
  });
  
  const data = await response.json();
  const analysisId = data.analysis_id;
  
  // 2. Mostrar estado inicial
  updateUI('Análisis iniciado...');
  
  // 3. Consultar estado periódicamente
  const checkInterval = setInterval(async () => {
    const statusResponse = await fetch(`http://localhost:8000/analysis/${analysisId}`);
    const statusData = await statusResponse.json();
    
    if (statusData.status === 'completed') {
      clearInterval(checkInterval);
      displayResults(statusData.result);
    } else if (statusData.status === 'error') {
      clearInterval(checkInterval);
      displayError(statusData.message);
    } else {
      updateUI(`Estado: ${statusData.status}`);
    }
  }, 2000);
}
```

### React

```jsx
import { useState, useEffect } from 'react';

function CodeAnalyzer() {
  const [code, setCode] = useState('');
  const [filename, setFilename] = useState('');
  const [analysisId, setAnalysisId] = useState(null);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  // Iniciar análisis
  const startAnalysis = async () => {
    try {
      const response = await fetch('http://localhost:8000/analyze/async', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: 'mi-proyecto',
          code_data: {
            code,
            filename
          }
        }),
      });
      
      const data = await response.json();
      setAnalysisId(data.analysis_id);
      setStatus(data.status);
    } catch (err) {
      setError('Error al iniciar el análisis');
    }
  };
  
  // Consultar estado
  useEffect(() => {
    if (!analysisId) return;
    
    const checkStatus = async () => {
      try {
        const response = await fetch(`http://localhost:8000/analysis/${analysisId}`);
        const data = await response.json();
        
        setStatus(data.status);
        
        if (data.status === 'completed') {
          setResult(data.result);
        } else if (data.status === 'error') {
          setError(data.message);
        }
      } catch (err) {
        setError('Error al consultar el estado');
      }
    };
    
    const interval = setInterval(checkStatus, 2000);
    return () => clearInterval(interval);
  }, [analysisId]);
  
  return (
    <div>
      <h1>Analizador de Código</h1>
      
      {/* Formulario de entrada */}
      <div>
        <input
          type="text"
          placeholder="Nombre del archivo"
          value={filename}
          onChange={(e) => setFilename(e.target.value)}
        />
        <textarea
          placeholder="Código a analizar"
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />
        <button onClick={startAnalysis}>Analizar</button>
      </div>
      
      {/* Estado */}
      {status && (
        <div>
          <p>Estado: {status}</p>
          {(status === 'pending' || status === 'processing') && (
            <div className="loading-spinner" />
          )}
        </div>
      )}
      
      {/* Error */}
      {error && (
        <div className="error">
          <p>{error}</p>
        </div>
      )}
      
      {/* Resultados */}
      {result && (
        <div className="results">
          <h2>Resultados del análisis</h2>
          <p>Puntuación: {result.average_score}</p>
          <p>Archivos analizados: {result.files_analyzed}</p>
          <p>Problemas encontrados: {result.total_issues}</p>
          
          {result.results.map((fileResult, index) => (
            <div key={index} className="file-result">
              <h3>{fileResult.filename}</h3>
              <p>Puntuación: {fileResult.score}</p>
              
              {fileResult.issues.length > 0 ? (
                <div>
                  <h4>Problemas:</h4>
                  <ul>
                    {fileResult.issues.map((issue, i) => (
                      <li key={i}>
                        <span className={`severity ${issue.severity}`}>
                          {issue.severity}
                        </span>
                        <p>{issue.message}</p>
                        <p>Línea: {issue.line}</p>
                        <p>Sugerencia: {issue.suggestion}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p>No se encontraron problemas</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default CodeAnalyzer;
```

## Implementación asíncrona con Celery

Para el procesamiento asíncrono, el servidor utiliza Celery con Redis como broker de mensajes. Esto permite:

1. Procesar análisis en segundo plano sin bloquear el servidor web
2. Distribuir la carga de trabajo entre múltiples workers
3. Manejar tareas de larga duración de manera eficiente
4. Proporcionar actualizaciones de estado en tiempo real

### Requisitos para la implementación asíncrona

- Redis (como broker de mensajes)
- Celery (para procesamiento en segundo plano)
- FastAPI (para la API REST)

### Estados de análisis

- **pending**: El análisis ha sido recibido pero aún no ha comenzado a procesarse
- **processing**: El análisis está siendo procesado actualmente
- **completed**: El análisis ha finalizado correctamente
- **error**: Ha ocurrido un error durante el análisis

## Consideraciones de seguridad

- Todos los endpoints deben ser accesibles solo a través de HTTPS en producción
- Considere implementar autenticación para proteger los endpoints
- Valide y sanitice todas las entradas para prevenir ataques de inyección
- Implemente límites de tasa para prevenir abusos de la API

## Limitaciones actuales

- El análisis síncrono tiene un tiempo límite de 30 segundos
- El tamaño máximo de código para análisis es de 1MB
- Se recomienda el uso del endpoint asíncrono para archivos grandes o múltiples

## Próximas mejoras

- Soporte para análisis de repositorios completos
- Webhooks para notificaciones de finalización de análisis
- Análisis histórico y comparativo
- Integración con sistemas de CI/CD  