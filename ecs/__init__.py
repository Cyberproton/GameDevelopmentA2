from types import MethodType
from typing import TypeVar, Type, Optional
from weakref import ref, WeakMethod


class Component:
    pass


TComponent = TypeVar("TComponent", bound=Component)


class Signal:
    pass


TSignal = TypeVar("TSignal", bound=Signal)


class Entity:
    def __init__(self, entity_type: str, components=None):
        if components is None:
            components = []

        self.id = -1
        self.entity_type = entity_type

        self.components = {}
        if components is not None:
            for component in components:
                self.components[type(component)] = component

        self.tags = []

    def get_component(self, component_type: Type[TComponent]) -> Optional[TComponent]:
        if component_type not in self.components:
            return None
        return self.components[component_type]

    def has_component(self, component_type: Type[TComponent]) -> bool:
        return component_type in self.components

    def add_component(self, component: Component):
        self.components[type(component)] = component

    def remove_component(self, component_type: Type[TComponent]):
        self.components.pop(component_type)


TEntity = TypeVar("TEntity", bound=Entity)


class System:
    def __init__(self, world):
        self.world = world

    def process(self):
        pass


TSystem = TypeVar("TSystem", bound=System)


class SignalDispatcher:
    def __init__(self):
        self.handlers = {}

    def dispatch(self, signal: Signal):
        signal_type = type(signal)
        if signal_type not in self.handlers:
            return
        h = self.handlers[signal_type]
        for func in h:
            func()(signal)

    def register_handler(self, signal_type: Type[TSignal], func):
        if signal_type not in self.handlers:
            self.handlers[signal_type] = []
        h = self.handlers[signal_type]
        if isinstance(func, MethodType):
            h.append(WeakMethod(func, self._make_callback(signal_type)))
        else:
            h.append(ref(func, self._make_callback(signal_type)))

    def unregister_handler(self, signal_type: Type[TSignal], func):
        if signal_type not in self.handlers:
            self.handlers[signal_type] = []
        h = self.handlers[signal_type]
        h.remove(func)

    def _make_callback(self, signal_type: Type[TSignal]):
        def callback(weak_method):
            self.handlers[signal_type].remove(weak_method)

        return callback


class World:
    def __init__(self):
        self.current_id = 0
        self.entity_container: EntityContainer = EntityContainer()
        self.system_container = SystemContainer()
        self.signal_dispatcher = SignalDispatcher()

    def process(self):
        for system in self.system_container.systems:
            system.process()

    def get_entities(self, entity_type: Type[TEntity] = None) -> list[TEntity]:
        return self.entity_container.get_entities(entity_type)

    def add_entity(self, entity: Entity):
        self.entity_container.add_entity(entity)

    def remove_entity(self, entity: Entity):
        self.entity_container.remove_entity(entity)

    def get_system(self, system_type: Type[TSystem]) -> TSystem:
        return self.system_container.get_system(system_type)

    def add_system(self, system: System):
        self.system_container.add_system(system)

    def dispatch_signal(self, signal: Signal):
        self.signal_dispatcher.dispatch(signal)

    def register_handler(self, signal_type: Type[TSignal], func):
        self.signal_dispatcher.register_handler(signal_type, func)

    def unregister_handler(self, signal_type: Type[TSignal], func):
        self.signal_dispatcher.unregister_handler(signal_type, func)

    def get_next_id(self):
        self.current_id += 1
        return self.current_id


class EntityContainer:
    def __init__(self):
        self.current_id = 0
        self.entities = {}

    def get_entities(self, entity_type: Type[TEntity] = None) -> list[TEntity]:
        if not entity_type:
            return list(self.entities.values())
        filtered = filter(lambda entity: type(entity) is entity_type, self.entities.values())
        return list(filtered)

    def add_entity(self, entity: Entity):
        entity.id = self.get_next_id()
        self.entities[entity.id] = entity

    def remove_entity(self, entity: Entity):
        self.entities.pop(entity.id)

    def get_entity_of_type(self, entity_type: str) -> list[Entity]:
        filtered = filter(lambda entity: entity.entity_type == entity_type, self.entities.values())
        return list(filtered)

    def get_entities_with_component(self, component_type: Type[TComponent]) -> list[Entity]:
        filtered = filter(
            lambda entity: any(type(component) is component_type for component in entity.components.values()),
            self.entities.values())

        return list(filtered)

    def get_next_id(self):
        self.current_id += 1
        return self.current_id


class SystemContainer:
    def __init__(self):
        self.systems = []

    def get_system(self, system_type: Type[TSystem]) -> TSystem:
        for system in self.systems:
            if type(system) is not system_type:
                continue
            return system

    def add_system(self, system: System):
        self.systems.append(system)
