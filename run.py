import multiprocessing
import os

# Prevents Intel Fortran runtime (libifcoremd.dll / MKL bundled with numpy)
# from intercepting uvicorn's reload signal, causing
# "forrtl: error (200): program aborting due to control-C event".
os.environ["FOR_DISABLE_CONSOLE_CTRL_HANDLER"] = "1"

if __name__ == "__main__":
    multiprocessing.freeze_support()
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
