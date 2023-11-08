from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
import random

class CleaningRobot(Agent):
    """
    Un robot de limpieza reactivo que aspira las celdas sucias y se mueve aleatoriamente.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
        self.model.total_moves += 1  # Incrementar el conteo de movimientos

    def clean(self):
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for content in cell_contents:
            if isinstance(content, Dirt):
                self.model.grid.remove_agent(content)
                self.model.dirt.remove(content)

    def step(self):
        self.clean()  # Clean the current cell
        self.move()   # Move to a new cell

class Dirt(Agent):
    """
    Una celda de suciedad que será limpiada por el robot.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class CleaningModel(Model):
    """
    El modelo que representa la habitación con una cuadrícula MxN y robots de limpieza.
    """

    def __init__(self, width, height, initial_dirt, n_robots, max_steps):
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True
        self.max_steps = max_steps
        self.steps = 0
        self.dirt = []
        self.total_moves = 0  # Añadido para rastrear el número total de movimientos

        # Inicializar la suciedad
        for i in range(initial_dirt):
            dirt = Dirt(i, self)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(dirt, (x, y))
            self.dirt.append(dirt)
            self.schedule.add(dirt)

        # Inicializar los robots
        for i in range(n_robots):
            robot = CleaningRobot(i + initial_dirt, self)
            self.grid.place_agent(robot, (1, 1))  # Todos los agentes comienzan en (1,1)
            self.schedule.add(robot)

    def step(self):
        self.schedule.step()
        self.steps += 1
        # Detener la simulación si no queda suciedad o se alcanza el tiempo máximo
        if not self.dirt or self.steps >= self.max_steps:
            self.running = False
            self.print_stats()  # Imprimir las estadísticas al final

    def print_stats(self):  # Imprimir las estadísticas
        print(
            f"Tiempo necesario hasta que todas las celdas estén limpias (o se haya llegado al tiempo máximo): {self.steps}")
        print(
            f"Porcentaje de celdas limpias después del termino de la simulación: {100 * (1 - len(self.dirt) / (self.grid.width * self.grid.height))}%")
        print(
            f"Número de celdas sucias que quedaron: {len(self.dirt)}")  # Añadido el número de celdas sucias que quedaron
        print(f"Número de movimientos realizados por todos los agentes: {self.total_moves}")


# Parámetros de la simulación
width = 10
height = 10
initial_dirt = int(width * height * 0.1)  # 10% de las celdas sucias
n_robots = 10
max_steps = 100

# Ejecutar la simulación
model = CleaningModel(width, height, initial_dirt, n_robots, max_steps)
while model.running:
    model.step()

def agent_portrayal(agent):
    if isinstance(agent, CleaningRobot):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": "red",  # Cambiado a rojo
                     "r": 0.5}
    elif isinstance(agent, Dirt):
        portrayal = {"Shape": "circle",  # Cambiado a círculo
                     "Filled": "true",
                     "Layer": 0,
                     "Color": "green",  # Cambiado a verde
                     "r": 0.5}  # Añadido el radio
    return portrayal

ancho = 28
alto = 28
grid = CanvasGrid(agent_portrayal, ancho, alto, 750, 750)
server = ModularServer(CleaningModel,
                       [grid],
                       "Cleaning Robot Model",
                       {"width": ancho, "height": alto, "initial_dirt": int(ancho * alto * 0.1), "n_robots": 10,
                        "max_steps": 300})
server.port = 8522  # Cambiado a un puerto diferente
server.launch()
