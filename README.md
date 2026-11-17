# Dónde se gana y dónde se pierde plata: análisis de ventas, descuentos y rentabilidad

Análisis exploratorio de 9.994 líneas de venta de una tienda minorista (Superstore, 2014-2017), pensado como si fuera un trabajo de analista de datos en el área de Compras: ¿qué productos y categorías son rentables, cómo afectan los descuentos al margen, dónde se concentran las ventas y cuándo conviene reforzar el stock?

> **Nota:** es un proyecto personal de práctica con datos públicos. Simula el tipo de análisis que se hace en un puesto de Compras de retail; no se trata de datos reales de ninguna empresa.

**App interactiva:** [COMPLETAR con el link de Streamlit Cloud cuando lo tengas]

## Preguntas que responde el análisis

1. ¿Qué categorías y subcategorías generan más ventas y cuáles dejan más beneficio?
2. ¿Hay productos que se venden pero dan pérdida?
3. ¿Cómo afecta el descuento al beneficio y desde qué nivel empieza a haber pérdidas?
4. ¿Qué pocos productos concentran el 80% de las ventas? (análisis ABC)
5. ¿Cómo evolucionan las ventas por mes y hay estacionalidad?

## Hallazgos principales

- **Furniture factura casi lo mismo que las otras dos categorías (unos $742 mil) pero con un margen de 2,5%**, frente a 17,4% de Technology y 17,0% de Office Supplies.
- **Tables, Bookcases y Supplies terminan en pérdida.** En las tres, el margen es positivo sin descuento y se vuelve negativo al descontar (por ejemplo, Tables: 18,5% de margen sin descuento y -27,7% con descuentos de 21-40%).
- **El descuento destruye margen de forma escalonada:** 29,5% sin descuento, 11,9% con 1-20%, -15,3% con 21-40% y -77,4% con más de 40%. El punto de quiebre está cerca del 20%.
- **301 de 1.850 productos (16%) pierden plata**, unos $77 mil en total, y los 10 peores concentran el 38% de esa pérdida. En la mayoría el descuento promedio supera el 35%, aunque no explica todos los casos: dos de los diez pierden con descuentos bajos, lo que apunta a otros factores (por ejemplo, el costo).
- **Análisis ABC:** el 23% de los productos (419) genera el 80% de las ventas. La mitad del catálogo (clase C) aporta solo el 5%.
- **Estacionalidad:** septiembre, noviembre y diciembre concentran las ventas; noviembre vende en promedio más de cinco veces que febrero. El descuento promedio es similar todos los meses (15% a 17%), por lo que no explica las diferencias de margen entre meses.

## Recomendaciones

- Tope de descuento de 20% en general, y descuento cero en Tables y Supplies.
- Concentrar el control de stock y de proveedores en los productos clase A.
- Reforzar stock desde agosto para los meses pico y comprar poco en enero y febrero.
- Revisar costos de los productos que pierden aun con descuentos bajos.

## Cómo ejecutar la app

```bash
pip install -r requirements.txt
streamlit run app.py
```

El archivo de datos debe llamarse `superstore.csv` y estar en la misma carpeta que `app.py`. Si no está, la app permite subirlo desde la barra lateral.

## Estructura del repositorio

```
├── app.py                  # App interactiva en Streamlit
├── requirements.txt        # Dependencias
├── superstore.csv          # Datos
├── notebooks/
│   └── superstore_notb.ipynb   # Limpieza y análisis exploratorio
└── README.md
```

## Herramientas

Python, pandas, Plotly, Streamlit, Google Colab.

## Limitaciones

- Es una tienda de muebles, tecnología y artículos de oficina, no un supermercado. Las preguntas y el método son los mismos que en retail, pero los resultados no se pueden extrapolar.
- El análisis es descriptivo: muestra asociaciones entre descuentos, margen y ventas, pero no prueba causalidad ni predice.
- No incluye costos ni datos de proveedores, que serían clave en un análisis de Compras real.

## Datos

Dataset público Superstore, disponible en Kaggle. 
https://www.kaggle.com/datasets/vivek468/superstore-dataset-final

## Autor

Tatiana Flores· Estudiante de Ingeniería en Ciencia de Datos · tatianaflores.ofc@gmail.com