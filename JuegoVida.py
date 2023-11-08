"""
Modifico el juego de la vida que programó Edgar Covantes de Mty
Él lo hizo todo para Jupyter usando GColab y tomando datos usando el DataCollector
Nos dio el código en un GDrive
Octubre 8, 2021
"""

# La clase Model se hace cargo de los atributos a nivel del modelo, maneja los agentes.
# Cada modelo puede contener múltiples agentes y todos ellos son instancias de la clase Agent.
from mesa import Agent, Model

# Debido a que necesitamos un solo agente por celda elegimos SingleGrid que fuerza un solo objeto por celda.
from mesa.space import SingleGrid

# Con SimultaneousActivation hacemos que todos los agentes se activen de manera simultanea.
from mesa.time import SimultaneousActivation
import numpy as np

class GameLifeAgent(Agent):
    '''
    Representa a un agente o una celda con estado vivo (1) o muerto (0)
    '''
    def __init__(self, unique_id, model):
        '''
        Crea un agente con estado inicial aleatorio de 0 o 1, también se le asigna un identificador
        formado por una tupla (x,y). También se define un nuevo estado cuyo valor será definido por las
        reglas mencionadas arriba.
        '''
        super().__init__(unique_id, model)
        self.live = np.random.choice([0,1])
        self.next_state = None

    def step(self):
        '''
        Este método es el que calcula si la celda vivirá o morirá dependiendo el estado de sus vecinos.
        El estado live de la siguiente generación no se cambia aquí se almacena en self.next_state. La idea
        es esperar a que todos los agentes calculen su estado y una vez hecho eso, ya hacer el cambio.
        '''
        live_neighbours = 0

        neighbours = self.model.grid.get_neighbors(
            self.pos,
            moore=True,
            include_center=False)

        for neighbor in neighbours:
            live_neighbours = live_neighbours + neighbor.live

        self.next_state = self.live
        if self.next_state == 1:
            if live_neighbours < 2 or live_neighbours > 3:
                self.next_state = 0
        else:
            if live_neighbours == 3:
                self.next_state = 1

    def advance(self):
        '''
        Define el nuevo estado calculado del método step.
        '''
        self.live = self.next_state

class GameLifeModel(Model):
    '''
    Define el modelo del juego de la vida.
    '''
    def __init__(self, width, height):
        self.num_agents = width * height
        self.grid = SingleGrid(width, height, True)
        self.schedule = SimultaneousActivation(self)
        self.running = True #Para la visualizacion usando navegador

        for content, (x, y) in self.grid.coord_iter():
            a = GameLifeAgent((x, y), self)
            self.grid.place_agent(a, (x, y))
            self.schedule.add(a)


    def step(self):
        self.schedule.step()