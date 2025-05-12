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
    def create(cls, DeviceInfo, ActivationDecription: dict) -> ActivationCommand:
        command_Type = ActivationDecription["Body"]["CommandType"]
        factory = cls._registry.get(command_Type)
        if not factory:
            raise ValueError(f"No command registered for type '{command_Type}'")
        return factory(DeviceInfo, ActivationDecription)


class ActivationGenerator:
    _instance = None
    def __new__(cls, *args, **kwargs): # singleton pattern
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def generate(self, DeviceInfo, ActivationDescription: dict) -> ActivationCommand:
        return CommandRegistry.create(DeviceInfo, ActivationDescription)

@CommandRegistry.register("ActivePump") # this line return a decorator and call it with the bellow function as argument
def create_pump_command(DeviceInfo, ActivationDescription):
    return ActivatePump(DeviceInfo, ActivationDescription["Body"]["Parameter"])

@CommandRegistry.register("ActiveFan")
def create_light_command(DeviceInfo,ActivationDescription):
    return ActivateFan(DeviceInfo, ActivationDescription["Body"]["Parameter"])