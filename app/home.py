"""
Getting data for home page
"""
import repo
from markdown import markdown

def get_home_data(state):
    """
    Get home page data
    """
    try:
        readme = repo.get_readme(state)
        readme = markdown(readme)
    except:
        readme = None
    databases = {db: sorted(tuple(queries)) for db, queries in repo.list_sources(state).items()}
    home_data = {
        "readme": readme,
        "databases": databases,
    }
    return home_data
