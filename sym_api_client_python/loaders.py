import logging
import os

from .auth.auth import Auth
from .auth.rsa_auth import SymBotRSAAuth
from .configure.configure import SymConfig


def load_from_env_var(env_var, delimiter=":"):
    """Look for an environment variable with the format:
        env_var=[RSA|CERT]:/path/to/config
    
    E.g. SYMPHONY_CONFIG=RSA:resources/config.json

    The env_var parameter describes which environment variable to check

    config.configure() and auth.authenticate() are called within this method so don't need to
    be called again

    Returns a tuple of configuration, auth
    """
    env_value = os.environ.get(env_var)
    if env_value is None:
        raise ValueError("Unable to find environment variable at: " + env_var)

    split = env_value.split(delimiter)

    if len(split) == 1:
        raise ValueError(f"Did not find {delimiter} in environment variable: {env_value}")
    elif len(split) > 2:
        # On windows you can have a colon in the path
        if len(split) == 3 and os.name == "nt":
            split = [split[0], split[1] + ":" + split[2]]
        else:
            raise ValueError(f"Found more than one {delimiter} in environment_variable: {env_value}") 
    
    
    if split[0].lower() not in ["rsa", "cert"]:
        raise ValueError(f"Didn't recognise f{split[0]}, expected one of: RSA, CERT")
    
    logging.debug(f"Loading config from {split[1]} with authentication mode: {split[0]}")

    conf = SymConfig(split[1], split[1])
    conf.load_config()

    if split[0].lower() == "rsa":
        auth = SymBotRSAAuth(conf)
    else:
        auth = Auth(conf)
    
    auth.authenticate()

    return conf, auth


def configure_logging(filename=None, directory=None, log_level=logging.DEBUG, format=None, filemode='a'):
    """Set up the loggers with basic defaults

        Set filename and directory to both be None to not save to file.

        filename: The filename to give to the logs. If this has paths as well they will be relative
                  to the directory. Defaults to log.log.
        directory: Directory to save the logs in. Defaults to a directory called "logs" adjacent
                   to the main. Put "." to make this current working directory. This will creat the
                   folder if it doesn't already exist.
        log_level: One of logging.levels
        format: Defaults to '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        filemode: How to open the logfile, 'w' rewrites, 'a' appends to existing
    """
    file_log = True
    if directory is None and filename is None:
        file_log = False

    if directory is None:
        # It's generally bad practice to import in functions, but in this instance
        # this import might fail (if it's loaded from a REPL etc) so it's probably
        # best to leave it until it's definitely needed.
        import __main__
        directory = os.path.dirname(__main__.__file__)
    elif directory == ".":
        directory = sys.curdir
    elif filename is None:
        filename = "log.log"
    
    if not file_log:
        full_path = None        
    else:
        full_path = os.path.join(directory, filename)
        # This has to be done again to handle the case where filename was relative
        full_dir = os.path.dirname(full_path)

        if not os.path.exists(full_dir):
            os.makedirs(full_dir, exist_ok=True)
            
    if format is None:
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(
            filename=full_path,
            format=format,
            filemode=filemode, level=log_level
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)
