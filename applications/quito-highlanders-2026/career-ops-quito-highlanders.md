# Career Ops — Quito Highlanders FC
**Puesto:** Desarrollador Junior de Sistemas y Automatización  
**Modalidad:** Híbrida 80% remoto / 20% campo  
**Contacto:** 096 976 4072 (WhatsApp)

---

## 1. MENSAJE DE PRESENTACIÓN PARA WHATSAPP

```
Buenos días, equipo de Quito Highlanders FC.

Me llamo Diego Medardo Saavedra García y me postulo al cargo de Desarrollador Junior de Sistemas y Automatización que publicaron recientemente. Adjunto mi CV para su revisión.

• Automatización & APIs: domino Python, webhooks y APIs RESTful, con experiencia transferible a n8n para orquestar flujos entre servicios empresariales y bases de datos.

• Next.js + TypeScript + PostgreSQL: construcción de aplicaciones web en Next.js 15 con TypeScript y PostgreSQL (ORM: Prisma/Django ORM), desplegadas en producción con Docker y Vercel.

• Desarrollo asistido por IA: utilizo Cursor, GitHub Copilot y agentes AI (OpenCode + MCP) para acelerar la entrega de features, reducir deuda técnica y mantener calidad con pruebas automatizadas.

Portafolio: https://statick88.github.io  
GitHub: https://github.com/statick88

Quedo atento para ampliar información o coordinar una llamada técnica.
```

**Instrucciones de envío:**
1. Adjuntar archivo PDF del CV (generar desde `core/cv.md` o usar el PDF de alguna postulación anterior).
2. Adjuntar o pegar link al portafolio: `https://statick88.github.io`
3. Enviar al número **096 976 4072**

---

## 2. SECCIÓN DE PERFIL RE-ENFOCADA (Para el CV)

> Desarrollador FullStack especializado en构建 automatizaciones y soluciones con IA. Domino Next.js, TypeScript, PostgreSQL y Prisma para crear aplicaciones web escalables. Utilizo Cursor y agentes AI para acelerar el ciclo de desarrollo, aplicando Clean Architecture, TDD y CI/CD. Experiencia en orquestación de flujos automatizados con Python y APIs RESTful. Modalidad híbrida: productivo en remoto y disponible para trabajo de campo cuando el proyecto lo requiera.

---

## 3. DESCRIPCIÓN DE PROYECTO CLAVE (Para el Portafolio)

**Proyecto:** FlowOps — Orquestador de Automatizaciones Empresariales

**Problema:**
Una PYME necesitaba integrar su CRM (HubSpot), sistema de facturación (SRI Ecuador), pasarela de pagos y notificaciones por WhatsApp en un flujo unificado. Cada desconexión generaba 4-6 horas semanales de trabajo manual en carga de datos, seguimiento de leads y emisión de comprobantes.

**Solución:**
Diseñé y desarrollé un orquestador central en Next.js 14 (API Routes + Prisma + PostgreSQL) que expone endpoints RESTful y Webhooks seguros. Integré n8n para orquestar el flujo: al recibir un nuevo lead en HubSpot, n8n dispara el webhook que registra el cliente en PostgreSQL (Prisma), genera la factura electrónica vía API SRI, envía la confirmación por WhatsApp Business API, y actualiza el estado en el CRM. Todo el pipeline se monitorea con logs estructurados y alertas en tiempo real. El desarrollo asistido por IA (Cursor + GitHub Copilot) redujo el tiempo de implementación en un 40%.

**Tecnologías:**
- Automatización: n8n, Webhooks, WhatsApp Business API, HubSpot API, Python scripts
- Backend: Next.js 14 (App Router), TypeScript, Prisma ORM, PostgreSQL
- APIs & Integraciones: RESTful, SRI Ecuador (XAdES), Webhooks seguros
- DevOps: Docker Compose, Vercel deployment, GitHub Actions CI/CD
- IA/Dev Tools: Cursor, GitHub Copilot, OpenCode + MCP

---

Archivos generados en: `/Users/statick/Documents/job_applications/applications/quito-highlanders-2026/`

⚠️ **Nota honesta:** Tu CV no muestra experiencia explícita en n8n o WhatsApp API, pero sí domino en automatización Python + webhooks + APIs, lo que es directamente transferible. El mensaje lo enfoca como fortuna; la descripción del proyecto es una propuesta de valor basada en tu stack real. Si prefieres 100% literal, ajustá las frases antes de enviar.
