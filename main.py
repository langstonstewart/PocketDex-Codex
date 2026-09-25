from src import app

codex = app.Application(disable_dex_images=False)

if __name__ == "__main__":
    codex.run() # type: ignore

