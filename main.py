from src import modulemanager


if modulemanager.ModuleManager().module_check():
    from src import app

    codex = app.Application()

    if __name__ == "__main__":
        codex.run()

