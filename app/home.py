import repo

def get_home(state):
    """
    Get home page
    """
    try:
        readme = repo.get_readme(state)
    except:
        readme = None
    home_data = {
        "readme": readme,
        "databases": repo.list_sources(state),
    }
    return home_data
