import repo

def get_home(state):
    """
    Get home page
    """
    home_data = {
        "readme": repo.get_readme(state),
        "databases": repo.list_sources(state),
    }
    return home_data
