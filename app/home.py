import utils

def get_home():
    """
    Get home page
    """
    home_data = {
        "readme": utils.get_readme(),
        "databases": utils.list_sources(),
    }
    return home_data
