"""
Getting data for home page
"""
import repo

def get_home_data(state):
    """
    Get home page data
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
