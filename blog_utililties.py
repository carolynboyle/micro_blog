from os import environ
from dotenv import load_dotenv
from faker import Faker

def get_env(env_file:str, env_value:str):
    """
    Load environment variables from a .env file.
    parms: 
        env_file: Path to the .env file.
        env_value: The name of the environment variable to retrieve.
    returns:
        The value of the specified environment variable.        
        2025-AUG-06 cfboyle004@sdccd.edu
        first version

    """
    try:
        load_dotenv(environ)
        return environ['database_name']
    except:
        print(f"An error has occurred retrieving the environment variable {env_value} from {env_file}.  Please check the file and try again.")


if __name__ == "__main__":
   print(f"Database Name: {get_env('.env', 'database_name')}")
   fake = Faker()