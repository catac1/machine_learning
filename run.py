import multiprocessing
import os

# Prevents Intel Fortran runtime (libifcoremd.dll / MKL bundled with numpy)
# from intercepting CTRL+C/SIGTERM during uvicorn reload, which causes
# "forrtl: error (200): program aborting due to control-C event".
os.environ["FOR_DISABLE_CONSOLE_CTRL_HANDLER"] = "1"

# Prevent joblib/loky from spawning a process pool that conflicts with
# uvicorn's --reload worker process lifecycle on Windows.
os.environ["LOKY_MAX_CPU_COUNT"] = "1"
os.environ["JOBLIB_MULTIPROCESSING"] = "0"

if __name__ == "__main__":
    multiprocessing.freeze_support()
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        reload_delay=1.0,
    )
