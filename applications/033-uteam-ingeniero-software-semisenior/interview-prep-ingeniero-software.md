# Interview Prep — Ingeniero de Software Semi-Senior (Uteam)

## Preguntas Técnicas Probables

### Node.js / TypeScript
1. **¿Cómo manejas la asincronía en Node.js?** — Event loop, Promesas, async/await, manejo de errores en cadenas de promesas
2. **¿Qué patrones de diseño aplicas en NestJS?** — Dependency Injection, Guards, Interceptors, Pipes, Middleware
3. **¿Cómo estructuras un proyecto NestJS para microservicios?** — Módulos, DTOs, Clean Architecture, separación de concerns
4. **¿Experiencia con bases de datos en Node.js?** — TypeORM/Prisma con PostgreSQL, patrones repository, migraciones

### Kubernetes / AWS EKS
5. **¿Cómo despliegas una aplicación en Kubernetes?** — Deployments, Services, Ingress, ConfigMaps, Secrets, Health checks
6. **¿Qué es EKS y cómo lo has utilizado?** — Managed Kubernetes on AWS, node groups, auto-scaling, load balancing
7. **¿Cómo configuras CI/CD para despliegue en K8s?** — GitHub Actions, docker build, kubectl apply, rolling updates

### Microservicios
8. **¿Cómo diseñas la comunicación entre microservicios?** — REST,消息队uing (RabbitMQ/Kafka), event-driven architecture
9. **¿Cómo manejas la consistencia en microservicios?** — Saga pattern, eventual consistency, distributed transactions
10. **¿Cómo monitoreas microservicios en producción?** — Logging, metrics, tracing, health endpoints

### Metodologías Ágiles
11. **¿Cómo aplicas Scrum en tu trabajo diario?** — Sprint planning, daily standups, retrospectives, backlog grooming
12. **¿Qué es TDD y cómo lo implementas?** — Red-green-refactor, cobertura de tests, integración con CI

## Gap Defense

### Gap: Residencia en Argentina
**Estrategia:** Si el requisito es flexible para 100% remoto, enfatizar disponibilidad full-time remoto. Si es presencial, ser transparente sobre ubicación actual y disposición a reubicación.

### Gap: AWS EKS específico
**Defensa:** "Mi experiencia con Kubernetes y AWS es directamente transferible a EKS. He desplegado aplicaciones en clusters K8s con orquestación de containers, y mi conocimiento de AWS (EC2, S3, Lambda) facilita la curva de aprendizaje específica de EKS."

### Gap: Microservicios explícitos
**Defensa:** "Aunque mi experiencia formal es con Clean Architecture en monolitos modularizados, el patrón es directamente aplicable a microservicios. He diseñado sistemas con separación de concerns, bounded contexts y APIs independientes."

## STAR Stories

### Story 1: API de Facturación Electrónica
- **S:** Necesidad de implementar facturación electrónica SRI para clientes empresariales
- **T:** Diseñar API RESTful que procese transacciones en tiempo real con alta disponibilidad
- **A:** Implementé con NestJS + TypeScript, patrón repository, validación estricta de DTOs, testing automatizado
- **R:** API en producción procesando transacciones con 99%+ uptime, open-source para la comunidad

### Story 2: Despliegue CI/CD con Kubernetes
- **S:** Proceso de deploy manual causaba errores y perdía tiempo
- **T:** Automatizar el pipeline de build, test y deploy
- **A:** Configuré GitHub Actions con docker build, testing automatizado, y despliegue en Kubernetes
- **R:** Reducción de 60% en tiempo de release, cero errores de deploy en producción

### Story 3: Sistema de Gestión Educativa
- **S:** Institución necesitaba sistema para gestionar 6+ cursos simultáneos
- **T:** Construir aplicación web escalable con múltiples módulos
- **A:** Arquitectura modular con Django + PostgreSQL, Docker para containerización, deployment automatizado
- **R:** Sistema en uso activo, 93.4/100 promedio de evaluación de estudiantes

## Key Talking Points

1. **10+ años de experiencia** construyendo software en producción, no solo en proyectos académicos
2. **Full-stack con foco backend:** Node.js/TypeScript + Kubernetes + CI/CD = stack que buscan
3. **Seguridad by design:** Mi formación en ciberseguridad aporta una perspectiva que otros candidatos no tienen
