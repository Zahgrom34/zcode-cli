from random import uniform
from time import sleep
from requests import get
from src.application import ContextApplication
from src.main import CLI, BaseCLI
from rich.progress import Progress

cli = CLI("Main CLI")


class DownloadData(BaseCLI):
    name: str
    link: str
    file: str

    def callback(self, ctx: ContextApplication):
        response = get(self.link)
        progress = Progress(console=ctx.console, transient=True)

        with progress:
            task = progress.add_task(f"Downloading from {self.link}")

            while not progress.finished:
                progress.update(task, advance=0.5)
                sleep(int(response.headers["Content-length"][0]) / 1000)

        open(self.file + f"/{self.name}", "wb").write(response.content)


if __name__ == "__main__":
    cli.register_command(DownloadData())
    cli.run()
