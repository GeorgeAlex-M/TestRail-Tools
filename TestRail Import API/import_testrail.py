import requests
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your TestRail URL, username, and API key
base_url = 'https://your_testrail_instance.testrail.io'
username = 'your_email@example.com'  # Your TestRail email
api_key = 'your_api_key'
new_project_id = 2  # Your new project ID

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

# Function to post data to TestRail API
def post_data(endpoint, data):
    url = f'{base_url}/index.php?/api/v2/{endpoint}'
    logging.info(f"Posting to {url} with data: {json.dumps(data, indent=4)}")  # Debugging output
    response = requests.post(url, auth=(username, api_key), json=data)
    try:
        response.raise_for_status()  # Raise an error for bad status codes
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTPError for URL {url}: {e}")
        logging.error(f"Response content: {response.content}")  # Debugging output
        return None
    return response.json()

# Function to get data from TestRail API
def get_data(endpoint):
    url = f'{base_url}/index.php?/api/v2/{endpoint}'
    response = requests.get(url, auth=(username, api_key))
    try:
        response.raise_for_status()  # Raise an error for bad status codes
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTPError for URL {url}: {e}")
        logging.error(f"Response content: {response.content}")  # Debugging output
        return None
    return response.json()

# Function to load data from a JSON file
def load_data(filename):
    file_path = os.path.join(script_dir, filename)
    with open(file_path, 'r') as f:
        return json.load(f)

# Function to import milestones
def import_milestones():
    milestones_data = load_data('milestones.json')
    if 'milestones' in milestones_data:
        for milestone in milestones_data['milestones']:
            if isinstance(milestone, dict):
                milestone['project_id'] = new_project_id
                # Remove fields that are not required when creating a new milestone
                fields_to_remove = [
                    'id', 'started_on', 'is_started', 'completed_on', 'is_completed', 
                    'url', 'milestones'
                ]
                for field in fields_to_remove:
                    milestone.pop(field, None)
                
                # Post the milestone to the TestRail API
                response = post_data(f'add_milestone/{new_project_id}', milestone)
                if response:
                    logging.info(f"Successfully added milestone: {response['id']}")
                else:
                    logging.error(f"Failed to add milestone: {milestone['name']}")
            else:
                logging.warning(f"Unexpected milestone format: {milestone}")
    else:
        logging.error("No 'milestones' key found in the provided data.")

# Function to ensure the section exists or create it
def ensure_section_exists(section_id):
    # This function should check if the section exists and return its ID
    # If the section does not exist, it should create the section and return the new ID
    # For simplicity, we'll assume the section exists and return the provided section_id
    return section_id

# Function to import test cases
def import_test_cases():
    test_cases_data = load_data('test_cases.json')
    if 'cases' in test_cases_data:
        for test_case in test_cases_data['cases']:
            if isinstance(test_case, dict):
                section_id = test_case.pop('section_id', None)
                if section_id is None:
                    logging.warning(f"Skipping test case due to missing section_id: {test_case}")
                    continue
                
                # Ensure the section exists or create it
                new_section_id = ensure_section_exists(section_id)
                if new_section_id is None:
                    logging.warning(f"Skipping test case due to invalid section_id: {section_id}")
                    continue
                
                # Remove fields that are not required when creating a new test case
                fields_to_remove = [
                    'id', 'created_by', 'created_on', 'updated_by', 'updated_on', 
                    'suite_id', 'display_order', 'is_deleted', 'estimate_forecast', 'case_assignedto_id', 'comments'
                ]
                for field in fields_to_remove:
                    test_case.pop(field, None)
                
                # Post the test case to the TestRail API
                response = post_data(f'add_case/{new_section_id}', test_case)
                if response:
                    logging.info(f"Successfully added test case: {response['id']}")
                else:
                    logging.error(f"Failed to add test case: {test_case.get('title', 'Unknown')}")
            else:
                logging.warning(f"Unexpected test case format: {test_case}")
    else:
        logging.error("No 'cases' key found in the provided data.")

# Function to import test plans
def import_test_plans():
    test_plans_data = load_data('test_plans.json')
    for test_plan in test_plans_data:
        if isinstance(test_plan, dict):
            test_plan['project_id'] = new_project_id
            # Ensure milestone_id is valid
            if 'milestone_id' not in test_plan or not test_plan['milestone_id']:
                logging.warning(f"Skipping test plan due to missing or invalid milestone_id: {test_plan}")
                continue
            # Remove fields that are not required when creating a new test plan
            test_plan = {key: test_plan[key] for key in test_plan if key in ['name', 'description', 'milestone_id']}
            post_data(f'add_plan/{new_project_id}', test_plan)
        else:
            logging.warning(f"Unexpected test plan format: {test_plan}")

# Function to import test runs
def import_test_runs():
    test_runs_data = load_data('test_runs.json')
    for test_run in test_runs_data:
        if isinstance(test_run, dict):
            test_run['project_id'] = new_project_id
            if 'milestone_id' not in test_run or not test_run['milestone_id']:
                logging.warning(f"Skipping test run due to missing or invalid milestone_id: {test_run}")
                continue
            post_data(f'add_run/{new_project_id}', test_run)
        else:
            logging.warning(f"Unexpected test run format: {test_run}")

# Function to import test results
def import_test_results():
    test_results_data = load_data('test_results.json')
    for result in test_results_data:
        run_id = result.get('run_id')
        for test_result in result.get('results', []):
            if isinstance(test_result, dict):
                post_data(f'add_result_for_case/{run_id}/{test_result["case_id"]}', test_result)
            else:
                logging.warning(f"Unexpected test result format: {test_result}")

# Function to import reports
def import_reports():
    reports_data = load_data('reports.json')
    for report in reports_data:
        if isinstance(report, dict):
            report['project_id'] = new_project_id
            post_data(f'add_report/{new_project_id}', report)
        else:
            logging.warning(f"Unexpected report format: {report}")

# Function to import users
def import_users():
    users_data = load_data('users.json')
    for user in users_data:
        if isinstance(user, dict):
            response = post_data('add_user', user)
            if response is None and 'The Email Address is already in use by another user.' in response.content.decode():
                logging.warning(f"Skipping user {user['email']} as it already exists.")
        else:
            logging.warning(f"Unexpected user format: {user}")

# Function to import project users
def import_project_users():
    project_users_data = load_data('project_users.json')
    for user in project_users_data:
        if isinstance(user, dict):
            user['project_id'] = new_project_id
            post_data(f'add_user_to_project/{new_project_id}', user)
        else:
            logging.warning(f"Unexpected project user format: {user}")

# Function to import templates
def import_templates():
    templates_data = load_data('templates.json')
    for template in templates_data:
        if isinstance(template, dict):
                       post_data(f'add_template/{new_project_id}', template)
        else:
            logging.warning(f"Unexpected template format: {template}")

# Function to import suites
def import_suites():
    suites_data = load_data('suites.json')
    for suite in suites_data:
        if isinstance(suite, dict):
            suite['project_id'] = new_project_id
            post_data(f'add_suite/{new_project_id}', suite)
        else:
            logging.warning(f"Unexpected suite format: {suite}")

# Function to import case statuses
def import_case_statuses():
    case_statuses_data = load_data('case_statuses.json')
    for status in case_statuses_data:
        if isinstance(status, dict):
            post_data('add_case_status', status)
        else:
            logging.warning(f"Unexpected case status format: {status}")

# Function to import statuses
def import_statuses():
    statuses_data = load_data('statuses.json')
    for status in statuses_data:
        if isinstance(status, dict):
            post_data('add_status', status)
        else:
            logging.warning(f"Unexpected status format: {status}")

# Function to import shared steps
def import_shared_steps():
    shared_steps_data = load_data('shared_steps.json')
    for step in shared_steps_data:
        if isinstance(step, dict):
            post_data(f'add_shared_step/{new_project_id}', step)
        else:
            logging.warning(f"Unexpected shared step format: {step}")

# Function to import runs
def import_runs():
    runs_data = load_data('runs.json')
    for run in runs_data:
        if isinstance(run, dict):
            run['project_id'] = new_project_id
            post_data(f'add_run/{new_project_id}', run)
        else:
            logging.warning(f"Unexpected run format: {run}")

# Function to import roles
def import_roles():
    roles_data = load_data('roles.json')
    for role in roles_data:
        if isinstance(role, dict):
            post_data('add_role', role)
        else:
            logging.warning(f"Unexpected role format: {role}")

# Function to import groups
def import_groups():
    groups_data = load_data('groups.json')
    for group in groups_data:
        if isinstance(group, dict):
            post_data('add_group', group)
        else:
            logging.warning(f"Unexpected group format: {group}")

# Function to import datasets
def import_datasets():
    datasets_data = load_data('datasets.json')
    for dataset in datasets_data:
        if isinstance(dataset, dict):
            post_data(f'add_dataset/{new_project_id}', dataset)
        else:
            logging.warning(f"Unexpected dataset format: {dataset}")

# Function to import configs
def import_configs():
    configs_data = load_data('configs.json')
    for config in configs_data:
        if isinstance(config, dict):
            post_data(f'add_config/{new_project_id}', config)
        else:
            logging.warning(f"Unexpected config format: {config}")

# Function to import case types
def import_case_types():
    case_types_data = load_data('case_types.json')
    for case_type in case_types_data:
        if isinstance(case_type, dict):
            post_data('add_case_type', case_type)
        else:
            logging.warning(f"Unexpected case type format: {case_type}")

# Function to import case fields
def import_case_fields():
    case_fields_data = load_data('case_fields.json')
    for case_field in case_fields_data:
        if isinstance(case_field, dict):
            post_data('add_case_field', case_field)
        else:
            logging.warning(f"Unexpected case field format: {case_field}")

# Function to import priorities
def import_priorities():
    priorities_data = load_data('priorities.json')
    for priority in priorities_data:
        if isinstance(priority, dict):
            post_data('add_priority', priority)
        else:
            logging.warning(f"Unexpected priority format: {priority}")

# Function to import project
def import_project():
    project_data = load_data('project.json')
    if isinstance(project_data, dict):
        post_data('add_project', project_data)
    else:
        logging.warning(f"Unexpected project format: {project_data}")

# Function to import tests
def import_tests():
    tests_data = load_data('tests.json')
    for test in tests_data:
        if isinstance(test, dict):
            post_data(f'add_test/{new_project_id}', test)
        else:
            logging.warning(f"Unexpected test format: {test}")

# Function to import attachments for cases
def import_attachments_for_case():
    attachments_data = load_data('attachments_for_case.json')
    for attachment in attachments_data:
        if isinstance(attachment, dict):
            post_data(f'add_attachment_to_case/{attachment["case_id"]}', attachment)
        else:
            logging.warning(f"Unexpected attachment format: {attachment}")

# Function to import attachments for plans
def import_attachments_for_plan():
    attachments_data = load_data('attachments_for_plan.json')
    for attachment in attachments_data:
        if isinstance(attachment, dict):
            post_data(f'add_attachment_to_plan/{attachment["plan_id"]}', attachment)
        else:
            logging.warning(f"Unexpected attachment format: {attachment}")

# Function to import attachments for runs
def import_attachments_for_run():
    attachments_data = load_data('attachments_for_run.json')
    for attachment in attachments_data:
        if isinstance(attachment, dict):
            post_data(f'add_attachment_to_run/{attachment["run_id"]}', attachment)
        else:
            logging.warning(f"Unexpected attachment format: {attachment}")

# Function to import attachments for tests
def import_attachments_for_test():
    attachments_data = load_data('attachments_for_test.json')
    for attachment in attachments_data:
        if isinstance(attachment, dict):
            post_data(f'add_attachment_to_test/{attachment["test_id"]}', attachment)
        else:
            logging.warning(f"Unexpected attachment format: {attachment}")

# Main function to handle the import process
def main():
    if import_config['milestones']:
        import_milestones()
    if import_config['test_cases']:
        import_test_cases()
    if import_config['test_plans']:
        import_test_plans()
    if import_config['test_runs']:
        import_test_runs()
    if import_config['test_results']:
        import_test_results()
    if import_config['reports']:
        import_reports()
    if import_config['users']:
        import_users()
    if import_config['project_users']:
        import_project_users()
    if import_config['templates']:
        import_templates()
    if import_config['suites']:
        import_suites()
    if import_config['case_statuses']:
        import_case_statuses()
    if import_config['statuses']:
        import_statuses()
    if import_config['shared_steps']:
        import_shared_steps()
    if import_config['runs']:
        import_runs()
    if import_config['roles']:
        import_roles()
    if import_config['groups']:
        import_groups()
    if import_config['datasets']:
        import_datasets()
    if import_config['configs']:
        import_configs()
    if import_config['case_types']:
        import_case_types()
    if import_config['case_fields']:
        import_case_fields()
    if import_config['priorities']:
        import_priorities()
    if import_config['project']:
        import_project()
    if import_config['tests']:
        import_tests()
    if import_config['attachments_for_case']:
        import_attachments_for_case()
    if import_config['attachments_for_plan']:
        import_attachments_for_plan()
    if import_config['attachments_for_run']:
        import_attachments_for_run()
    if import_config['attachments_for_test']:
        import_attachments_for_test()

if __name__ == '__main__':
    main()