# TechNorte — analítica de YouTube

Dashboard web estático para portfolio, con diseño responsive y gráficos interactivos. No requiere Power BI ni librerías externas.

## Datos automáticos

El HTML solicita automáticamente los nueve CSV en `./data/` al abrirse. Para publicarlo, sube `Dashboard TechNorte Analytics.html` y la carpeta `data` a la misma ubicación/ruta del sitio. Conserva los nombres de archivo y encabezados.

Al abrirlo con doble clic desde el disco, algunos navegadores bloquean las lecturas locales por seguridad. En ese caso, sirve la carpeta con un servidor web local (por ejemplo, `python -m http.server`) y abre el HTML a través de `http://localhost`. En un portfolio publicado, se carga sin botón de importación.

## Mantenimiento

- `data/`: CSV que alimentan el dashboard.
- `generar_dashboard_html.mjs`: regenera el HTML con `node generar_dashboard_html.mjs`.
- `generar_datos.mjs` o `generar_datos.py`: crean datos sintéticos reproducibles en `data/`.
- `extraer_youtube.py`: extractor opcional de métricas públicas. Requiere `YT_API_KEY` en el entorno. La API pública no proporciona retención ni históricos completos de canales ajenos.

**Los datos actuales son sintéticos.** TechNorte y los canales de comparación son demostrativos. Los minutos vistos se estiman como vistas × duración × retención supuesta; no son el tiempo real de visualización de YouTube Studio.
