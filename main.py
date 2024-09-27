from gitlab_burndown.config import get_config
from gitlab_burndown.discovery import search_project_id_by_project_name


def main():
    """Main function to find and print the project ID."""
    project_id = search_project_id_by_project_name(
        get_config().GITLAB_PROJECT_NAME
    )
    print(f"Project ID: {project_id}")


if __name__ == "__main__":
    main()
