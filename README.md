# sid_nonconformity

Módulo ligero para registrar y seguir no conformidades en Odoo 15, pensado para una empresa de distribución con sistema integrado ISO 9001 e ISO 14001.

## Objetivo

Centralizar no conformidades de proveedor, cliente, almacén, producto, proceso interno, auditoría e incidencias ambientales, con trazabilidad mediante chatter, actividades, adjuntos y enlaces a documentos operativos.

## Funcionalidades principales

- Registro `sid.nonconformity` con secuencia `NC/YYYY/0001`.
- Chatter, seguidores, adjuntos y actividades.
- Estados: borrador, abierta, acción correctiva, verificación de eficacia, cerrada y cancelada.
- Clasificación por ISO 9001, ISO 14001 o sistema integrado.
- Tipos de NC: proveedor, cliente, almacén/logística, producto, proceso, ambiental, auditoría y otros.
- Responsable, revisor, severidad, prioridad, fecha de detección, fecha límite y cierre.
- Enlaces operativos a compra, venta, albarán, línea de operación, producto, lote y partner.
- Campos de tratamiento: descripción/evidencia, contención inmediata, causa raíz, acción correctiva, acción preventiva, verificación de eficacia y cierre.
- Campo específico de impacto ambiental para ISO 14001.
- Indicadores simples: vencida, días abierta y días hasta cierre.
- Menú propio `Quality / ISO > Nonconformities`.
- Botón y contador de NCs en pedidos de compra, pedidos de venta y albaranes.

## Dependencias

- `mail`
- `stock`
- `purchase`
- `sale_management`

## Uso recomendado

1. Crear la NC desde el menú o desde el botón `Create NC` de una compra, venta o albarán.
2. Completar origen, descripción y evidencia.
3. Asignar responsable y fecha límite.
4. Registrar contención inmediata.
5. Analizar causa raíz y definir acción correctiva/preventiva.
6. Pasar a verificación y documentar la eficacia.
7. Cerrar la NC cuando causa raíz y acción correctiva estén informadas.

## Notas de diseño

Este módulo está inspirado funcionalmente en flujos de no conformidades tipo OCA/management-system, pero se mantiene deliberadamente simple para uso operativo diario. No depende del stack `mgmtsystem`, ni de páginas documentales, ni de catálogos complejos. La prioridad es trazabilidad, seguimiento, comunicación y relación con documentos reales de distribución.

## Próximas mejoras sugeridas

- Reglas de cierre por tipo de NC.
- Plantillas de NC para proveedor, cliente, almacén y ambiental.
- Acciones planificadas con responsables y fechas por línea.
- Informe PDF de NC.
- Automatización de avisos por vencimiento.
- Dashboard por proveedor, cliente, tipo, severidad y plazo medio de cierre.
