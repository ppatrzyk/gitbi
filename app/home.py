import repo

def get_home():
    """
    Get home page
    """
    home_data = {
        "readme": repo.get_readme(),
        "databases": repo.list_sources(),
    }
    return home_data
