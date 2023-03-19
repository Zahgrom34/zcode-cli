from sys import argv
from functools import wraps
from typing import List, Optional
from types import FunctionType
from models import ArgumentedCMD
from src.application import ContextApplication, ErrorHandler
from errors.base import DeclaredBaseCliIsNotDefined, IncorrectCommandArgument
from rich import print as cprint
from inspect import getfullargspec

from argparse import ArgumentParser


class BaseCLI:

    def __init__(self) -> None:
        pass

    def get_arguments(self):
        result = []

        for key, value in self.__class__.__dict__["__annotations__"].items():
            if value in [list, int, dict, str]:
                result.append({"argument": key, "type": value})

        return result

    def callback(self, ctx: ContextApplication):
        """
        ## Callback function, all callbacks would be come here
        """
        pass


class GenericCLI:
    app_name: str
    help: Optional[str]

    def __init__(self) -> None:
        pass

    def get_methods(self):
        result = []
        for key, value in self.__class__.__dict__.items():
            if isinstance(value, FunctionType) and key != "__init__":
                args = getfullargspec(getattr(self, key))
                args = [{"argument": key, "type": value}
                        for key, value in args.annotations.items()]

                result.append({"name": key, "args": args})

        return result

    def __str__(self) -> str:
        return self.app_name


def console_command(f):
    """
    ## Console command.

    Command decorator for generic cli
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            return f[args[0]]

    return decorator


class CLI:
    app_name: str
    help: Optional[str]
    extra_arguments: Optional[dict]
    cli_list: List[BaseCLI] = []
    generic_cli_list: List[GenericCLI] = []
    handler_list: List[ErrorHandler] = []

    def __init__(self, app_name: str, help: Optional[str] = None, **kwarg) -> None:
        self.app_name = app_name
        self.help = help
        self.extra_arguments = kwarg

    def register_command(self, instance: BaseCLI):
        if issubclass(type(instance), BaseCLI):
            self.cli_list.append(instance)
            return

        raise DeclaredBaseCliIsNotDefined(instance.__class__.__name__)

    def register_handler(self, handler: ErrorHandler):
        if issubclass(type(handler), ErrorHandler):
            self.handler_list.append(handler)
            return

        raise DeclaredBaseCliIsNotDefined(handler.__class__.__name__)

    def register_generic_command(self, instance: GenericCLI):
        if issubclass(type(instance), GenericCLI):
            self.generic_cli_list.append(instance)
            return

        raise DeclaredBaseCliIsNotDefined(instance.__class__.__name__)

    def run(self):
        self.load_basecli()
        self.load_genericcli()

    def load_basecli(self):
        cli_list = self.cli_list

        for cli in cli_list:

            if argv[1] == cli.__class__.__name__.lower():
                if argv[2] in ["-h", "--help"]:
                    cprint(cli)
                    return

                arguments = cli.get_arguments()
                if len(argv[2:]) > len(arguments):
                    raise IncorrectCommandArgument(
                        argv[1].lower(), argv[(len(argv) - 1) + (len(arguments) - 1)])

                for index, item in enumerate(arguments):
                    cmd_argument = argv[index + 2]
                    
                    if cmd_argument.isnumeric():
                        cmd_argument = int(cmd_argument)

                    if type(cmd_argument) != item["type"]:
                        raise ValueError

                    setattr(cli, item["argument"], cmd_argument)

                cli.callback(ContextApplication())

    def load_genericcli(self):
        cli_list = self.generic_cli_list

        for cli in cli_list:
            methods = cli.get_methods()
            for method in methods:
                try:
                    if argv[1] == method["name"].lower().replace("_", " "):
                        # if argv[2] in ["-h", "--help"]:
                        #     cprint(method)
                        #     return
                        args = {}
                        arguments = method["args"][1:]
                        if len(argv[2:]) > len(arguments):
                            raise IncorrectCommandArgument(
                                argv[1], argv[len(argv) - 1])

                        for index, item in enumerate(arguments):
                            cmd_argument = argv[index + 2]

                            if cmd_argument.isnumeric():
                                cmd_argument = int(cmd_argument)

                            if type(cmd_argument) != item["type"]:
                                raise ValueError

                            args[item["argument"]] = cmd_argument

                        getattr(cli, method["name"])(
                            ctx=ContextApplication(), **args)

                except Exception as ex:
                    self.load_handlers(ex)
                    # raise ex

    def load_handlers(self, exception: Exception):
        error_handler = ErrorHandler()
        error_handler.trigger_handlers(self.handler_list, exception)
