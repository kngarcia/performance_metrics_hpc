# ACO — Optimizacion de Rutas con GPU

Simulacion de Ant Colony Optimization sobre un espacio de waypoints
con obstaculos rectangulares. Acelerado con PyTorch (CUDA / Apple MPS / CPU).

## Estructura

```
aco_app/
├── main.py                 # Punto de entrada
├── requirements.txt
└── aco_app/
    ├── config.py           # Configuracion global y colores
    ├── map_gen.py          # Generacion del mapa con semilla
    ├── aco_core.py         # Nucleo ACO con PyTorch
    ├── renderer.py         # Visualizacion pygame + panel de control
```

## Instalacion

### Cualquier plataforma (CPU)
```bash
pip install -r requirements.txt
```

### Apple Silicon (GPU MPS)
```bash
pip install -r requirements.txt
# PyTorch detecta MPS automaticamente — no se necesita nada extra
```

### NVIDIA / Colab (GPU CUDA)
```bash
# Instala PyTorch con soporte CUDA segun tu version de CUDA:
# https://pytorch.org/get-started/locally/
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install pygame Pillow numpy
```

## Uso

```bash
# Ejecutar con parametros por defecto
python main.py

# Especificar semilla y parametros iniciales
python main.py --seed 42 --ants 30 --iter 150 --alpha 2.0 --beta 4.0 --rho 0.3
```

## Controles

| Tecla   | Accion                              |
|---------|-------------------------------------|
| SPACE   | Pausar / reanudar simulacion        |
| R       | Reiniciar con parametros del panel  |
| ESC / Q | Salir                               |

## Panel de control

Todos los parametros se pueden ajustar en tiempo real desde el panel lateral:

- **N hormigas** — cantidad de agentes por iteracion
- **M iteraciones** — total de ciclos ACO
- **alpha** — importancia de las feromonas en la decision
- **beta** — importancia de la heuristica (1/distancia)
- **rho** — tasa de evaporacion de feromonas
- **Waypoints** — nodos intermedios del grafo
- **Obstaculos** — cantidad de rectangulos en el mapa
- **Velocidad** — iteraciones calculadas por frame dibujado
- **Semilla** — semilla para reproducir el mismo mapa

Presiona **Ejecutar** para aplicar los cambios y reiniciar la simulacion.

## Parametros del enunciado

| Simbolo | Widget en panel       |
|---------|-----------------------|
| N       | N hormigas            |
| M       | M iteraciones         |
| tau     | (visible como heatmap)|
| rho     | rho (evaporacion)     |
| alpha   | alpha                 |
| beta    | beta                  |

## Deteccion de GPU

El modulo `config.py` detecta automaticamente el mejor dispositivo disponible:

```
CUDA disponible  →  GPU NVIDIA
MPS disponible   →  GPU Apple Silicon (M1/M2/M3)
ninguno          →  CPU
```

El dispositivo activo se muestra en la esquina superior del panel lateral.
