import requests
import json
import os
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your TestRail URL, username, and API key
base_url = 'https://your_testrail_instance.testrail.io'
username = 'your_email@example.com'  # Your TestRail email
api_key = 'your_api_key'
project_id = 2  # Your project ID

# Import configuration
import_config = {
    'milestones': True,
    'test_cases': True,
    'test_plans': False,
    'test_runs': False,
    'test_results': False,
    'reports': False,
    'users': False,
    'project_users': False,
    'templates': False,
    'suites': False,
    'case_statuses': False,
    'statuses': False,
    'shared_steps': False,
    'runs': False,
    'roles': False,
    'groups': False,
    'datasets': False,
    'configs': False,
    'case_types': False,
    'case_fields': False,
    'priorities': False,
    'project': False,
    'tests': False,
    'attachments_for_case': False,
    'attachments_for_plan': False,
    'attachments_for_run': False,
    'attachments_for_test': False
}

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

def get_data(endpoint):
    url = f'{base_url}/index.php?/api/v2/{endpoint}'
    try:
        response = requests.get(url, auth=(username, api_key))
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException for URL {url}: {e}")
    return None

def save_data(data, filename):
    if data is not None:
        file_path = os.path.join(script_dir, filename)
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            logging.info(f"Data saved to {filename}")
        except IOError as e:
            logging.error(f"IOError while saving {filename}: {e}")
    else:
        logging.warning(f"Skipping saving {filename} due to no data.")

def fetch_and_save(endpoint, filename):
    data = get_data(endpoint)
    save_data(data, filename)

def fetch_test_runs_from_plans(test_plans):
    test_runs = []
    if isinstance(test_plans, dict) and 'plans' in test_plans:
        for plan in test_plans['plans']:
            if isinstance(plan, dict) and 'id' in plan:
                plan_id = plan['id']
                plan_details = get_data(f'get_plan/{plan_id}')
                if plan_details:
                    for entry in plan_details.get('entries', []):
                        for run in entry.get('runs', []):
                            test_runs.append(run)
    else:
        logging.error("Test plans data is not in the expected format.")
    return test_runs

def fetch_and_save_test_results(test_runs):
    all_results = []
    for run in test_runs:
        if isinstance(run, dict) and 'id' in run:
            run_id = run['id']
            results = get_data(f'get_results_for_run/{run_id}')
            if results is not None:
                all_results.append({
                    'run_id': run_id,
                    'results': results
                })
    save_data(all_results, 'test_results.json')

def fetch_tests_with_pagination(run_id):
    tests = []
    offset = 0
    limit = 250
    while True:
        endpoint = f'get_tests/{run_id}&offset={offset}&limit={limit}'
        response = get_data(endpoint)
        if response and 'tests' in response:
            tests.extend(response['tests'])
            if len(response['tests']) < limit:
                break
            offset += limit
        else:
            break
    return tests

def fetch_and_save_tests_and_attachments(test_runs):
    for run in test_runs:
        if isinstance(run, dict) and 'id' in run:
            run_id = run['id']
            tests = fetch_tests_with_pagination(run_id)
            if tests:
                save_data(tests, f'tests_run_{run_id}.json')
                if import_config.get('test_results'):
                    all_results = []
                    for test in tests:
                        if isinstance(test, dict) and 'id' in test:
                            test_id = test['id']
                            results = get_data(f'get_results/{test_id}')
                            if results:
                                all_results.append({
                                    'test_id': test_id,
                                    'results': results
                                })
                    save_data(all_results, f'results_run_{run_id}.json')
                if import_config.get('attachments_for_test'):
                    for test in tests:
                        if isinstance(test, dict) and 'id' in test:
                            test_id = test['id']
                            attachments = get_data(f'get_attachments_for_test/{test_id}')
                            save_data(attachments, f'attachments_test_{test_id}.json')

def main():
    if import_config.get('milestones'):
        fetch_and_save(f'get_milestones/{project_id}&is_completed=0', 'milestones.json')

    if import_config.get('test_cases'):
        fetch_and_save(f'get_cases/{project_id}', 'test_cases.json')

    test_plans = None
    if import_config.get('test_plans'):
        test_plans = get_data(f'get_plans/{project_id}')
        save_data(test_plans, 'test_plans.json')

    test_runs = fetch_test_runs_from_plans(test_plans)

    if import_config.get('test_runs'):
        save_data({'runs': test_runs}, 'test_runs.json')

    if import_config.get('test_results'):
        fetch_and_save_test_results(test_runs)

    if import_config.get('reports'):
        fetch_and_save(f'get_reports/{project_id}', 'reports.json')

    if import_config.get('users'):
        fetch_and_save('get_users', 'users.json')

    if import_config.get('project_users'):
        fetch_and_save(f'get_users/{project_id}', 'project_users.json')

    if import_config.get('templates'):
        fetch_and_save(f'get_templates/{project_id}', 'templates.json')

    if import_config.get('suites'):
        fetch_and_save(f'get_suites/{project_id}', 'suites.json')

    if import_config.get('case_statuses'):
        fetch_and_save('get_case_statuses', 'case_statuses.json')

    if import_config.get('statuses'):
        fetch_and_save('get_statuses', 'statuses.json')

    if import_config.get('shared_steps'):
        fetch_and_save(f'get_shared_steps/{project_id}', 'shared_steps.json')

    if import_config.get('runs'):
        fetch_and_save(f'get_runs/{project_id}', 'runs.json')

    if import_config.get('roles'):
        fetch_and_save('get_roles', 'roles.json')

    if import_config.get('groups'):
        fetch_and_save('get_groups', 'groups.json')

    if import_config.get('datasets'):
        fetch_and_save(f'get_datasets/{project_id}', 'datasets.json')

    if import_config.get('configs'):
        fetch_and_save(f'get_configs/{project_id}', 'configs.json')

    if import_config.get('case_types'):
        fetch_and_save('get_case_types', 'case_types.json')

    if import_config.get('case_fields'):
        fetch_and_save('get_case_fields', 'case_fields.json')

    if import_config.get('priorities'):
        fetch_and_save('get_priorities', 'priorities.json')

    if import_config.get('project'):
        fetch_and_save(f'get_project/{project_id}', 'project.json')

    if import_config.get('tests'):
        fetch_and_save_tests_and_attachments(test_runs)

    if import_config.get('attachments_for_case'):
        cases = get_data(f'get_cases/{project_id}')
        if cases and 'cases' in cases:
            for case in cases['cases']:
                if isinstance(case, dict) and 'id' in case:
                    case_id = case['id']
                    attachments = get_data(f'get_attachments_for_case/{case_id}')
                    save_data(attachments, f'attachments_case_{case_id}.json')

    if import_config.get('attachments_for_plan') and test_plans:
        for plan in test_plans['plans']:
            if isinstance(plan, dict) and 'id' in plan:
                plan_id = plan['id']
                attachments = get_data(f'get_attachments_for_plan/{plan_id}')
                save_data(attachments, f'attachments_plan_{plan_id}.json')

    if import_config.get('attachments_for_run'):
        for run in test_runs:
            if isinstance(run, dict) and 'id' in run:
                run_id = run['id']
                attachments = get_data(f'get_attachments_for_run/{run_id}')
                save_data(attachments, f'attachments_run_{run_id}.json')

    logging.info("Export completed successfully.")

if __name__ == "__main__":
    main()