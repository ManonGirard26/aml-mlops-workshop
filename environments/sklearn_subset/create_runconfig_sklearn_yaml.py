from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import RunConfiguration
from azureml.core import Workspace, Run
from azureml.core.authentication import AzureCliAuthentication
from azureml.core.dataset import Dataset
import os
from azureml.exceptions._azureml_exception import UserErrorException
from azureml.core.runconfig import (Data,
                                    DataLocation,
                                    Dataset as RunDataset)

run = Run.get_context()


def load_data(dataset, input_name):
    data = Data(
        data_location=DataLocation(
            dataset=RunDataset(dataset_id=dataset.id)),
        create_output_directories=False,
        mechanism='mount',
        environment_variable_name=input_name,
        overwrite=True
        )
    return data


# Retrieve a datastore from a ML workspace
try:
    workspace = Workspace.from_config(auth=AzureCliAuthentication())
except UserErrorException:
    workspace = run.experiment.workspace

# Define the conda dependencies
cd = CondaDependencies(
    conda_dependencies_file_path=os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'conda_dependencies_sklearn.yml'
    )
)

# define compute
compute_target = 'alwaysoncluster'

# define data set names
input_name_train = 'newsgroups_subset_train'
input_name_test = 'newsgroups_subset_test'

# Retrieve datsets
dataset_train = Dataset.get_by_name(workspace, name=input_name_train)
dataset_test = Dataset.get_by_name(workspace, name=input_name_test)

# Runconfig
amlcompute_run_config = RunConfiguration(
    script="train.py",
    conda_dependencies=cd,
    framework='Python',
)

amlcompute_run_config.environment.docker.enabled = True
amlcompute_run_config.environment.spark.precache_packages = False
amlcompute_run_config.target = compute_target
amlcompute_run_config.data = {input_name_train: load_data(dataset_train,
                                                          input_name_train),
                              input_name_test: load_data(dataset_test,
                                                         input_name_test)}

amlcompute_run_config.save(path=os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "RunConfig/",
        "runconfig_subset.yml",
    ), name='sklearn', separate_environment_yaml=True)
