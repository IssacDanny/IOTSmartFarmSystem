from .CommandModel import ActivationCommand,ActivatePump,ActivateFan

class CommandRegistry: # registry pattern
    _registry = {}

    @classmethod
    def register(cls, command_Type: str):
        def decorator(factory):
            cls._registry[command_Type] = factory
            return factory
        return decorator

    @classmethod
    def create(cls, DeviceInfo, mqtt_manager, ActivationDecription: dict) -> ActivationCommand:
        command_Type = ActivationDecription["Body"]["CommandType"]
        factory = cls._registry.get(command_Type)
        if not factory:
            raise ValueError(f"No command registered for type '{command_Type}'")
        return factory(DeviceInfo, mqtt_manager, ActivationDecription)


class ActivationGenerator:
    _instance = None
    def __new__(cls, *args, **kwargs): # singleton pattern
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def generate(self, DeviceInfo, mqtt_manager, ActivationDescription: dict) -> ActivationCommand:
        return CommandRegistry.create(DeviceInfo, mqtt_manager, ActivationDescription)

@CommandRegistry.register("ActivePump") # this line return a decorator and call it with the bellow function as argument
def create_pump_command(DeviceInfo, mqtt_manager, ActivationDescription):
    return ActivatePump(DeviceInfo, mqtt_manager, ActivationDescription["Body"]["Parameter"])

@CommandRegistry.register("ActiveFan")
def create_light_command(DeviceInfo, mqtt_manager, ActivationDescription):
    return ActivateFan(DeviceInfo, mqtt_manager, ActivationDescription["Body"]["Parameter"])