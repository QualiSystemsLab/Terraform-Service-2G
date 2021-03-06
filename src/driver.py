from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
from data_model import *  # run 'shellfoundry generate' to generate data model classes
from subprocess import check_output
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext


class TerraformService2GDriver (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    def run_terraform(self, context):
        """
        :param ResourceCommandContext context:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        res_id = context.reservation.reservation_id

        api.WriteMessageToReservationOutput(res_id, "Running terraform with auto approve..")
        service_resource = TerraformService2G.create_from_context(context)
        tform_dir = service_resource.terraform_module_path
        tform_exe_dir = service_resource.terraform_executable
        tform_command = [f"{tform_exe_dir}\\terraform.exe", "apply", "-auto-approve", "-no-color"]
        outp = check_output(tform_command, cwd=tform_dir).decode("utf-8")

        return outp

    def plan_terraform(self, context):
        """
        :param ResourceCommandContext context:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        res_id = context.reservation.reservation_id

        api.WriteMessageToReservationOutput(res_id, "Generating terraform plan..")
        service_resource = TerraformService2G.create_from_context(context)
        tform_dir = service_resource.terraform_module_path
        tform_exe_dir = service_resource.terraform_executable
        tform_command = [f"{tform_exe_dir}\\terraform.exe", "plan", "-no-color"]
        outp = check_output(tform_command, cwd=tform_dir).decode("utf-8")

        return outp

    def destroy_terraform(self, context):
        """
        :param ResourceCommandContext context:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        res_id = context.reservation.reservation_id

        api.WriteMessageToReservationOutput(res_id, "Destroying terraform deployment..")
        service_resource = TerraformService2G.create_from_context(context)
        tform_dir = service_resource.terraform_module_path
        tform_exe_dir = service_resource.terraform_executable
        tform_command = [f"{tform_exe_dir}\\terraform.exe", "destroy", "-auto-approve", "-no-color"]
        outp = check_output(tform_command, cwd=tform_dir).decode("utf-8")

        return outp

    def show_terraform_state(self, context):
        """
        :param ResourceCommandContext context:
        :return:
        """
        api = CloudShellSessionContext(context).get_api()
        res_id = context.reservation.reservation_id

        api.WriteMessageToReservationOutput(res_id, "Getting current Terraform Deployment state..")
        service_resource = TerraformService2G.create_from_context(context)
        tform_dir = service_resource.terraform_module_path
        try:
            state_file = open(f"{tform_dir}\\terraform.tfstate", mode="r")
            outp = state_file.read()

            state_file.close()
        except:
            outp = "Could not retrieve deployment state."
        return outp
