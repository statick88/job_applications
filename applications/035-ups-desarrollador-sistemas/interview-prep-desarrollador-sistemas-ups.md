# Interview Prep — Desarrollador de Sistemas (UPS)

## Preguntas Técnicas Probables

### Desarrollo Web y Backend
1. **¿Cómo diseñas una API RESTful escalable?** — NestJS con módulos, DTOs, validación con class-validator, patrón repository, testing automatizado
2. **¿Qué es Clean Architecture y cómo la aplicas?** — Separación de capas (domain, data, presentation), dependencias inward, testabilidad
3. **¿Cómo manejas la autenticación en aplicaciones web?** — JWT, refresh tokens, OAuth2, role-based access control
4. **¿Experiencia con bases de datos relacionales?** — PostgreSQL, diseño de esquemas, migraciones, índices, consultas optimizadas
5. **¿Cómo implementas CI/CD?** — GitHub Actions, pipelines de build/test/deploy, Docker, Kubernetes

### Arquitectura y Diseño
6. **¿Cómo decides entre monolito y microservicios?** — Complejidad del dominio, equipo, escalabilidad, madurez del proyecto
7. **¿Qué patrones de diseño has utilizado?** — Repository, Strategy, Factory, Observer, Dependency Injection
8. **¿Cómo manejas la escalabilidad?** — Load balancing, caching (Redis), database optimization, horizontal scaling

### Frontend
9. **¿Cómo optimizas el rendimiento en React/Next.js?** — Lazy loading, memoization, SSR/SSG, image optimization, code splitting
10. **¿Experiencia con TypeScript?** — Tipado estricto, generics, utility types, discriminados

### Metodologías
11. **¿Cómo aplicas TDD?** — Red-green-refactor, cobertura de tests, testing de integración
12. **¿Cómo gestionas el código en equipo?** — Git flow, code review, pull requests, convenciones de commits

## STAR Stories

### Story 1: API Facturación Electrónica SRI
- **S:** Empresas ecuatorianas necesitaban integración con el SRI para facturación electrónica
- **T:** Construir una API RESTful open-source que procese transacciones en tiempo real
- **A:** NestJS + TypeScript, patrón repository, validación estricta de DTOs, testing automatizado, Docker
- **R:** API en producción con 99%+ uptime, utilizada por múltiples empresas, open-source

### Story 2: Plataforma SaaS (Saavedra Construction)
- **T:** Sistema de gestión para empresa de construcción, accesible desde cualquier dispositivo
- **A:** Next.js 15, Clean Architecture, deploy en Vercel con CDN, responsive design
- **R:** Sistema en producción con arquitectura modular, despliegue continuo, 0 downtime

### Story 3: Sistema de Gestión Educativa
- **S:** Institución necesitaba sistema para gestionar 6+ cursos simultáneos
- **T:** Aplicación web escalable con múltiples módulos
- **A:** Django + PostgreSQL, Docker para containerización, deployment automatizado
- **R:** Sistema en uso activo, gestión de +500 estudiantes, 93.4/100 promedio evaluación

### Story 4: CyberVault (Gestor de Credenciales)
- **S:** Necesidad de gestor de credenciales con seguridad de nivel empresarial
- **T:** Implementar encriptación de 4 capas con Zero-Knowledge
- **A:** TypeScript, IPFS, noble-curves/hashes, Docker + Kubernetes
- **R:** Aplicación con seguridad de nivel bancario, desplegada en K8s

## Key Talking Points

1. **10+ años construyendo software en producción** — No solo proyectos académicos, sino sistemas reales con usuarios
2. **Formación de posgrado + experiencia práctica** — Magíster en Ciencias de la Computación + implementación real de arquitecturas escalables
3. **Full-stack con foco en calidad** — TypeScript, Clean Architecture, TDD, CI/CD = código mantenible y escalable
